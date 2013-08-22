#!/usr/bin/env python

import numpy as np
import msg_navigation
import sys
import pickle
from netCDF4 import Dataset
from pyproj import Proj
import png
from config import Config

DOMAIN = 'sp'

R_SIZE, C_SIZE = 3712, 3712
R_HRVSIZE, C_HRVSIZE = R_SIZE * 3, C_SIZE * 3

ULLAT, ULLON = 3262, 2122
URLAT, URLON = 3013, 1723

ULLAT_HRV, ULLON_HRV = 9786 -4, 6366 -4 
URLAT_HRV, URLON_HRV = 9039 -6, 5169 -4

def generate_lat_lon(shape, hrv):
    columns, rows = np.meshgrid(np.arange(shape.shape[0],0,-1), np.arange(shape.shape[1],0,-1))
    return msg_navigation.coord2geo(columns, rows, hrv)

def nc_save_lat_lon(lat, lon, name):
    rootgrp = Dataset(name + '.nc','w',format='NETCDF4')
    d_north = rootgrp.createDimension('northing', lat.shape[0])
    d_east = rootgrp.createDimension('easting', lat.shape[1])
    v_lat = rootgrp.createVariable('latitudes', 'f4', ('northing','easting',), zlib=True, least_significant_digit=4)
    v_lon = rootgrp.createVariable('longitudes', 'f4', ('northing','easting',), zlib=True, least_significant_digit=4)
    v_lat[:] = lat
    v_lon[:] = lon
    rootgrp.close()

def nc_read_lat_lon(name):
    rootgrp = Dataset(name + '.nc','r')
    lat = np.array(rootgrp.variables['latitudes'][:])
    lon = np.array(rootgrp.variables['longitudes'][:])
    rootgrp.close()
    return lat, lon

def px_save_lat_lon(lat, lon, name):
    pickle.dump(lat, open(name+'/lat.pkl.gz','wb'))
    pickle.dump(lon, open(name+'/lon.pkl.gz','wb'))

def px_read_lat_lon(name):
    lat = pickle.load(open(name+'/lat.pkl.gz','rb'))
    lon = pickle.load(open(name+'/lon.pkl.gz','rb'))
    return lat, lon

def np_save_lat_lon(lat, lon, name):
    np.savetxt(name+'/lat.np.gz', lat)
    np.savetxt(name+'/lon.np.gz', lon)

def np_read_lat_lon(name):
    lat = np.loadtxt(name +'/lat.np.gz')
    lon = np.loadtxt(name +'/lon.np.gz')
    return lat, lon

#sm = np.zeros([3712,3712])
#sm_hrv = np.zeros([11136,11136])
#lat, lon = generate_lat_lon(sm, False)
#nc_save_lat_lon(lat, lon, Config.DATA_ROOT_MOUNT + '/domain/root')
latitude_sat, longitude_sat = nc_read_lat_lon(Config.DATA_ROOT_MOUNT + '/domain/root')
#latitude_hrvsat, longitude_hrvsat = nc_read_lat_lon(Config.DATA_ROOT_MOUNT + '/domain/roothrv')

def getsubmatrix(matrix, imin, imax, jmin, jmax):
	return matrix[imin:imax+1,jmin:jmax+1]

def getdom_img(hrv):
	if hrv:
		imin, imax, jmin, jmax = R_HRVSIZE - ULLAT_HRV, R_HRVSIZE - URLAT_HRV, C_HRVSIZE - ULLON_HRV, C_HRVSIZE - URLON_HRV 
	else:
		imin, imax, jmin, jmax = R_SIZE    - ULLAT,     R_SIZE    - URLAT,     C_SIZE    - ULLON,     C_SIZE    - URLON
	return imin,imax,jmin,jmax

def getsubmatrix_img(matrix, hrv):
	imin, imax, jmin, jmax = getdom_img(hrv)
	return getsubmatrix(matrix, imin, imax, jmin, jmax)

latitude_img, longitude_img = getsubmatrix_img(latitude_sat, False), getsubmatrix_img(longitude_sat, False)
#latitude_hrvimg, longitude_hrvimg = getsubmatrix_img(latitude_hrvsat, True), getsubmatrix_img(longitude_hrvsat, True)

latitude_dom, longitude_dom = [],[]
x_sat, y_sat = [],[]

p = Proj(proj='geos', lon_0=0, h= 35786000, y_0 = -3562253.66275, R=6370997.0, x_0= 690972.754387, units='m') 

def latlon2geos(lat,lon):
	return p(lon,lat)

def geo2latlon(x,y):
	return p(x,y,inverse=True)

def getposxy(X, Y, lat, lon):
	x, y = latlon2geos(lat,lon)
	c = np.argmin(np.cumsum(np.abs(X - x), 0)[X.shape[0] - 1])
	l = np.argmin(np.cumsum(np.abs(Y - y), 1)[:, Y.shape[1] -1])
	return l,c

def getpos(lat,lon,hrv):
	latitude_dom, longitude_dom = getlatlon(hrv)
	x_sat, y_sat = latlon2geos(latitude_dom, longitude_dom)
	return getposxy( x_sat, y_sat, lat, lon)

#x, y = getpos(40.0,-10.0, True)

minlat, minlon = 35.47 , -7.93
maxlat, maxlon = 39.25 , -1.15

def getdom_subimg(latitude, longitude):
	X, Y = latlon2geos(latitude,longitude)
	xmax, ymin = getposxy(X, Y, minlat, minlon)
	xmin, ymax = getposxy(X, Y, maxlat, maxlon)
	return xmin, xmax, ymin, ymax

def getlatlon(hrv):
	if hrv:
		xmin, xmax, ymin, ymax = getdom_subimg(latitude_hrvimg, longitude_hrvimg)
		return getsubmatrix(latitude_hrvimg,xmin,xmax,ymin,ymax), getsubmatrix(longitude_hrvimg,xmin,xmax,ymin,ymax)
	else:
		xmin, xmax, ymin, ymax = getdom_subimg(latitude_img, longitude_img)
		return getsubmatrix(latitude_img,xmin,xmax,ymin,ymax), getsubmatrix(longitude_img,xmin,xmax,ymin,ymax)

def getsubimg(img, hrv):
	if (hrv):
		imin, imax, jmin, jmax = getdom_subimg(latitude_hrvimg, longitude_hrvimg) 
	else:
		imin, imax, jmin, jmax = getdom_subimg(latitude_img, longitude_img)
	return getsubmatrix(img, imin, imax, jmin, jmax)

def getpng(matrix,name):
	f = open(name, 'wb')
	w = png.Writer(matrix.shape[1], matrix.shape[0], greyscale=True)
	w.write(f, matrix)
	f.close()

def matrixtogrey(m):
	the_min = np.amin(m)
	return 255 - np.trunc((m - the_min)/(np.amax(m) - the_min) * 255)

def matrixtorgb(red,green,blue):
	the_unit = np.amax((red,green,blue)) / 256
	r = (red / the_unit).astype('int') * (2**16)
	g = (green / the_unit).astype('int') * (2**8)
	b = (blue / the_unit).astype('int')
	return r | g | b
