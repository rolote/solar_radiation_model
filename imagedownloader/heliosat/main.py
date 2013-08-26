#!/usr/bin/env python

import gc

import numpy as np
from datetime import datetime
import calendar
from scipy import stats
import os
import pylab as pl
#from osgeo import gdal
import sys
import time

from libs.file import netcdf as nc
from libs.geometry import jaen as geo
from libs.linke import toolbox as linke
from libs.dem import dem
#from libs.paint import jaen as draw
import processgroundstations as pgs
from libs.console import *

SAT_LON = -60.0 # -75.3305 # longitude of sub-satellite point in degrees
GREENWICH_LON = 0.0
IMAGE_PER_HOUR = 2

def getsatelliteradiance(data, root, index):
	return data[index]

def geti0met():
	GOES_OBSERVED_ALBEDO_CALIBRATION = 1.89544 * (10 ** (-3))
	return np.pi / GOES_OBSERVED_ALBEDO_CALIBRATION

def save_temporal_data(root,index,gamma,tst_hour,declination,solarangle,solarelevation,excentricity,slots):
	v_gamma = nc.getvar(root,'gamma', 'f4', ('timing',),4)
	v_gamma[index] = gamma
	v_tst_hour = nc.getvar(root,'tst_hour', 'f4', ('timing','northing','easting',),4)
	v_tst_hour[index,:] = tst_hour
	v_declination = nc.getvar(root,'declination', 'f4', ('timing',),4)
	v_declination[index] = declination
	v_solarangle = nc.getvar(root, 'solarangle', 'f4', ('timing','northing','easting',),4)
	v_solarangle[index] = solarangle
	v_solarelevation = nc.getvar(root, 'solarelevation', 'f4', ('timing','northing','easting',),4)
	v_solarelevation[index] = solarelevation
	v_excentricity = nc.getvar(root, 'excentricity', 'f4', ('timing','northing','easting',),4)
	v_excentricity[index] = excentricity
	v_slots = nc.getvar(root,'slots', 'u1', ('timing',))
	v_slots[index] = slots
	nc.sync(root)

def process_temporal_data(lat, lon, root):
	times = [ datetime.fromtimestamp(int(t)) for t in nc.getvar(root, 'time') ]
	indexes = range(len(times))
	for i in indexes:
		show("\rTemporal data: preprocessing image %d / %d " % (i, len(indexes)-1))
		dt = times[i]
		# Calculate some geometry parameters
		# Parameters that need the datetime: gamma, tst_hour, slots, linketurbidity
		gamma = geo.getdailyangle(geo.getjulianday(dt),geo.gettotaldays(dt))
		tst_hour = geo.gettsthour(geo.getdecimalhour(dt), GREENWICH_LON, lon, geo.gettimeequation(gamma))
		declination = geo.getdeclination(gamma)
		slots = geo.getslots(dt,IMAGE_PER_HOUR)
		omega = geo.gethourlyangle(tst_hour, lat/abs(lat))
		solarangle = geo.getzenithangle(declination,lat,omega)
		solarelevation = geo.getelevation(solarangle)
		excentricity = geo.getexcentricity(gamma)
		save_temporal_data(root,i,gamma,tst_hour,declination,solarangle,solarelevation,excentricity,slots)
	say("Projecting Linke's turbidity index... ")
	linke.cut_projected(root)
	say("Calculating the satellital zenith angle... ")
	satellitalzenithangle = geo.getsatellitalzenithangle(lat, lon, SAT_LON)
	dem.cut_projected(root)
	v_satellitalzenithangle = nc.getvar(root,'satellitalzenithangle', 'f4', ('northing','easting',),4)
	v_satellitalzenithangle[:] = satellitalzenithangle
	nc.sync(root)

