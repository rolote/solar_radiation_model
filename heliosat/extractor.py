#!/usr/bin/env python

import domain_process as dp
import processfiles as pf
import h5py
from functions import *
import msg_navigation as msg
from netCDF4 import Dataset
import tlinke
from datetime import datetime
import calendar
from scipy import stats
import os
import processgroundstations as pgs
import pylab as pl
from osgeo import gdal
from config import Config

is_hrv = False

def show(*objs):
	result = ''
	for o in objs:
		result += str(o)
	print result

def getimg_channel(name, ch):
	f = h5py.highlevel.File(name)
	img_sp = f['U-MARF/MSG/Level1.5/DATA/Channel '+str(ch).zfill(2)+'/IMAGE_DATA'].value
	slopeoffset = f['U-MARF/MSG/Level1.5/METADATA/HEADER/RadiometricProcessing/Level15ImageCalibration_ARRAY']
	slopeoffsettuple = (slopeoffset['Cal_Slope'][ch-1], slopeoffset['Cal_Offset'][ch-1])
	f.close()
	return img_sp, slopeoffsettuple

def getsatelliteradiance(filename, hrv):
	if (hrv):
		img, slopeoffset = dp.getsubimg(getimg_channel(filename, 12), hrv)
		satelliteradiance = img * slopeoffset[0] + slopeoffset[1]
	else:
		# Spectral radiance
		img_1, slopeoffset_1 = getimg_channel(filename, 1)
		img_1 = dp.getsubimg(img_1, hrv)
		img_1 = img_1 * slopeoffset_1[0] + slopeoffset_1[1]
		img_2, slopeoffset_2 = getimg_channel(filename, 2)
		img_2 = dp.getsubimg(img_2, hrv)
		img_2 = img_2 * slopeoffset_2[0] + slopeoffset_2[1]
		#dp.getpng(dp.matrixtogrey(img_1), "anda_1.png")
		#dp.getpng(dp.matrixtogrey(img_2), "anda_2.png")
		# Only radiance
		img_1 = img_1 * 120.45 / 65.2065
		img_2 = img_2 * 63.46 / 73.1869
		img = (img_1, img_2)
		# Combined radiance
		satelliteradiance = 1.0605 * (4.49459 * img_1 + 2.36764 * img_2) + 0.5909
	return satelliteradiance, img

def nc_process_getvariable(root, name, vtype, dimensions, digits=0):
	try:
		v = root.variables[name]
	except KeyError:
		if digits > 0:
			v = root.createVariable(name, vtype, dimensions, zlib=True, least_significant_digit=digits)
		else:
			v = root.createVariable(name, vtype, dimensions, zlib=True)
	return v

def nc_process_create(filename):
	if os.path.exists(filename):
		rootgrp = Dataset(filename,'a')
	else:
		rootgrp = Dataset(filename,'w',format='NETCDF4')
	return rootgrp

def nc_process_insert_geo(rootgrp, lat, lon, terrain):
	d_north = rootgrp.createDimension('northing', lat.shape[0])
	d_east = rootgrp.createDimension('easting', lat.shape[1])
	d_timing = rootgrp.createDimension('timing', None)
	v_lat = nc_process_getvariable(rootgrp,'latitudes', 'f4', ('northing','easting',), 4)
	v_lon = nc_process_getvariable(rootgrp,'longitudes', 'f4', ('northing','easting',), 4)
	v_terrain = nc_process_getvariable(rootgrp,'elevacion_terreno', 'f4', ('northing','easting',), 4)
	v_lat[:] = lat
	v_lon[:] = lon
	v_terrain[:] = terrain

def nc_process_insert_img(rootgrp, index, dt, img, linketurbidity, hrv):
	v_dt = nc_process_getvariable(rootgrp,'datetime', 'u8', ('timing',))
	v_dt[index] = getintfromdatetime(dt)
	if hrv:
		v_img_12 = nc_process_getvariable(rootgrp,'canal_12', 'f4', ('timing','northing','easting',),4)
		v_img_12[index,:] = img
	else:
		v_img_01 = nc_process_getvariable(rootgrp,'canal_01', 'f4', ('timing','northing','easting',),4)
		v_img_02 = nc_process_getvariable(rootgrp,'canal_02', 'f4', ('timing','northing','easting',),4)
		v_img_01[index,:] = img[0]
		v_img_01[index,:] = img[1]
	v_linketurbidity = nc_process_getvariable(rootgrp,'tlinke', 'f4', ('timing','northing','easting',),4)
	v_linketurbidity[index,:] = linketurbidity
	#rootgrp.sync()

