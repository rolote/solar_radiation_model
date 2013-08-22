import numpy as np
from libs.console import *

try:
	from pycuda.compiler import SourceModule
	import pycuda.gpuarray as gpuarray
	import pycuda.driver as cuda
	import pycuda.autoinit
	cuda_can_help = False
except ImportError:
	class SourceModule:
		def __init__(self, c):
			pass
	cuda_can_help = False

import gpu
from datetime import datetime

def iterative_broadcast(*args):
	ITERABLE_AMOUNT_OF_DIMS=[1,3]
	# Get the arguments dimensions
	dimensions = [ (lambda x: len(x.shape) if isinstance(x, np.ndarray) else 0)(a) for a in args ]
	# Get the positions of the huge matrix in term of maximum amount of dimensions (detect cores matrix)
	iterable_args = [i for i, dn in enumerate(dimensions) if dn in ITERABLE_AMOUNT_OF_DIMS ]
	# Define the first dimension as iterable, and obtain the amount of iterations to be done
	iteration_amount = 0
	if len(iterable_args) > 0:
		iteration_amount = args[iterable_args[0]].shape[0]
		huge_i = 0
		for i, a in enumerate(args):
			if dimensions[i] > dimensions[huge_i]:
				huge_i = i
		result_shape = args[huge_i].shape
		if dimensions[huge_i] > min(ITERABLE_AMOUNT_OF_DIMS) and dimensions[huge_i] < max(ITERABLE_AMOUNT_OF_DIMS):
			result_shape = args[iterable_args[0]].shape + result_shape
	if len(iterable_args) > 0:
		# Begin the creation of the argument to be used in the iterative call
		result = np.zeros(result_shape)
		for it_idx in range(iteration_amount):
			# Update the argument according to the iteration
			tmp_args = [ a[it_idx] if i in iterable_args else a for i,a in enumerate(args)]
			# Iterate using the wrapped function
			show_progress(it_idx)
			tmp_args = tuple(tmp_args)
			result[it_idx] = yield aspects.proceed(*tmp_args)
	else:
		result = yield aspects.proceed(*args)
	yield aspects.return_stop(result)

def getjulianday(dt):
	return dt.timetuple()[7]

def gettotaldays(dt):
	return getjulianday(datetime(dt.year,12,31))

def getdailyangle(julianday, totaldays):
	return np.rad2deg(2 * np.pi * (julianday -1) / totaldays)

mod_getexcentricity = SourceModule("""
	  __global__ void getexcentricity(float *gamma)
	  {
		int it = threadIdx.x;
		int i2d = blockDim.x*blockIdx.x;
		int i3d = i2d + it;
		gamma[i3d] *= """ + gpu._deg2rad_ratio + """;
		gamma[i3d] = 1.000110 + 0.034221 * cos(gamma[i3d]) + 0.001280 * sin(gamma[i3d]) + 0.000719 * cos(2 * gamma[i3d]) + 0.000077 * sin(2 * gamma[i3d]);
	  }
	  """)
def getexcentricity(gamma):
	result = None
	if cuda_can_help:
		func = mod_getexcentricity.get_function("getexcentricity")
		sh = gamma.shape
		show("")
		for i in range(sh[0]):
			show("\r--->" + str(i).zfill(3) + "/" + str(sh[0]-1).zfill(3))
			gamma[i] = gpu._gpu_exec(func, gamma[i])
		result = gamma
	else:
		gamma = np.deg2rad(gamma)
		result = 1.000110 + 0.034221 * np.cos(gamma) + 0.001280 * np.sin(gamma) + 0.000719 * np.cos(2 * gamma) + 0.000077 * np.sin(2 * gamma)
	return result

