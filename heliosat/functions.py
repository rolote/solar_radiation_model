#!/usr/bin/env python

from mpl_toolkits.basemap import Basemap
import pylab as pl
import domain_process as dp
import msg_navigation as msg
import numpy as np
from datetime import datetime
from matplotlib.dates import date2num

#import matplotlib.pyplot as plt
#from mpl_toolkits.axes_grid1 import AxesGrid

#~ X = dp.matrixtorgb(img_3, img_2, img_1)
#~ 
#~ fig = plt.figure()
#~ ax = fig.add_subplot(111)
#~ ax.imshow(X)
#~ 
#~ numrows, numcols = X.shape
#~ def format_coord(x, y):
    #~ col = int(x+0.5)
    #~ row = int(y+0.5)
    #~ if col>=0 and col<numcols and row>=0 and row<numrows:
        #~ z = X[row,col]
        #~ return 'x=%1.4f, y=%1.4f, z=%1.4f'%(x, y, z)
    #~ else:
        #~ return 'x=%1.4f, y=%1.4f'%(x, y)
#~ ax.format_coord = format_coord
#~ plt.draw()
#~ plt.savefig("anda_1_plt.png")

def drawmap(lat,lon,img,i):
	pl.ion()
	pl.figure(i)
	m = Basemap(projection='geos',lon_0=msg.SUB_LON,llcrnrlon=dp.minlon,llcrnrlat=dp.minlat,urcrnrlon=dp.maxlon,urcrnrlat=dp.maxlat)
	X, Y = m(lon, lat)
	cm = m.pcolormesh(X,Y,img,cmap='gist_gray')
	pl.colorbar(cm)
	pl.show()

def getjulianday(dt):
	if np.iterable(dt) == 0:
		return dt.timetuple()[7]
	else:
		return np.array([ getjulianday(d) for d in dt])

def gettotaldays(dt):
	if np.iterable(dt) == 0:
		return getjulianday(datetime(dt.year,12,31))
	else:
		return np.array([ gettotaldays(d) for d in dt])

def getdailyangle(julianday, totaldays):
	return 2 * np.pi * (julianday -1) / totaldays

def getexcentricity(gamma):
	return 1.000110 + 0.034221 * np.cos(gamma) + 0.001280 * np.sin(gamma) + 0.000719 * np.cos(2 * gamma) + 0.000077 * np.sin(2 * gamma)

def getdeclination(gamma):
	return 0.006918 - 0.399912 * np.cos(gamma) + 0.070257 * np.sin(gamma) - 0.006758 * np.cos(2 * gamma) + 0.000907 * np.sin(2 * gamma) - 0.002697 * np.cos(3 * gamma) + 0.00148 * np.sin(3 * gamma)

def gettimeequation(gamma):
	return (0.000075 + 0.001868 * np.cos(gamma) - 0.032077 * np.sin(gamma) - 0.014615 * np.cos(2 * gamma) - 0.040849 * np.sin(2 * gamma)) * (12 /np.pi)

def getdecimalhour(dt):
	return dt.hour + dt.minute/60.0 + dt.second/3600.0

def gettsthour(hour, d_ref, d, timeequation):
	return hour - (d_ref - d) * (12 / np.pi) + timeequation

def gethourlyangle(tst_hour):
	return (tst_hour - 12) * np.pi / 12

def getzenitangle(declination, latitude, hourlyangle):
	return np.arccos(np.sin(declination) * np.sin(latitude) + np.cos(declination) * np.cos(latitude) * np.cos(hourlyangle))

def getelevation(zenitangle):
	return (np.pi / 2) - zenitangle


def getcorrectedelevation(elevation):
	return elevation + 0.061359*((0.1594 + 1.1230*elevation + 0.065656 * np.power(elevation,2))/(1+ 28.9344 * elevation + 277.3971 * np.power(elevation,2)))

def getopticalpath(correctedelevation, terrainheight):
	#8434.5 mts
	return (np.exp(-terrainheight/8434.5)) / (np.sin(correctedelevation) + 0.50572 * np.power(np.rad2deg(correctedelevation)+6.07995, -1.6364))

def getopticaldepth(opticalpath):
	tmp = np.zeros(opticalpath.shape) + 1.0
	highslopebeam = opticalpath <= 20
	lowslopebeam = opticalpath > 20
	tmp[highslopebeam] = 1/(6.625928 + 1.92969 * opticalpath[highslopebeam] - 0.170073 * np.power(opticalpath[highslopebeam],2) + 0.011517 * np.power(opticalpath[highslopebeam],3) - 0.000285 * np.power(opticalpath[highslopebeam],4))
	tmp[lowslopebeam] = 1/(10.4 + 0.718 * opticalpath[lowslopebeam])
	return tmp
	#return np.where(opticalpath > 20, \
	#	1/(10.4 + 0.718 * opticalpath), \
	#	1/(6.625928 + 1.92969 * opticalpath - 0.170073 * np.power(opticalpath,2) + 0.011517 * np.power(opticalpath,3) - 0.000285 * np.power(opticalpath,4)))

def getbeamtransmission(linketurbidity, opticalpath, opticaldepth):
	return np.exp(-0.8662 * linketurbidity * opticalpath * opticaldepth)

