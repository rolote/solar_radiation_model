from django.db import models
from requester.models import *
from process import Process
from libs.file import netcdf as nc
import calendar
import numpy as np
import collections
from libs import matrix

class Compact(Process):
	class Meta:
        	app_label = 'plumbing'
	extension = models.TextField()
	def do(self, data):
		results = {}
		for filename in data:
			print filename, len(data[filename])
			f = self.do_file(filename,data[filename])
			results[filename] = [ f ]
		return results
	def do_file(self, filename, data):
		print "Creating ", filename
		# create compact file and initialize basic settings
		root, is_new = nc.open(filename + self.extension) # The filename does not contain the extension
		if is_new:
			sample, n = nc.open(data[(data.keys())[0].completepath()])
			shape = sample.variables['data'].shape
			nc.getdim(root,'northing', shape[1])
			nc.getdim(root,'easting', shape[2])
			nc.getdim(root,'timing')
			v_lat = nc.getvar(root,'lat', 'f4', ('northing','easting',), 4)
			v_lon = nc.getvar(root,'lon', 'f4', ('northing','easting',), 4)
			v_lon[:] = nc.getvar(sample, 'lon')[:]
			v_lat[:] = nc.getvar(sample, 'lat')[:]
			nc.close(sample)
		if isinstance(data,collections.Mapping):
			for d in data:
				self.do_var(root, d, data[d])
		else:
			self.create_var(root, 'data', data)
		# save the content inside the compact file
		if not root is None: nc.close(root)
		f = File(localname=localname, downloaded=True, begin_download=begin_time, end_download=datetime.now())
		f.save()
		return f
	def do_var(self, root, var_name, files):
		count = 0
		max_count = len(files[c])
		print "Compacting ", var_name
		shape = nc.getvar(root,'lat').shape
		begin_time = datetime.now()
		for f in files:
			# join the distributed content
			ch = f.channel()
			v_ch   = nc.getvar(root,var_name, 'f4', ('timing','northing','easting',), 4)
			v_ch_t = nc.getvar(root,var_name + 'time', 'f4', ('timing',))
			try:
				rootimg, n = nc.open(f.completepath())
				data = (nc.getvar(rootimg, 'data'))[:]
				# Force all the channels to the same shape
				data = matrix.adapt(data, shape)
				if v_ch.shape[1] == data.shape[1] and v_ch.shape[2] == data.shape[2]:
					index = v_ch.shape[0]
					v_ch[index,:] = data
					v_ch_t[index] = calendar.timegm(f.image_datetime().utctimetuple())
				nc.close(rootimg)
				nc.sync(root)
				print "\r","\t" + str(count/max_count * 100).zfill(2) + "%",
			except RuntimeError, e:
				print f.completepath()
