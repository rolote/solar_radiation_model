from django.db import models
from datetime import datetime, timedelta
import pytz  # 3rd party
import os
from django.db.models import Min, Max, Avg, Count
from decimal import Decimal
from netCDF4 import Dataset

# Create your models here.

class Area(models.Model):
	name = models.TextField()
	north_latitude = models.DecimalField(max_digits=4,decimal_places=2)
	south_latitude = models.DecimalField(max_digits=4,decimal_places=2)
	east_longitude = models.DecimalField(max_digits=5,decimal_places=2)
	west_longitude = models.DecimalField(max_digits=5,decimal_places=2)
	hourly_longitude = models.DecimalField(max_digits=5, decimal_places=2, default=Decimal('0.00'))
	created = models.DateTimeField(auto_now_add=True)
	modified = models.DateTimeField(auto_now=True)
	def __str__(self):
		return self.name
	def getlongitude(self,datetime=datetime.now()):
		return self.hourly_longitude

class UTCTimeRange(models.Model):
	begin = models.DateTimeField()
	end = models.DateTimeField()
	created = models.DateTimeField(auto_now_add=True)
	modified = models.DateTimeField(auto_now=True)
	def __str__(self):
		return str(self.begin) + ' -> ' + str(self.end)
	def step(self):
		begin = datetime.utcnow() if self.begin is None else self.begin
		end = datetime.utcnow() if self.end is None else self.end
		diff = (end - begin).total_seconds()
		return timedelta(days=(diff / abs(diff)))
	def steps(self):
		return int((self.end - self.begin).total_seconds() / (self.step().total_seconds()))
	def contains(self, datetime):
		timezoned = timezone.make_aware(datetime, timezone.get_default_timezone())
		return self.begin <= timezoned and self.end >= timezoned

class Account(models.Model):
	password = models.TextField()
	created = models.DateTimeField(auto_now_add=True)
	modified = models.DateTimeField(auto_now=True)

class EmailAccount(Account):
	hostname = models.TextField()
	port = models.IntegerField()
	username = models.EmailField()
	def __str__(self):
		return self.username

class ServerAccount(Account):
	username = models.TextField()

class WebServerAccount(ServerAccount):
	url = models.TextField()
	def __str__(self):
		return self.username + '@' + self.url

class FTPServerAccount(ServerAccount):
	hostname = models.TextField()
	def __str__(self):
		return self.username + '@' + self.hostname

class Satellite(models.Model):
	name = models.TextField()
	identification = models.TextField()
	in_file = models.TextField()
	request_server = models.ForeignKey(WebServerAccount)
	created = models.DateTimeField(auto_now_add=True)
	modified = models.DateTimeField(auto_now=True)
	def __str__(self):
		return self.name

class Channel(models.Model):
	name = models.TextField(db_index=True)
	in_file = models.TextField(db_index=True,null=True)
	satellite = models.ForeignKey(Satellite)
	created = models.DateTimeField(auto_now_add=True)
	modified = models.DateTimeField(auto_now=True)
	def __str__(self):
		return self.name + ' ('+ str(self.satellite) + ')'

class AutomaticDownload(models.Model):
	title = models.TextField(db_index=True)
	area = models.ForeignKey(Area)
	time_range = models.ForeignKey(UTCTimeRange,db_index=True)
	paused = models.BooleanField()
	max_simultaneous_request = models.IntegerField()
	channels = models.ManyToManyField(Channel)
	email_server = models.ForeignKey(EmailAccount)
	root_path = models.TextField()
	created = models.DateTimeField(auto_now_add=True)
	modified = models.DateTimeField(auto_now=True)
	def __str__(self):
		return self.title
	def pending_requests(self):
		posible_pending = [ r for r in self.request_set.all() if not r.order.downloaded ]
		return [ r for r in posible_pending if r.order.update_downloaded() and not r.order.downloaded ]
	def pending_orders(self):
		return [ r.order for r in self.pending_requests() ]
	def step(self):
		return self.time_range.step()
	def get_next_request_range(self, begin_0=None, end_0=None):
		begins = [ r.end for r in self.request_set.all() ]
		begins.append(self.time_range.begin)
		if not end_0 is None:
			begins.append(end_0)
		if self.step().total_seconds() >= 0:
			f = max
		else:
			f = min
		begin = f(begins)
		end = begin + self.step()
		return begin, end
	def progress(self):
		return str(self.request_set.all().count()) + '/' + str(self.time_range.steps())
	def total_time(self):
		deltas = [ request.total_time() for request in self.request_set.all() ]
		total = None
		for d in deltas:
			total = d if not total else total + d
		return total
	def average_time(self):
		amount = self.request_set.all().count()
		return amount if amount == 0 else (self.total_time() / amount)
	def estimated_time(self):
		return self.average_time() * self.time_range.steps()


class Request(models.Model):
	automatic_download = models.ForeignKey(AutomaticDownload,db_index=True)
	begin = models.DateTimeField(db_index=True)
	end = models.DateTimeField(db_index=True)
	created = models.DateTimeField(auto_now_add=True)
	modified = models.DateTimeField(auto_now=True)
	aged = models.BooleanField(default=False)
	def __str__(self):
		return str(self.begin) + '->' + str(self.end) + ' (' + self.order.identification + ')'
	def get_channels(self):
		return self.automatic_download.channels.all()
	def get_satellite(self):
		return self.get_channels()[0].satellite
	def get_request_server(self):
		# For each request one server is used (the same satellite is shared by all the channels)
		return self.get_satellite().request_server
	def get_area(self):
		return self.automatic_download.area
	def get_email_server(self):
		return self.automatic_download.email_server
	def get_timerange(self):
		return (self.begin, self.end)
	def get_order(self):
		orders = Order.objects.filter(request=self)
		if len(orders) == 0:
			self.save()
			order = Order()
			order.request = self
			order.identification = ''
			order.save()
		else:
			order = orders[0]
		return order
	def identification(self):
		return self.get_order().identification
	def progress(self):
		return self.order.progress()
	def downloaded_porcentage(self):
		return self.order.downloaded_porcentage()
	def total_time(self):
		return self.order.total_time()