mod_getdeclination = SourceModule("""
	  __global__ void getdeclination(float *gamma)
	  {
		int it = threadIdx.x;
		int i2d = blockDim.x*blockIdx.x;
		int i3d = i2d + it;
		gamma[i3d] *= """ + gpu._deg2rad_ratio + """;
		gamma[i3d] = 0.006918 - 0.399912 * cos(gamma[i3d]) + 0.070257 * sin(gamma[i3d]) - 0.006758 * cos(2 * gamma[i3d]) + 0.000907 * sin(2 * gamma[i3d]) - 0.002697 * cos(3 * gamma[i3d]) + 0.00148 * sin(3 * gamma[i3d]);
		gamma[i3d] *= """ + gpu._rad2deg_ratio + """;
	  }
	  """)
def getdeclination(gamma):
	result = None
	if cuda_can_help:
		func = mod_getdeclination.get_function("getdeclination")
		#sh = gamma.shape
		#print "\n",
		#for i in range(sh[0]):
		#	print "\r--->" + str(i).zfill(3) + "/" + str(sh[0]-1).zfill(3),
		result = gpu._gpu_exec(func, gamma)
	else:
		gamma = np.deg2rad(gamma)
		result = np.rad2deg(0.006918 - 0.399912 * np.cos(gamma) + 0.070257 * np.sin(gamma) - 0.006758 * np.cos(2 * gamma) + 0.000907 * np.sin(2 * gamma) - 0.002697 * np.cos(3 * gamma) + 0.00148 * np.sin(3 * gamma))
	return result

def gettimeequation(gamma):
	gamma = np.deg2rad(gamma)
	return np.rad2deg((0.000075 + 0.001868 * np.cos(gamma) - 0.032077 * np.sin(gamma) - 0.014615 * np.cos(2 * gamma) - 0.04089 * np.sin(2 * gamma)) * (12 /np.pi))

def getdecimalhour(dt):
	return dt.hour + dt.minute/60.0 + dt.second/3600.0

def gettsthour(hour, d_ref, d, timeequation):
	timeequation = np.deg2rad(timeequation)
	lon_diff = np.deg2rad(d_ref - d)
	return hour - lon_diff * (12 / np.pi) + timeequation

def gethourlyangle(tst_hour, latitud_sign):
	return np.rad2deg((tst_hour - 12) * latitud_sign * np.pi / 12)

mod_getzenitangle = SourceModule("""
	  __global__ void getzenitangle(float *hourlyangle, float *lat, float *dec)
	  {
		int it = threadIdx.x;
		int i2d = blockDim.x*blockIdx.x;
		int i3d = i2d + it;
		float lat_r = lat[i2d] * """ + gpu._deg2rad_ratio + """;
		float dec_r = dec[it] * """ + gpu._deg2rad_ratio + """;
		hourlyangle[i3d] *= """ + gpu._deg2rad_ratio + """;
		hourlyangle[i3d] = acos(sin(dec_r) * sin(lat_r) + cos(dec_r) * cos(lat_r) * cos(hourlyangle[i3d]));
		hourlyangle[i3d] *= """ + gpu._rad2deg_ratio + """;
	  }
	  """)
def getzenithangle(declination, latitude, hourlyangle):
	result = None
	if cuda_can_help:
		func = mod_getzenitangle.get_function("getzenitangle")
		result = gpu._gpu_exec(func, hourlyangle, latitude, declination)
	else:
		hourlyangle = np.deg2rad(hourlyangle)
		lat = np.deg2rad(latitude)
		dec = np.deg2rad(declination)
		# TODO: Evaluate this situation. Shapes: dec:(252) ; lat:(242,384)
		result = np.rad2deg(np.arccos(np.sin(dec) * np.sin(lat) + np.cos(dec) * np.cos(lat) * np.cos(hourlyangle)))
	return result

def getelevation(zenithangle):
	zenithangle = np.deg2rad(zenithangle)
	return np.rad2deg((np.pi / 2) - zenithangle)

def getsolarelevationmatrix(dt, sub_lon, lat, lon):
	gamma = getdailyangle(getjulianday(dt),gettotaldays(dt))
	declination = getdeclination(gamma)
	timeequation = gettimeequation(gamma)
	tst_hour = gettsthour(getdecimalhour(dt), sub_lon, lon, timeequation)
	omega = gethourlyangle(tst_hour,lat/abs(lat))
	solarangle = getzenitangle(declination,lat,omega)
	return getelevation(solarangle)


