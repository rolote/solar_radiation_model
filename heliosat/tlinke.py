#!/usr/bin/env python

import numpy as np
from config import Config

months = {}

#~ def np_save_lat_lon(lat, lon, name):
    #~ np.savetxt(name+'/lat.np.gz', lat)
    #~ np.savetxt(name+'/lon.np.gz', lon)

def np_read_tlinke(name):
    return np.loadtxt(Config.DATA_ROOT_MOUNT + '/tlinke/'+name +'.asc', skiprows=6)

def gettlinke(dt, hrv):
	is_hrv = 'hrv' if hrv else 'nonhrv'
	file_name = is_hrv + '/' + str(dt.month).zfill(2) + '_andalucia_' + is_hrv + '_geos'
	try:
		months[file_name]
	except KeyError:
		months[file_name] = np_read_tlinke(file_name)
	return months[file_name]