class Order(models.Model):
	request = models.OneToOneField(Request,db_index=True)
	server = models.ForeignKey(FTPServerAccount, null=True)
	identification = models.TextField(db_index=True)
	downloaded = models.BooleanField()
	empty_flag = models.BooleanField()
	created = models.DateTimeField(auto_now_add=True)
	modified = models.DateTimeField(auto_now=True)
	def __str__(self):
		return self.identification
	def pending_files(self):
		return self.file_set.filter(downloaded=False)
	def update_downloaded(self):
		self.downloaded = True if self.empty_flag else (len(self.file_set.all()) > 0 and len(self.pending_files()) == 0)
		self.save()
		return True
	def progress(self):
		return str(self.file_set.filter(downloaded=True).count())+'/'+str(self.file_set.all().count())
	def downloaded_porcentage(self):
		files = self.file_set.all().count()
		ratio = 0. if files == 0 else (self.file_set.filter(downloaded=True).count() / float(self.file_set.all().count()))
		ratio = 1. if self.empty_flag else ratio
		return '%.2f' % (ratio * 100.)
	def total_time(self):
		result = self.file_set.filter(downloaded=True).aggregate(Min('begin_download'), Max('end_download'))
		if result['begin_download__min'] is None:
			result['begin_download__min'] = datetime.utcnow()
		if result['end_download__max'] is None:
			result['end_download__max'] = datetime.utcnow()
		return result['end_download__max'] - result['begin_download__min']
	def average_speed(self):
		if not self.downloaded:
			speeds = [ float(f.download_speed()) for f in self.file_set.filter(begin_download__isnull = False)]
			avg = (sum(speeds) / len(speeds)) if len(speeds) > 0 else 0
		else:
			avg = 0
		return '%.2f' % (avg * 8)
	def download_speed(self):
		if not self.downloaded:
			speeds = [ float(f.download_speed()) for f in self.file_set.filter(begin_download__isnull = False, end_download__isnull = True)]
			avg = (sum(speeds) / len(speeds)) if len(speeds) > 0 else 0
		else:
			avg = 0
		return '%.2f' % (avg * 8)
	def year(self):
		return self.request.get_timerange()[0].year
	def julian_day(self):
		return min(self.request.get_timerange()[0].timetuple()[7],self.request.get_timerange()[1].timetuple()[7])

class File(models.Model):
	order = models.ForeignKey(Order, db_index=True, null=True)
	localname = models.TextField()
	remotename = models.TextField(null=True)
	size = models.IntegerField(null=True)
	downloaded = models.BooleanField(db_index=True)
	begin_download = models.DateTimeField(null=True,db_index=True)
	end_download = models.DateTimeField(null=True,db_index=True)
	failures = models.IntegerField(default=0)
	created = models.DateTimeField(auto_now_add=True)
	modified = models.DateTimeField(auto_now=True)
	def channel(self):
		res = re.search('BAND_([0-9]*)\.', self.completepath())
		return str(res.groups(0)[0]) if res else 'meta'
	def satellite(self):
		res = self.filename().split(".")
		return str(res[0])
	def image_datetime(self):
		t_info = self.filename().split(".")
		year = int(t_info[1])
		days = int(t_info[2])
		time = t_info[3]
		date = datetime(year, 1, 1) + timedelta(days - 1)
		return date.replace(hour=int(time[0:2]), minute=int(time[2:4]), second=int(time[4:6]))
	def image_satellite(self):
		sats = Satellite.objects.find(in_file = self.satellite())
		return sats[0] if len(sats) > 0 else None
	def image_channel(self):
		sat = self.image_satellite()
		chs = sat.channel_set.find(in_file=self.channel())
		return chs[0] if len(chs) > 0 else None
	def image_latlon(self):
		if self.channel() == 'meta':
			return None
		root = Dataset(self.completepath(),'r')
		lat = root.variables['lat'][:]
		lon = root.variables['lon'][:]
		root.close()
		return lat, lon
	def filename(self):
		return self.remotename.split("/")[-1]
	def completepath(self):
		root = self.order.request.automatic_download.root_path if self.order else '.'
		return os.path.expanduser(os.path.normpath(root + '/' + self.localname))
	def localsize(self):
		path = self.completepath()
		return os.stat(path).st_size if os.path.isfile(path) else 0
	def downloaded_porcentage(self):
		return '%.2f' % (0 if self.size == 0 else ((float(self.localsize()) / self.size) * 100.))
	def progress(self):
		return str(self.localsize()) + '/' + str(self.size)
	def download_speed(self):
		now = datetime.utcnow()
		now = now.replace(tzinfo=pytz.utc)
		begin = now if self.begin_download is None else self.begin_download
		last = now if self.end_download is None else self.end_download
		speed_in_bytes = self.localsize() / (last - begin).total_seconds() if last != begin else 0
		return '%.2f' % (speed_in_bytes / 1024.)
	def __gt__(self, obj):
		return self.image_datetime() > obj.image_datetime()
	def verify_copy_status(self):
		if self.size is None:
			self.size = 0
		if self.localsize() != self.size or self.size == 0 or self.localsize() == 0:
			self.downloaded = False
			self.end_download = None
			self.begin_download = None
			self.save()
			self.order.downloaded = False
			self.order.save()

from requester.models_goes import *