def getcorrectedelevation(elevation):
	elevation = np.deg2rad(elevation)
	return np.rad2deg(elevation + 0.061359*((0.1594 + 1.1230*elevation + 0.065656 * np.power(elevation,2))/(1+ 28.9344 * elevation + 277.3971 * np.power(elevation,2))))

def getopticalpath(correctedelevation, terrainheight, atmosphere_theoretical_height):
	# In the next line the correctedelevation is used over a degree base
	power = np.power(correctedelevation+6.07995, -1.6364)
	# Then should be used over a radian base
	correctedelevation = np.deg2rad(correctedelevation)
	return (np.exp(-terrainheight/atmosphere_theoretical_height)) / (np.sin(correctedelevation) + 0.50572 * power)

def getopticaldepth(opticalpath):
	tmp = np.zeros(opticalpath.shape) + 1.0
	highslopebeam = opticalpath <= 20
	lowslopebeam = opticalpath > 20
	tmp[highslopebeam] = 1/(6.6296 + 1.7513 * opticalpath[highslopebeam] - 0.1202 * np.power(opticalpath[highslopebeam],2) + 0.0065 * np.power(opticalpath[highslopebeam],3) - 0.00013 * np.power(opticalpath[highslopebeam],4))
	tmp[lowslopebeam] = 1/(10.4 + 0.718 * opticalpath[lowslopebeam])
	return tmp

def getbeamtransmission(linketurbidity, opticalpath, opticaldepth):
	return np.exp(-0.8662 * linketurbidity * opticalpath * opticaldepth)

def gethorizontalirradiance(extraterrestrialirradiance, excentricity, zenitangle):
	zenitangle = np.deg2rad(zenitangle)
	return extraterrestrialirradiance * excentricity * np.cos(zenitangle)

def getbeamirradiance(extraterrestrialirradiance, excentricity, zenitangle, solarelevation, linketurbidity, terrainheight):
	#print excentricity.shape, zenitangle.shape, solarelevation.shape, linketurbidity.shape, terrainheight.shape
	correctedsolarelevation = getcorrectedelevation(solarelevation)
	#TODO: Meteosat is at 8434.5 mts
	opticalpath = getopticalpath(correctedsolarelevation, terrainheight, 8434.5)
	opticaldepth = getopticaldepth(opticalpath)
	return gethorizontalirradiance(extraterrestrialirradiance, excentricity, zenitangle) * getbeamtransmission(linketurbidity, opticalpath, opticaldepth)

def getzenithdiffusetransmitance(linketurbidity):
	return -0.015843 + 0.030543 * linketurbidity + 0.0003797 * np.power(linketurbidity,2)

def getangularcorrection(solarelevation, linketurbidity):
	solarelevation = np.deg2rad(solarelevation)
	a0 = 0.264631 - 0.061581 * linketurbidity + 0.0031408 * np.power(linketurbidity,2)
	a1 = 2.0402 + 0.018945 * linketurbidity - 0.011161 * np.power(linketurbidity,2)
	a2 = -1.3025 + 0.039231 * linketurbidity + 0.0085079 * np.power(linketurbidity,2)
	zenitdiffusetransmitance = getzenithdiffusetransmitance(linketurbidity)
	c = a0*zenitdiffusetransmitance < 0.002
	a0[c] = 0.002 / zenitdiffusetransmitance[c]
	return a0 + a1 * np.sin(solarelevation) + a2 * np.power(np.sin(solarelevation),2)

def getdiffusetransmitance(linketurbidity, solarelevation):
	return getzenithdiffusetransmitance(linketurbidity) * getangularcorrection(solarelevation, linketurbidity)

