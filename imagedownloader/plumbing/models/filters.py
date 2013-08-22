from django.db import models
from requester.models import *
from process import *
import numpy as np
from libs.geometry import jaen as geo
from libs.file import netcdf as nc

class FilterSolarElevation(Process):
	class Meta:
        	app_label = 'plumbing'
	minimum = models.DecimalField(max_digits=4,decimal_places=2)
	def do(self,files):
		result = {}
		for k in files:
			sub_lon = float(files[k][0].order.request.automatic_download.area.getlongitude())
			lat,lon = files[k][0].image_latlon()
			result[k] = [ f	for f in files[k] if self.solar_elevation(f, sub_lon, lat, lon) >= self.minimum ]
		return result
	def solar_elevation(self, f, sub_lon, lat, lon):
		dt = f.image_datetime()
		solarelevation_min = -90.0
		if not lon is None:
			solarelevation = geo.getsolarelevationmatrix(dt, sub_lon, lat, lon)
			solarelevation_min = solarelevation.min()
		return solarelevation_min

class CollectTimed(Process):
	class Meta:
        	app_label = 'plumbing'
	# Should multiplex, if it has other collect applyied previously
	monthly = models.BooleanField()
	def do(self, files):
		#compacted = {'goes13.2013.01.BAND_'+ch.in_file+'.nc': files}
		#c = Compact()
		#c.apply(compacted)
		return files

class CollectChannel(Process):
	class Meta:
        	app_label = 'plumbing'
	# Should multiplex, if it has other collect applyied previously
	#for ch in Channel.objects.all():
	# f.channel() == ch.in_file ]
	def do(self, files):
		result = {}
		for k in files:
			for f in files[k]:
				key = f.satellite() + '.' + k + '.BAND_' + f.channel()
				if not key in result:
					result[key] = []
				result[key].append(f)
		return result

class FilterChannel(Process):
	class Meta:
        	app_label = 'plumbing'
	channels = models.ManyToManyField(Channel,db_index=True)
	def do(self, files):
		result = {}
		chs = [ str(ch.in_file) for ch in self.channels.all() ]
		sat = self.channels.all()[0].satellite
		for k in files:
			result[k] = [ f for f in files[k] if f.channel() in chs and f.satellite() == sat.in_file ]
		return result

class FilterTimed(Process):
	class Meta:
        	app_label = 'plumbing'
	time_range = models.ManyToManyField(UTCTimeRange,db_index=True)
	def do(self, files):
		result = {}
		for k in files:
			result[k] = [ f for f in files[k] if self.time_range.contains(f.image_datetime()) ]
		return result

class TransformCountsToRadiation(Process):
	class Meta:
		app_label = 'plumbing'
	counts_shift = models.IntegerField()
	calibrated_coefficient = models.DecimalField(max_digits=5,decimal_places=3)
	space_measurement = models.DecimalField(max_digits=5,decimal_places=3)
	def do(self, files):
		for c in files:
			for f in files[c]:
				if f.channel() == '01':
					root, is_new = nc.open(f.completepath())
					var = nc.getvar(root, 'data')
					data = np.zeros(var.shape)
					for i in range(var.shape[0]):
						data = var[i]
						data = self.calibrated_coefficient * ((data / self.counts_shift) - self.space_measurement)
						var[i] = data
					nc.close(root)
		return files