def process_irradiance(lat, lon, data, root):
	excentricity = nc.getvar(root,'excentricity')[:]
	solarangle = nc.getvar(root,'solarangle')[:]
	solarelevation = nc.getvar(root,'solarelevation')[:]
	linketurbidity = nc.getvar(root,'linketurbidity')[0]
	terrain = nc.getvar(root,'dem')[:]
	say("Calculating beam, diffuse and global irradiance... ")
	# The average extraterrestrial irradiance is 1367.0 Watts/meter^2
	bc = geo.getbeamirradiance(1367.0,excentricity,solarangle,solarelevation,linketurbidity,terrain)
	dc = geo.getdiffuseirradiance(1367.0,excentricity,solarelevation,linketurbidity)
	gc = geo.getglobalirradiance(bc,dc)
	v_bc = nc.getvar(root, 'bc', 'f4', ('timing','northing','easting',),4)
	v_bc[:] = bc
	v_dc = nc.getvar(root, 'dc', 'f4', ('timing','northing','easting',),4)
	v_dc[:] = dc
	v_gc = nc.getvar(root, 'gc', 'f4', ('timing','northing','easting',),4)
	v_gc[:] = gc
	nc.sync(root)

def process_atmospheric_irradiance(lat, lon, data, root):
	i0met = geti0met()
	dc = nc.getvar(root,'dc')[:]
	satellitalzenithangle = nc.getvar(root,'satellitalzenithangle')[:]
	excentricity = nc.getvar(root,'excentricity')[:]
	say("Calculating atmospheric irradiance... ")
	atmosphericradiance = geo.getatmosphericradiance(1367.0, i0met,dc, satellitalzenithangle)
	atmosphericalbedo = geo.getalbedo(atmosphericradiance, i0met, excentricity, satellitalzenithangle)
	satellitalelevation = geo.getelevation(satellitalzenithangle)
	v_atmosphericalbedo = nc.getvar(root, 'atmosphericalbedo', 'f4', ('timing','northing','easting',),4)
	v_atmosphericalbedo[:] = atmosphericalbedo
	v_satellitalelevation = nc.getvar(root, 'satellitalelevation', 'f4', ('northing','easting',),4)
	v_satellitalelevation[:] = satellitalelevation
	nc.sync(root)

def process_optical_fading(lat, lon, data, root):
	solarelevation = nc.getvar(root,'solarelevation')[:]
	terrain = nc.getvar(root,'dem')[:]
	satellitalelevation = nc.getvar(root, 'satellitalelevation')[:]
	linketurbidity = nc.getvar(root,'linketurbidity')[0]
	say("Calculating optical path and optical depth... ")
	# The maximum height of the non-transparent atmosphere is at 8434.5 mts
	solar_opticalpath = geo.getopticalpath(geo.getcorrectedelevation(solarelevation),terrain, 8434.5)
	solar_opticaldepth = geo.getopticaldepth(solar_opticalpath)
	satellital_opticalpath = geo.getopticalpath(geo.getcorrectedelevation(satellitalelevation),terrain, 8434.5)
	satellital_opticaldepth = geo.getopticaldepth(satellital_opticalpath)
	say("Calculating sun-earth and earth-satellite transmitances... ")
	t_earth = geo.gettransmitance(linketurbidity, solar_opticalpath, solar_opticaldepth, solarelevation)
	t_sat = geo.gettransmitance(linketurbidity, satellital_opticalpath, satellital_opticaldepth, satellitalelevation)
	v_earth = nc.getvar(root, 't_earth', 'f4', ('timing','northing','easting',),4)
	v_earth[:] = t_earth
	v_sat = nc.getvar(root, 't_sat', 'f4', ('northing','easting',),4)
	v_sat[:] = t_sat
	nc.sync(root)

def process_albedos(lat, lon, data, root):
	i0met = geti0met()
	excentricity = nc.getvar(root,'excentricity')[:]
	solarangle = nc.getvar(root,'solarangle')[:]
	atmosphericalbedo = nc.getvar(root,'atmosphericalbedo')[:]
	t_earth = nc.getvar(root,'t_earth')[:]
	t_sat = nc.getvar(root,'t_sat')[:]
	say("Calculating observed albedo, apparent albedo, effective albedo and cloud albedo... ")
	observedalbedo = geo.getalbedo(data, i0met , excentricity, solarangle)
	apparentalbedo = geo.getapparentalbedo(observedalbedo,atmosphericalbedo, t_earth, t_sat)
	effectivealbedo = geo.geteffectivealbedo(solarangle)
	cloudalbedo = geo.getcloudalbedo(effectivealbedo,atmosphericalbedo,t_earth,t_sat)
	v_observedalbedo = nc.getvar(root, 'observedalbedo', 'f4', ('timing','northing','easting',),4)
	v_observedalbedo[:] = observedalbedo
	v_apparentalbedo = nc.getvar(root, 'apparentalbedo', 'f4', ('timing','northing','easting',),4)
	v_apparentalbedo[:] = apparentalbedo
	v_effectivealbedo = nc.getvar(root, 'effectivealbedo', 'f4', ('timing','northing','easting',),4)
	v_effectivealbedo[:] = effectivealbedo
	v_cloudalbedo = nc.getvar(root, 'cloudalbedo', 'f4', ('timing','northing','easting',),4)
	v_cloudalbedo[:] = cloudalbedo
	nc.sync(root)