def gettransmitance(linketurbidity, opticalpath, opticaldepth, solarelevation):
	return getbeamtransmission(linketurbidity, opticalpath, opticaldepth) + getdiffusetransmitance(linketurbidity, solarelevation)

def getdiffuseirradiance(extraterrestrialirradiance, excentricity, solarelevation, linketurbidity):
	return extraterrestrialirradiance * excentricity * getdiffusetransmitance(linketurbidity, solarelevation)

def getglobalirradiance(beamirradiance, diffuseirradiance):
	return beamirradiance + diffuseirradiance

mod_getalbedo = SourceModule("""
	  __global__ void getalbedo(float *radiance, float totalirradiance, float *excentricity, float *zenitangle)
	  {
		int it = threadIdx.x;
		int i2d = blockDim.x*blockIdx.x;
		int i3d = i2d + it;
		radiance[i3d] = (""" + str(np.float32(np.pi)) + """ * radiance[i3d])/(totalirradiance * excentricity[i3d] * cos(zenitangle[i3d]));
	  }
	  """)
def getalbedo(radiance, totalirradiance, excentricity, zenitangle):
	result = None
	if cuda_can_help:
		func = mod_getalbedo.get_function("getalbedo")
		sh = radiance.shape
		show("")
		for i in range(sh[0]):
			show("\r--->" + str(i).zfill(3) + "/" + str(sh[0]).zfill(3))
			radiance[i] = gpu._gpu_exec(func, radiance[i], totalirradiance, excentricity[i], zenitangle[i])
		result = radiance
	else:
		zenitangle = np.deg2rad(zenitangle)
		result = (np.pi * radiance)/(totalirradiance * excentricity * np.cos(zenitangle))
	return result

mod_getsatellitalzenithangle = SourceModule("""
	  __global__ void getsatellitalzenithangle(float *lat, float *lon, float sub_lon, float rpol, float req, float h)
	  {
		//int it = threadIdx.x;
		int i2d = blockDim.x*blockIdx.x;
		//int i3d = i2d + it;
		lat[i2d] *= """ + gpu._deg2rad_ratio + """;
		float lon_diff = (lon[i2d] - sub_lon) * """ + gpu._deg2rad_ratio + """;
		float lat_cos_only = cos(lat[i2d]);
		float re = rpol / (sqrt(1-(pow(req,2) - pow(rpol,2))/(pow(req,2))*pow(lat_cos_only,2)));
		float lat_cos = re * lat_cos_only;
		float r1 = h - lat_cos * cos(lon_diff);
		float r2 = - lat_cos * sin(lon_diff);
		float r3 = re * sin(lat[i2d]);
		float rs = sqrt(pow(r1,2) + pow(r2,2) + pow(r3,2));
		lat[i2d] = (""" + str(np.float32(np.pi)) + """ - acos((pow(h,2) - pow(re,2) - pow(rs,2))/(-2 * re * rs)));
		lat[i2d] *= """ + gpu._rad2deg_ratio + """;
	  }
	  """)
def getsatellitalzenithangle(lat, lon, sub_lon):
	result = None
	rpol = 6356.5838
	req = 6378.1690
	h = 42164.0
	if cuda_can_help:
		func = mod_getsatellitalzenithangle.get_function("getsatellitalzenithangle")
		lat = gpu._gpu_exec(func, lat, lon, sub_lon, rpol, req, h)
		result = lat
	else:
		lat = np.deg2rad(lat)
		lon_diff = np.deg2rad(lon - sub_lon)
		lat_cos_only = np.cos(lat)
		re = rpol /(np.sqrt(1-(req**2 - rpol**2)/(req**2)*np.power(lat_cos_only,2)))
		lat_cos = re * lat_cos_only
		r1 = h - lat_cos * np.cos(lon_diff)
		r2 = - lat_cos * np.sin(lon_diff)
		r3 = re * np.sin(lat)
		rs = np.sqrt(r1**2 + r2**2 + r3**2)
		result = np.rad2deg(np.pi - np.arccos((h**2 - re**2 - rs**2)/(-2 * re * rs)))
	return result