def nc_process_insert_tmp(rootgrp, index, tiempotst, slots, radiance, atmosphericradiance, gc, cloudalbedo, apparentalbedo, observedalbedo, atmosphericalbedo, solarelevation, tearth, tsat):
    v_tiempotst = nc_process_getvariable(rootgrp,'tiempo_tst', 'f4', ('timing','northing','easting',),4)
    v_tiempotst[index,:] = tiempotst
    v_slots = nc_process_getvariable(rootgrp,'slots', 'u1', ('timing',))
    v_slots[index] = slots
    v_radiance = nc_process_getvariable(rootgrp,'radiancia', 'f4', ('timing','northing','easting',),4)
    v_radiance[index,:] = radiance
    v_atmosphericradiance = nc_process_getvariable(rootgrp,'radiancia_atmosferica', 'f4', ('timing','northing','easting',),4)
    v_atmosphericradiance[index,:] = atmosphericradiance
    v_gc = nc_process_getvariable(rootgrp, 'radiacion_global_despejado', 'f4', ('timing','northing','easting',),4)
    v_gc[index,:] = gc
    v_cloudalbedo = nc_process_getvariable(rootgrp, 'albedo_nubes', 'f4', ('timing','northing','easting',),4)
    v_cloudalbedo[index,:] = cloudalbedo
    v_apparentalbedo = nc_process_getvariable(rootgrp, 'albedo_aparente', 'f4', ('timing','northing','easting',),4)
    v_apparentalbedo[index,:] = apparentalbedo
    v_observedalbedo = nc_process_getvariable(rootgrp, 'albedo_observado', 'f4', ('timing','northing','easting',),4)
    v_observedalbedo[index,:] = observedalbedo
    v_atmosphericalbedo = nc_process_getvariable(rootgrp, 'albedo_atmosferico', 'f4', ('timing','northing','easting',),4)
    v_atmosphericalbedo[index,:] = atmosphericalbedo
    v_solarelevation = nc_process_getvariable(rootgrp, 'elevacion_solar', 'f4', ('timing','northing','easting',),4)
    v_solarelevation[index,:] = solarelevation
    v_tearth = nc_process_getvariable(rootgrp, 'transmitancia_global_descendente', 'f4', ('timing','northing','easting',),4)
    v_tearth[index,:] = tearth
    v_tsat = nc_process_getvariable(rootgrp, 'transmitancia_global_ascendente', 'f4', ('timing','northing','easting',),4)
    v_tsat[index,:] = tsat
    #rootgrp.sync()

def nc_process_ready(rootgrp):
    rootgrp.close()

def geti0met(hrv):
	return 79.0113 if hrv else 693.17
	
def getfilename(year, month, hrv):
	return Config.DATA_ROOT_MOUNT+"/h5files/"+dp.DOMAIN + "_" + str(year) + "_" + str(month).zfill(2) + ('hrv' if hrv else 'nonhrv')+'.nc'
	
def getterrain(hrv):
	filename =  Config.DATA_ROOT_MOUNT +'/terrain/srtm_' + ('hrv' if hrv else 'nonhrv') + '.tif'
	ds = gdal.Open(filename, gdal.GA_ReadOnly)
	data = ds.ReadAsArray()
	data[data == -32768] = numpi.nan
	return data