def process_atmospheric_data(lat, lon, data, root):	
	process_irradiance(lat, lon, data, root)
	process_atmospheric_irradiance(lat, lon, data, root)
	process_optical_fading(lat, lon, data, root)
	process_albedos(lat, lon, data, root)

def process_ground_albedo(lat, lon, data, root):
	slots = nc.getvar(root, "slots")[:]
	declination = nc.getvar(root, "declination")[:]
	#The day is divided in _slots_ to avoid the minutes diferences between days.
	# TODO: Related with the solar hour at the noon if the pictures are taken every 15 minutes (meteosat)
	say("Calculating the noon window... ")
	slot_window_in_hours = 4
	# On meteosat are 96 image per day
	image_per_hour = IMAGE_PER_HOUR
	image_per_day = 24 * image_per_hour
	# and 48 image to the noon
	noon_slot = image_per_day / 2
	half_window = image_per_hour * slot_window_in_hours/2
	min_slot = noon_slot - half_window
	max_slot = noon_slot + half_window
	# Create the condition used to work only with the data inside that window
	say("Filtering the data outside the calculated window... ")
	condition = ((slots >= min_slot) & (slots < max_slot)) # TODO: Meteosat: From 40 to 56 inclusive (the last one is not included)
	apparentalbedo = nc.getvar(root, "apparentalbedo")[:]
	m_apparentalbedo = np.ma.masked_array(apparentalbedo[condition], data[condition] <= (geti0met()/np.pi) * 0.03)
	# To do the nexts steps needs a lot of memory
	say("Calculating the ground reference albedo... ")
	# TODO: Should review the p5_apparentalbedo parameters and shapes
	p5_apparentalbedo = np.ma.masked_array(m_apparentalbedo, m_apparentalbedo < stats.scoreatpercentile(m_apparentalbedo, 5))
	groundreferencealbedo = geo.getsecondmin(p5_apparentalbedo)
	# Calculate the solar elevation using times, latitudes and omega
	say("Calculating solar elevation... ")
	r_alphanoon = geo.getsolarelevation(declination, lat, 0)
	r_alphanoon = r_alphanoon * 2./3.
	r_alphanoon[r_alphanoon > 40] = 40
	r_alphanoon[r_alphanoon < 15] = 15
	solarelevation = nc.getvar(root, "solarelevation")[:]
	say("Calculating the apparent albedo second minimum... ")
	groundminimumalbedo = geo.getsecondmin(np.ma.masked_array(apparentalbedo[condition], solarelevation[condition] < r_alphanoon[condition]))
	aux_2g0 = 2 * groundreferencealbedo
	aux_05g0 = 0.5 * groundreferencealbedo
	groundminimumalbedo[groundminimumalbedo > aux_2g0] = aux_2g0[groundminimumalbedo > aux_2g0]
	groundminimumalbedo[groundminimumalbedo < aux_05g0] = aux_05g0[groundminimumalbedo < aux_05g0]
	say("Synchronizing with the NetCDF4 file... ")
	f_groundalbedo = nc.getvar(root, 'groundalbedo', 'f4', ('northing','easting',),4)
	f_groundalbedo[:] = groundminimumalbedo
	nc.sync(root)