def gethorizontalirradiance(extraterrestrialirradiance, excentricity, zenitangle):
	return extraterrestrialirradiance * excentricity * np.cos(zenitangle)

def getbeamirradiance(extraterrestrialirradiance, excentricity, zenitangle, solarelevation, linketurbidity, terrainheight):
	correctedsolarelevation = getcorrectedelevation(solarelevation)
	opticalpath = getopticalpath(correctedsolarelevation, terrainheight)
	opticaldepth = getopticaldepth(opticalpath)
	return gethorizontalirradiance(extraterrestrialirradiance, excentricity, zenitangle) * getbeamtransmission(linketurbidity, opticalpath, opticaldepth)



def getzenitdiffusetransmitance(linketurbidity):
	return -0.015843 + 0.030543 * linketurbidity + 0.0003797 * np.power(linketurbidity,2)

def getangularcorrection(solarelevation, linketurbidity):
	a0 = 0.26463 - 0.061581 * linketurbidity + 0.0031408 * np.power(linketurbidity,2)
	a1 = 2.0402 - 0.018945 * linketurbidity + 0.011161 * np.power(linketurbidity,2)
	a2 = -1.3025 - 0.039231 * linketurbidity + 0.0085079 * np.power(linketurbidity,2)
	zenitdiffusetransmitance = getzenitdiffusetransmitance(linketurbidity)
	c = a0*zenitdiffusetransmitance < 0.002
	a0[c] = 0.002 / zenitdiffusetransmitance[c]
	return a0 + a1 * np.sin(solarelevation) + a2 * np.power(np.sin(solarelevation),2)

def getdiffusetransmitance(linketurbidity, solarelevation):
	return getzenitdiffusetransmitance(linketurbidity) * getangularcorrection(solarelevation, linketurbidity)

def gettransmitance(linketurbidity, opticalpath, opticaldepth, solarelevation):
	return getbeamtransmission(linketurbidity, opticalpath, opticaldepth) + getdiffusetransmitance(linketurbidity, solarelevation)

def getdiffuseirradiance(extraterrestrialirradiance, excentricity, solarelevation, linketurbidity):
	return extraterrestrialirradiance * excentricity * getdiffusetransmitance(linketurbidity, solarelevation)

def getglobalirradiance(beamirradiance, diffuseirradiance):
	return beamirradiance + diffuseirradiance

def getalbedo(radiance, totalirradiance, excentricity, zenitangle):
	return (np.pi * radiance)/(totalirradiance * excentricity * np.cos(zenitangle))

def getsatellitalzenitangle(latitude, longitude):
	rpol = 6356.5838
	req = 6378.1690
	h = 42164.0
	re = rpol /(np.sqrt(1-(req**2 - rpol**2)/(req**2)*np.power(np.cos(latitude),2)))
	lat_cos = re * np.cos(latitude)
	lon_diff = np.deg2rad(np.rad2deg(longitude) - msg.SUB_LON)
	r1 = h - lat_cos * np.cos(lon_diff)
	r2 = - lat_cos * np.sin(lon_diff)
	r3 = re * np.sin(latitude)
	rs = np.sqrt(r1**2 + r2**2 + r3**2)
	return np.pi - np.arccos((h**2 - re**2 - rs**2)/(-2 * re * rs))

def getatmosphericradiance(extraterrestrialirradiance, i0met,diffuseclearsky, satellitalzenitangle):
	anglerelation = np.power((0.5 / np.cos(satellitalzenitangle)),0.8)
	return (i0met * diffuseclearsky * anglerelation) /  (np.pi * extraterrestrialirradiance)


def getdifferentialalbedo(firstalbedo, secondalbedo, t_earth, t_sat):
	return (firstalbedo - secondalbedo) / (t_earth * t_sat)


def getapparentalbedo(observedalbedo, atmosphericalbedo, t_earth, t_sat):
	apparentalbedo = getdifferentialalbedo(observedalbedo,atmosphericalbedo,t_earth,t_sat)
	apparentalbedo[apparentalbedo < 0] = 0.0
	return apparentalbedo

def geteffectivealbedo(solarangle):
	return 0.78 - 0.13 * (1-np.exp(-4 * np.power(np.cos(solarangle),5)))

def getcloudalbedo(effectivealbedo, atmosphericalbedo, t_earth, t_sat):
	cloudalbedo = getdifferentialalbedo(effectivealbedo, atmosphericalbedo, t_earth, t_sat)
	cloudalbedo[cloudalbedo < 0.2] = 0.2
	effectiveproportion = 2.24 * effectivealbedo
	cloudalbedo[cloudalbedo > effectiveproportion] = effectiveproportion[cloudalbedo > effectiveproportion]
	return cloudalbedo

def getslots(dt):
	return np.int(np.round(getdecimalhour(dt) * 4))

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

def getsolarelevation(dt,lat,omega):
	declination = getdeclination(getdailyangle(getjulianday(dt),gettotaldays(dt)))
	lat_r = np.array([ lat for d in declination ])
	declination_r = np.array([ np.zeros(lat.shape) + d for d in declination ])
	return np.arcsin(np.sin(declination_r) * np.sin(lat_r) + np.cos(declination_r) * np.sin(lat_r) * np.cos(omega))

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
