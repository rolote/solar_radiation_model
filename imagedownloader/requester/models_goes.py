from requester.models import *
from requester.worker_manager import *
from django.utils import timezone
from django.conf import settings
import re
import imaplib
import email
from ftplib import FTP, error_perm, error_temp
import sys
from libs.console import *
import os

class IMAPNotificationChecker(Job):
	def __init__(self, server):
		super(IMAPNotificationChecker, self).__init__(5)
		self._server = server
	def __del__(self):
		self.disconnect()
	def connect(self):
		self._connection = imaplib.IMAP4_SSL(str(self._server.hostname), self._server.port)
		self._connection.login(self._server.username, self._server.password)
	def disconnect(self):
		try:
			self._connection.close()
		except Exception as e:
			print_exception()
		self._connection.logout()
	def extract_body(self,payload):
		if isinstance(payload,str):
			return payload
		else:
			return '\n'.join([extract_body(part.get_payload()) for part in payload])
	def get_selection(self, selection, lines):
		for l in lines:
			result = re.search(selection, l)
			if result:
				return result.group(1)
	def get_hostname(self, lines):
		return self.get_selection('^ *ftp ([^ ]*)', lines)
	def get_user(self, lines):
		return self.get_selection('^ *([^ ]*) *\- FTP user id', lines)
	def get_passwd(self, lines):
		return self.get_selection('^ *([^ ]*) *\- FTP password', lines)
	def get_path(self, lines):
		return self.get_selection('^ *cd ([^ \t]*)', lines)
	def get_files(self,lines):
		path = self.get_path(lines)
		pattern = '\t*get ([^ ]*)'
		return [ path + "/" + (re.search(pattern,l).group(1)) for l in lines if re.search(pattern,l) ]
	def scrap_body(self, payload):
		body = self.extract_body(payload)
		lines = body.split("\r\n")
		host = self.get_hostname(lines)
		user = self.get_user(lines)
		passwd = self.get_passwd(lines)
		files = self.get_files(lines)
		return host, user, passwd, files
	def notifications(self):
		self._connection.select('data-notification')
		typ, data = self._connection.search(None, 'UNSEEN')
		notifications = []
		try:
			for num in data[0].split():
				typ, msg_data = self._connection.fetch(num, '(RFC822)')
				for response_part in msg_data:
					if isinstance(response_part, tuple):
						msg = email.message_from_string(response_part[1])
						subject=msg['subject']
						result = re.search('CLASS Order (\w+) Processing Complete', subject)
						if result:
							payload=msg.get_payload()
							scraped_data=self.scrap_body(payload)
							order_id = result.group(1)
							notifications.append((order_id, scraped_data))
				typ, response = self._connection.store(num, '+FLAGS', r'(\Seen)')
		finally:
			pass
		return notifications
	def create_new_orders(self):
		self.connect()
		notifications = self.notifications()
		for n in notifications:
			order, created_order = Order.objects.get_or_create(identification=n[0])
			if len(order.file_set.all()) == 0:
				service, created_service = FTPServerAccount.objects.get_or_create(hostname=n[1][0],username=n[1][1])
				service.password = n[1][2]
				service.save()
				order.server = service
				order.save()
				for filename in n[1][3]:
					f = File(remotename=filename,downloaded=False,size=0,localname='')
					f.order = order
					f.save()
		self.disconnect()
	def run(self,background):
		print 'Checking mail... (' + str(self._server) + ')'
		try:
			self.create_new_orders()
		except Exception as e:
			print 'Error ', e
			print_exception()
		print 'Finish checking mail... (' + str(self._server) + ')'
		background.wait('IMAPNotificationChecker'+str(self._server), 5*60)
		background.put_job(self)


class FTPFileDownloader(Job):
	def __init__(self, file_identification):
		super(FTPFileDownloader,self).__init__(10)
		self._file_id = file_identification
		self.size = 0
		self.stalled_times = 0
	def __del__(self):
		self.disconnect()
	def get_file_object(self):
		return File.objects.get(pk=self._file_id)
	def connect(self):
		service = (self.get_file_object()).order.server
		if not service is None:
			self._ftp = FTP(host=service.hostname, user=service.username, passwd=service.password)
	def disconnect(self):
		if hasattr(self, '_ftp'):
			if not self._ftp.sock is None:
				try:
					self._ftp.quit()
				except error_temp:
					self._ftp = None
	def get_size(self):
		return self._ftp.size((self.get_file_object()).remotename) if hasattr(self, '_ftp') else 0
	def get_localname(self):
		filename = ((self.get_file_object()).remotename.split("/"))[-1]
		year = filename.split(".")[1]
		return year + "/" + filename
	def ensure_dir(self, completepath):
		d = os.path.dirname(completepath)
		if not os.path.exists(d):
			os.makedirs(d)
	def download(self):
		file = self.get_file_object()
		try:
			file.size = self.get_size()
			file.localname = self.get_localname()
			completepath = file.completepath()
			if os.path.exists(completepath):
				size = (os.stat(completepath)).st_size
			else:
				size = 0
			if size < file.size:
				print 'Downloading '+ file.localname +'...'
				self.ensure_dir(completepath)
				file.begin_download = timezone.now()
				file.save()
				self._ftp.retrbinary('RETR ' + file.remotename, open(completepath, 'wb').write)
				file.end_download = timezone.now()
			file.failures = 0
			file.downloaded = True
		except error_perm as e:
			show(file.localname.ljust(60) + '[DONT EXISTS]')
			show(str(e) + '\n')
			file.failures += 1
		except Exception as e:
			show(file.localname.ljust(60) + '[FAIL]')
			show(str(e) + '\n')
			file.size = 0
			file.localname = ''
			print_exception()
		file.save()
	def run(self,background):
		self.connect()
		self.download()
		self.disconnect()