def process_radiation(lat, lon, data, root):
	apparentalbedo = nc.getvar(root, "apparentalbedo")[:]
	groundalbedo = nc.getvar(root, "groundalbedo")[:]
	cloudalbedo = nc.getvar(root, "cloudalbedo")[:]
	say("Calculating the cloud index... ")
	cloudindex = geo.getcloudindex(apparentalbedo, groundalbedo, cloudalbedo)
	f_cloudindex = nc.getvar(root, 'cloudinessindex', 'f4', ('timing','northing','easting',),4)
	f_cloudindex[:] = cloudindex
	say("Calculating the clear sky... ")
	clearsky = geo.getclearsky(cloudindex)
	f_clearsky = nc.getvar(root, 'clearskyindex', 'f4', ('timing','northing','easting',),4)
	f_clearsky[:] = clearsky
	say("Calculating the global radiation... ")
	clearskyglobalradiation = nc.getvar(root, 'gc')[:]
	globalradiation = clearsky * clearskyglobalradiation
	f_globalradiation = nc.getvar(root, 'globalradiation', 'f4', ('timing','northing','easting',),4)
	f_globalradiation[:] = globalradiation


def process_validate(year, month, times, root):
	tst_hour_step = 1/24.
	globalradiation = nc.getvar(root, 'globalradiation')
	clearskyradiation = nc.getvar(root, 'clearskyglobalradiation')
	timestamp = np.array([date2num(dt) for dt in times])
	tst_hour = nc.getvar(root, 'tst_hour')

	stations = pgs.getmeasuresinstations(year, month)
	for s in stations:
		l,c = dp.getpos(float(s['latitude']), float(s['longitude']))
		globalradiationinposition = globalradiation[:,l,c]
		tst_datehour = gettstdatetime(timestamp,tst_hour[:,l,c])
		estimated = []
		measured = []
		for m in s['measures']:
			cond = ((tst_datehour > m['timestamp'] - tst_hour_step) & (tst_datehour <= m['timestamp']))
			tst_filtered = tst_datehour[cond]
			if tst_filtered.size >= 4 and m['ghi'] > 0:
				estimated.append(globalradiationinposition[cond].mean())
				measured.append(m['ghi'])
		measured = np.array(measured)
		estimated = np.array(estimated)
		diff = estimated - measured
		ghi_mean = measured.mean()
		ghi_ratio = 100 / ghi_mean
		show("----------")
		show("Length:", measured.size)
		show("mean(GHI)", ghi_mean)
		show("mean(estimated)", estimated.mean())
		show(s['Name'])
		bias = diff.mean()
		show("BIAS:", bias, "(", bias * ghi_ratio, "%)")
		rmse = np.sqrt((diff**2).mean())
		show("RMSE:", rmse, "(", rmse * ghi_ratio, "%)")
		mae = np.absolute(diff).mean()
		show("MAE:", mae, "(", mae * ghi_ratio, "%)")

def workwith(year=2011, month=05, filename="goes13.all.BAND_02.nc"):
	show("=======================")
	show("Year: " , year)
	show("Month: " , month)
	show("Filename: ", filename)
	show("-----------------------\n")

	root, is_new = nc.open(filename)
	lat = (nc.getvar(root, 'lat'))[:]
	lon = (nc.getvar(root, 'lon'))[:]
	data = nc.getvar(root, 'data')[:]
	
	process_temporal_data(lat, lon, root)
	process_atmospheric_data(lat, lon, data, root)

	process_ground_albedo(lat, lon, data, root)

	process_radiation(lat, lon, data, root)

	#s = process_validate(year, month, root)
	#draw.getpng(draw.matrixtogrey(data[15]),'prueba.png')
	nc.close(root)
	show("Process finished.\n")

def show_times(*args):
	begin = datetime.now()
	result = yield aspects.proceed(*args)
	end = datetime.now()
	say("\t[time consumed: %.2f seconds]\n" % (end - begin).total_seconds())
	yield aspects.return_stop(result)

import aspects
import re
current_module = sys.modules[__name__]
methods = current_module.__dict__
fxs = [ func for name,func in methods.items() if re.match( r'^process.*',name) or re.match( r'workwith',name) ]
aspects.with_wrap(show_times, *fxs)


#import cProfile, pstats, io
#pr = cProfile.Profile()
#pr.enable()
workwith(sys.argv[1], sys.argv[2], sys.argv[3])
#pr.disable()
#s = io.StringIO()
#ps = pstats.Stats(pr, stream=s)
#ps.dump_stats('profile_results')