def extractimages(year, month, lat, lon, hrv):
	l = pf.listmonth(dp.DOMAIN, year, month)
	l.sort()
	extraterrestrialirradiance = 1367.0
	terrain = getterrain(hrv)
	root = nc_process_create(getfilename(year, month, hrv))
	nc_process_insert_geo(root, lat, lon, terrain)
	index = 0
	i0met = geti0met(hrv)
	for filename in l:
		dt = pf.getdatetime(filename)
		#dt = datetime(2012,5,1,12,27,41)
		gamma = getdailyangle(getjulianday(dt),gettotaldays(dt))
		declination = getdeclination(gamma)
		timeequation = gettimeequation(gamma)
		tst_hour = gettsthour(getdecimalhour(dt), np.deg2rad(msg.SUB_LON), np.deg2rad(lon), timeequation)
		omega = gethourlyangle(tst_hour)
		solarangle = getzenitangle(declination,np.deg2rad(lat),omega)
		solarelevation = getelevation(solarangle)
		solarelevation_deg = np.rad2deg(solarelevation.min())
		if (solarelevation_deg >= 15.0):
			linketurbidity = tlinke.gettlinke(dt, hrv)
			excentricity = getexcentricity(gamma)
			satelliteradiance, img = getsatelliteradiance(filename, hrv)
			nc_process_insert_img(root, index, dt, img, linketurbidity, hrv)
			
			observedalbedo = getalbedo(satelliteradiance, i0met , excentricity, solarangle)
			bc = getbeamirradiance(extraterrestrialirradiance,excentricity,solarangle,solarelevation,linketurbidity,terrain)
			dc = getdiffuseirradiance(extraterrestrialirradiance,excentricity,solarelevation,linketurbidity)
			gc = getglobalirradiance(bc,dc)
			sza = getsatellitalzenitangle(np.deg2rad(lat), np.deg2rad(lon))
			atmosphericradiance = getatmosphericradiance(extraterrestrialirradiance, i0met,dc, sza)
			atmosphericalbedo = getalbedo(atmosphericradiance, i0met, excentricity, sza)
			satellitalelevation = getelevation(sza)
			solar_opticalpath = getopticalpath(getcorrectedelevation(solarelevation),terrain)
			solar_opticaldepth = getopticaldepth(solar_opticalpath)
			satellital_opticalpath = getopticalpath(getcorrectedelevation(satellitalelevation),terrain)
			satellital_opticaldepth = getopticaldepth(satellital_opticalpath)
			t_earth = gettransmitance(linketurbidity, solar_opticalpath, solar_opticaldepth, solarelevation)
			t_sat = gettransmitance(linketurbidity, satellital_opticalpath, satellital_opticaldepth, satellitalelevation)
			apparentalbedo = getapparentalbedo(observedalbedo,atmosphericalbedo, t_earth, t_sat)
			effectivealbedo = geteffectivealbedo(solarangle)
			cloudalbedo = getcloudalbedo(effectivealbedo,atmosphericalbedo,t_earth,t_sat)
			slots = getslots(dt)
			nc_process_insert_tmp(root,index, tst_hour, slots, satelliteradiance, atmosphericradiance, gc, cloudalbedo, apparentalbedo, observedalbedo, atmosphericalbedo, solarelevation, t_earth, t_sat)
			index += 1
			#~ print("sza=",np.rad2deg((sza.min(), sza.max())))
			#~ print("ro=",observedalbedo.min(),observedalbedo.max())
			#~ print("ro_atm=",atmosphericalbedo.min(),atmosphericalbedo.max())
			#~ print("ro_alpha=",apparentalbedo.min(),apparentalbedo.max())
			#~ print("ro_eff=",effectivealbedo.min(),effectivealbedo.max())
			#~ print("ro_cloud=",c	loudalbedo.min(),cloudalbedo.max())
	nc_process_ready(root)

def nc_process_var(root, var):
	return np.array(root.variables[var][:])