class GOESRequest(Request,Job):
	erase6 = '\b\b\b\b\b\b'
	erase8 = '\b\b\b\b\b\b\b\b'
	erase10 ='\b\b\b\b\b\b\b\b\b\b'
	def do_login(self, browser, server):
		login_button = browser.find_link_by_partial_text('Login')
		print login_button
		if login_button:
			login_button.click()
		# At the login page
		if len(browser.find_by_name('j_username')) > 0:
			browser.fill('j_username', server.username)
			browser.fill('j_password', server.password)
			browser.find_by_value('Login').click()
	def do_select_area(self, browser, area):
		browser.find_by_name('nlat').type(self.erase6 + str(area.north_latitude))
		browser.find_by_name('slat').type(self.erase6 + str(area.south_latitude))
		browser.find_by_name('elon').type(self.erase6 + str(area.east_longitude))
		browser.find_by_name('wlon').type(self.erase6 + str(area.west_longitude))
	def do_select_timerange(self, browser, timerange):
		begin, end = min(timerange), max(timerange)
		browser.find_by_name('start_date').type(self.erase10 + begin.date().isoformat())
		browser.find_by_name('end_date').type(self.erase10 + end.date().isoformat())
		browser.find_by_name('start_time').type(self.erase8 + begin.time().isoformat())
		browser.find_by_name('end_time').type(self.erase8 + end.time().isoformat())	
	def do_selection(self, browser):
		# Select service GVAR_IMG
		form = browser.find_by_name('search')
		browser.select('datatype_family', 'GVAR_IMG')
		(form.find_by_name('submit')).click()
		# Fill the form to crop and filter the images
		self.do_select_area(browser, self.get_area())
		self.do_select_timerange(browser, self.get_timerange())
		(browser.find_by_value('SH')).check() # South Hemisphere
		(browser.find_by_value('R')).check()  # Routine
		browser.select('Satellite', self.get_satellite().identification)
		((browser.find_by_name('search_frm')).find_by_value('Search')).click()
		# Select all the images of the day or mark as empty order
		have_items_to_download = len((browser.find_by_name('rform')).find_by_css('td.searchresults_table_td')) > 0
		if not have_items_to_download:
			order = self.get_order()
			order.empty_flag = True
			order.update_downloaded()
		else:
			((browser.find_by_name('rform')).find_by_value('SelectAll')).click()
			((browser.find_by_name('rform')).find_by_value('Goto Cart')).click()
			# Select the format, all the channels, tells the email
			browser.select('format_top_GVAR_IMG', 'NetCDF')
			chs = browser.find_by_name('channels_top_GVAR_IMG')
			for ch in self.get_channels():
				chs.find_by_value(ch.name).check()
			browser.fill('email', self.get_email_server().username)
			(browser.find_by_name('cocoon-action')).click()
		return have_items_to_download
	def do_register_order(self, browser):
		# Create the associated Order
		order = self.get_order()
		regex = re.search('Your confirmation number is:\n *([^ ]*).\n', browser.html)
		#re. Your confirmation number is: 122929754. 
		order.identification = '<empty>' if regex is None else str(regex.groups(0)[0])
		order.save()
	def do_survey(self, browser):
		form = browser.find_by_name('FORM1')
		form.find_by_value('education').check()
		(form.find_by_name('postSurvey')).click()
	def run(self,background):
		browser = background.browser_mgr.obtain(background)
		server = self.get_request_server()
		browser.visit(server.url)
		self.do_login(browser,server)
		if self.do_selection(browser):
			self.do_register_order(browser)
			self.do_survey(browser)
		background.browser_mgr.release(background)