def getatmosphericradiance(extraterrestrialirradiance, i0met,diffuseclearsky, satellitalzenitangle):
	satellitalzenitangle = np.deg2rad(satellitalzenitangle)
	anglerelation = np.power((0.5 / np.cos(satellitalzenitangle)),0.8)
	return (i0met * diffuseclearsky * anglerelation) /  (np.pi * extraterrestrialirradiance)


def getdifferentialalbedo(firstalbedo, secondalbedo, t_earth, t_sat):
	return (firstalbedo - secondalbedo) / (t_earth * t_sat)


def getapparentalbedo(observedalbedo, atmosphericalbedo, t_earth, t_sat):
	apparentalbedo = getdifferentialalbedo(observedalbedo,atmosphericalbedo,t_earth,t_sat)
	apparentalbedo[apparentalbedo < 0] = 0.0
	return apparentalbedo

def geteffectivealbedo(solarangle):
	solarangle = np.deg2rad(solarangle)
	return 0.78 - 0.13 * (1-np.exp(-4 * np.power(np.cos(solarangle),5)))

def getcloudalbedo(effectivealbedo, atmosphericalbedo, t_earth, t_sat):
	cloudalbedo = getdifferentialalbedo(effectivealbedo, atmosphericalbedo, t_earth, t_sat)
	cloudalbedo[cloudalbedo < 0.2] = 0.2
	effectiveproportion = 2.24 * effectivealbedo
	cloudalbedo[cloudalbedo > effectiveproportion] = effectiveproportion[cloudalbedo > effectiveproportion]
	return cloudalbedo

def getslots(dt,images_per_hour):
	return np.int(np.round(getdecimalhour(dt) * images_per_hour))

def getintfromdatetime(dt):
	if np.iterable(dt) == 0:
		return int(dt.strftime("%Y%m%d%H%M%S"))
	else:
		return np.array([ getintfromdatetime(n) for n in number ])

def getdatetimefromint(number):
	if np.iterable(number) == 0:
		return datetime.strptime(str(number),"%Y%m%d%H%M%S")
	else:
		return np.array([ getdatetimefromint(n) for n in number ])

def getsolarelevation(declination,lat,omega):
	omega = np.deg2rad(omega)
	declination = np.deg2rad(declination)
	lat = np.deg2rad(lat)
	return np.rad2deg(np.arcsin(np.sin(declination) * np.sin(lat) + np.cos(declination) * np.sin(lat) * np.cos(omega)))

def getsecondmin(albedo):
	min1_albedo = np.ma.masked_array(albedo, albedo == np.amin(albedo, axis=0))
	return np.amin(albedo, axis=0)

def getcloudindex(apparentalbedo, groundalbedo, cloudalbedo):
	return (apparentalbedo - groundalbedo)/(cloudalbedo - groundalbedo)

def getclearsky(cloudindex):
	clearsky = np.zeros_like(cloudindex)
	cond = cloudindex < -0.2
	clearsky[cond] = 1.2
	cond = ((cloudindex >= -0.2) & (cloudindex < 0.8))
	clearsky[cond] = 1 - cloudindex[cond]
	cond = ((cloudindex >= 0.8) & (cloudindex < 1.1))
	clearsky[cond] = (31 - 55 * cloudindex[cond] + 25 * np.power(cloudindex[cond],2)) / 15
	cond = (cloudindex >= 1.1)
	clearsky[cond] = 0.05
	return clearsky

def gettstdatetime(timestamp, tst_hour):
	return np.trunc(timestamp) + tst_hour / 24.

if not cuda_can_help:
	import aspects
	import re
	excluded_functions = ['getsecondmin']
	current_module = sys.modules[__name__]
	methods = current_module.__dict__
	fxs = [ func for name,func in methods.items() if not name in excluded_functions and re.match( r'^get.*',name) ]
	aspects.with_wrap(iterative_broadcast, *fxs)