def extractgroundalbedo(filename, hrv):
	root = nc_process_create(filename)
	slots = nc_process_var(root, "slots")
	condition = ((slots >= 48 - 4*4/2) & (slots < 48 + 4*4/2)) # desde 40 inclusive a 56 (este ultimo no se incluye)
	f_radiances = nc_process_var(root, "radiancia")[condition]
	apparentalbedo = nc_process_var(root, "albedo_aparente")
	f_apparentalbedo = apparentalbedo[condition]
	m_apparentalbedo = np.ma.masked_array(f_apparentalbedo, f_radiances <= (geti0met(hrv)/np.pi) * 0.03)
	p5_apparentalbedo = np.ma.masked_array(m_apparentalbedo, m_apparentalbedo < stats.scoreatpercentile(m_apparentalbedo, 5))
	groundreferencealbedo = getsecondmin(p5_apparentalbedo)
	
	lat = nc_process_var(root, "latitudes")
	dt = getdatetimefromint(nc_process_var(root, "datetime"))
	alphanoon = np.rad2deg(getsolarelevation(dt, np.deg2rad(lat), 0))
	r_alphanoon = alphanoon * 2./3.
	r_alphanoon[r_alphanoon > 40] = 40
	r_alphanoon[r_alphanoon < 15] = 15
	solarelevation = np.rad2deg(nc_process_var(root, "elevacion_solar"))
	minimumapparentalbedo = np.ma.masked_array(apparentalbedo, solarelevation < r_alphanoon)
	groundminimumalbedo = getsecondmin(minimumapparentalbedo)
	
	aux_2g0 = 2 * groundreferencealbedo
	aux_05g0 = 0.5 * groundreferencealbedo
	groundminimumalbedo[groundminimumalbedo > aux_2g0] = aux_2g0[groundminimumalbedo > aux_2g0]
	groundminimumalbedo[groundminimumalbedo < aux_05g0] = aux_05g0[groundminimumalbedo < aux_05g0]
	
	f_groundalbedo = nc_process_getvariable(root, 'albedo_terrestre', 'f4', ('northing','easting',),4)
	f_groundalbedo[:] = groundminimumalbedo
	
	nc_process_ready(root)
	return groundminimumalbedo

def extractradiation(filename):
	root = nc_process_create(filename)
	apparentalbedo = nc_process_var(root, "albedo_aparente")
	groundalbedo = nc_process_var(root, "albedo_terrestre")
	cloudalbedo = nc_process_var(root, "albedo_nubes")
	cloudindex = getcloudindex(apparentalbedo, groundalbedo, cloudalbedo)
	f_cloudindex = nc_process_getvariable(root, 'indice_nubosidad', 'f4', ('timing','northing','easting',),4)
	f_cloudindex[:] = cloudindex
	clearsky = getclearsky(cloudindex)
	f_clearsky = nc_process_getvariable(root, 'indice_cielo_despejado', 'f4', ('timing','northing','easting',),4)
	f_clearsky[:] = clearsky
	clearskyglobalradiation = nc_process_var(root, 'radiacion_global_despejado')
	globalradiation = clearsky * clearskyglobalradiation
	f_globalradiation = nc_process_getvariable(root, 'radiacion_global', 'f4', ('timing','northing','easting',),4)
	f_globalradiation[:] = globalradiation
	nc_process_ready(root)
	return globalradiation

def fromtimestamptoint(num):
	return getintfromdatetime(pl.num2date(num))

def validate(year, month, hrv):
	tst_hour_step = 1/24.
	root = nc_process_create(getfilename(year, month, hrv))
	globalradiation = nc_process_var(root, 'radiacion_global')
	clearskyradiation = nc_process_var(root, 'radiacion_global_despejado')
	dt_int = nc_process_var(root, 'datetime')
	timestamp = np.array([date2num(getdatetimefromint(i)) for i in dt_int])
	tst_hour = nc_process_var(root, 'tiempo_tst')
	nc_process_ready(root)
	stations = pgs.getmeasuresinstations(year, month)
	for s in stations:
		l,c = dp.getpos(float(s['latitude']), float(s['longitude']), hrv)
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

lat, lon = dp.getlatlon(is_hrv)

def workwith(year, month):
	filename = getfilename(year,month,is_hrv)
	show("=======================")
	show("Year: " , year)
	show("Month: " , month)
	show("-----------------------")
	if not(os.path.exists(filename)):
		begin = datetime.now()
		o = extractimages(year, month, lat, lon, is_hrv)
		end = datetime.now()
		show("Time consumed:", end - begin)

	begin = datetime.now()
	p = extractgroundalbedo(filename, is_hrv)
	end = datetime.now()
	show("Time consumed:", end - begin)

	begin = datetime.now()
	q = extractradiation(filename)
	end = datetime.now()
	show("Time consumed:", end - begin)

	begin = datetime.now()
	s = validate(year, month, False)
	end = datetime.now()
	show("Time consumed:", end - begin)
	
for month in [3, 7]:
	workwith(2009, month)

#loadimg(False)
#img = load_img(False)
#drawmap(lat, lon, img[0], 1)