class QOSRequester(Job):
	def __init__(self, automatic_download):
		super(QOSRequester, self).__init__(2)
		self._automatic = automatic_download
		self._jobs = []
		self._file_downloader = {}
	def put_job(self, job,background):
		self._jobs.append(job)
		background.put_job(job)
	def full_of_orders(self):
		incomming = len(self._automatic.pending_orders()) + len(self._jobs)
		is_full = incomming >= self._automatic.max_simultaneous_request
		print len(self._jobs), incomming, self._automatic.max_simultaneous_request
		return is_full
	def can_proceed(self,begin_0=None,end_0=None):
		t_begin, t_end = self._automatic.get_next_request_range(end_0=end_0)
		begin = min(t_begin, t_end)
		end = max(t_begin, t_end)
		time_range = self._automatic.time_range
		range_begin = min(time_range.begin, time_range.end)
		range_end = max(time_range.begin, time_range.end)
		inside_range = begin >= range_begin and end <= range_end
		now = timezone.now()
		have_orders_to_download = inside_range and begin < now and end < now and begin != end
		should_proceed = (not self._automatic.paused) and have_orders_to_download and (not self.full_of_orders())
		return should_proceed, t_begin, t_end
	def replace_aged(self, background):
		for request in self._automatic.request_set.filter(aged=True):
			print "\033[34;1mReplacing the old GOESRequest...\033[0m"
			req = GOESRequest(automatic_download=self._automatic, begin=request.begin, end=request.end)
			self.put_job(req,background)
			request.delete()
	def update_pending(self,background):
		self.replace_aged(background)
		should_create, begin, end = self.can_proceed()
		# Make many requests at once (taking care of the pending_orders and the jobs).
		while should_create:
			print "\033[34;1mAdding to the queue a new GOESRequest...\033[0m"
			req = GOESRequest(automatic_download=self._automatic, begin=begin, end=end)
			self.put_job(req,background) # , priority=7))
			should_create, begin, end = self.can_proceed(end_0=end)
	def run(self,background):
		self._jobs = [ job for job in self._jobs if not job.ready ]
		self.update_pending(background)
		background.wait('QOSRequester'+str(self._automatic.title), 2*60)
		background.put_job(self)

class QOSManager:
	class QOSManager__impl(Job):
		def __init__(self):
			self._priority = 1
			self._requesters = {}
			self._checkers = {}
			self._downloading = {}
		def get_requester(self, ad):
			if not ad in self._requesters:
				self._requesters[ad] = QOSRequester(ad)
			return self._requesters[ad]
		def get_checker(self, server):
			if not server in self._checkers:
				self._checkers[server] = IMAPNotificationChecker(server)
			return self._checkers[server]
		def get_downloader(self, file_object):
			if not file_object.id in self._downloading:
				self._downloading[file_object.id] = FTPFileDownloader(file_object.id)
			return self._downloading[file_object.id]
		def initialize_new_requester(self,background):
			print "Checking new automatic downloads..."
			news = [ self.get_requester(ad) for ad in AutomaticDownload.objects.all() if not ad in self._requesters ]
			for requester in news:
				background.put_job(requester)
			print "Finish checking new automatic downloads..."
		def initialize_new_checker(self,background):
			print "Checking new mail servers..."
			news = [ self.get_checker(s) for s in EmailAccount.objects.all() if not s in self._checkers ]
			for server in news:
				background.put_job(server)
			print "Finish checking new mail servers..."
		def initialize_new_files(self,background):
			print "Checking pending files..."
			for f in File.objects.filter(downloaded=True):
				f.verify_copy_status()
			news = [ self.get_downloader(f) for f in File.objects.filter(downloaded=False) if not f.id in self._downloading ]
			for o in Order.objects.all():
				o.update_downloaded()
			for downloader in news:
				background.put_job(downloader)
			print "Finish checking pending files..."
		def attend_stalled_file(self, f, background):
			dm = self._downloading[f.id]
			newsize = f.localsize()
			if not dm.size == newsize:
				dm.size = newsize
				dm.stalled_times = 0
			else:
				dm.stalled_times += 1
				if dm.stalled_times == 3:
					print 'Detected stalled file (' + f.filename() + ')...'
					dm.disconnect()
					background.put_job(dm)
		def mark_order_as_stalled(self, f):
			self._downloading[f.id] = None
			f.order.request.aged = True
			f.order.request.save()
		def check_stalled_files_or_requests(self,background):
			# TODO: In some point this process mark as unloaded some files that allready has been downloaded.
			for f in self._downloading:
				file_object = File.objects.get(pk=f)
				if file_object.failures <= 0:
					self.attend_stalled_file(file_object, background)
				else:
					show(file_object.failures, ' failures.')
					self.mark_order_as_stalled(file_object)
		def run(self, background):
			self.initialize_new_files(background)
			self.initialize_new_checker(background)
			self.initialize_new_requester(background)
			self.check_stalled_files_or_requests(background)
			background.wait('QOSManager', 7*60)
			background.put_job(self)

	__instance = None
	def __init__(self):
		if QOSManager.__instance is None:
			QOSManager.__instance = QOSManager.QOSManager__impl()
		self.__dict__['_QOSManager__instance'] = QOSManager.__instance
	def __getattr__(self, attr):
		return getattr(self.__instance, attr)
	def __setattr__(self, attr, value):
		return setattr(self.__instance, attr, value)
