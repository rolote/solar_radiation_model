#!/usr/bin/env python

import numpy as np
import sys

SAT_HEIGHT = 42164.0 # distance from Earth centre to satellite
SUB_LON = 0.0 # longitude of sub-satellite point in radiant
CFAC_NONHRV = -781648343 # column scaling coefficients (non hi-resolution)
LFAC_NONHRV = -781648343 # line scaling coefficients (non hi-resolution)
COFF_NONHRV = 1856 # column offset coefficients (non hi-resolution)
LOFF_NONHRV = 1856 # line offset coefficients (non hi-resolution)
CFAC_HRV = -2344945030 # column scaling coefficients (hi-resolution)
LFAC_HRV = -2344945030 # line scaling coefficients (hi-resolution)
COFF_HRV = 5566 # column offset coefficients (hi-resolution)
LOFF_HRV = 5566 # line offset coefficients (hi-resolution)

def coord2geo(column, row, hrv):
	sys.stdout.write('Obtaining latitude and longitude...\n')
	sys.stdout.flush()
	if hrv:
		cfac = CFAC_HRV
		coff = COFF_HRV
		lfac = LFAC_HRV
		loff = LOFF_HRV
	else:
		cfac = CFAC_NONHRV
		coff = COFF_NONHRV
		lfac = LFAC_NONHRV
		loff = LOFF_NONHRV
	
	sys.stdout.write('Obtaining middle''s coodinates...\n')
	sys.stdout.flush()
	x = ((column - coff) * np.power(2,16)) / float(cfac)
	y = ((row - loff) * np.power(2,16)) / float(lfac)
	
	sys.stdout.write('Preparing to obtain coefficients to projection process...\n')
	sys.stdout.flush()
	sat_cos = np.cos(x) * np.cos(y)
	sat_cos_xy = float(SAT_HEIGHT) * sat_cos
	sat_k = np.power(np.cos(y),2) + 1.006803 * np.power(np.sin(y),2)
	
	sys.stdout.write('Obtaining coefficients to projection process...\n')
	sys.stdout.flush()
	sa = np.power(sat_cos_xy,2) - sat_k * 1737121856
	sa = np.where(sa < 0.0, np.nan, sa)
	sd = np.sqrt(sa)
	sn = (sat_cos_xy - sd) / sat_k
	s1 = 42164 - sn * sat_cos
	s2 = sn * np.sin(x) * np.cos(y)
	s3 = -sn * np.sin(y)
	sxy = np.sqrt(np.power(s1,2) + np.power(s2,2))
	
	sys.stdout.write('Obtaining longitudes...\n')
	sys.stdout.flush()
	lon = np.arctan(s2/s1) + SUB_LON
	
	sys.stdout.write('Obtaining latitudes...\n')
	sys.stdout.flush()
	lat = np.arctan(1.006803 * s3 / sxy)
	return np.rad2deg((lat, lon))
	
def geo2coord(lat, lon, hrv):
	sys.stdout.write('Obtaining row and column...\n')
	sys.stdout.flush()
	if hrv:
		cfac = CFAC_HRV
		coff = COFF_HRV
		lfac = LFAC_HRV
		loff = LOFF_HRV
	else:
		cfac = CFAC_NONHRV
		coff = COFF_NONHRV
		lfac = LFAC_NONHRV
		loff = LOFF_NONHRV
	# -->
	
	sys.stdout.write('Obtaining middle''s coodinates...\n')
	sys.stdout.flush()
	x = ((column - coff) * np.power(2,16)) / float(cfac)
	y = ((row - loff) * np.power(2,16)) / float(lfac)
	
	sys.stdout.write('Preparing to obtain coefficients to projection process...\n')
	sys.stdout.flush()
	sat_cos = np.cos(x) * np.cos(y)
	sat_cos_xy = float(SAT_HEIGHT) * sat_cos
	sat_k = np.power(np.cos(y),2) + 1.006803 * np.power(np.sin(y),2)
	
	sys.stdout.write('Obtaining coefficients to projection process...\n')
	sys.stdout.flush()
	sa = np.power(sat_cos_xy,2) - sat_k * 1737121856
	sa = np.where(sa < 0.0, np.nan, sa)
	sd = np.sqrt(sa)
	sn = (sat_cos_xy - sd) / sat_k
	s1 = 42164 - sn * sat_cos
	s2 = sn * np.sin(x) * np.cos(y)
	s3 = -sn * np.sin(y)
	sxy = np.sqrt(np.power(s1,2) + np.power(s2,2))
	
	sys.stdout.write('Obtaining longitudes...\n')
	sys.stdout.flush()
	lon = np.arctan(s2/s1) + SUB_LON
	
	sys.stdout.write('Obtaining latitudes...\n')
	sys.stdout.flush()
	lat = np.arctan(1.006803 * s3 / sxy)
	return np.rad2deg((lat, lon))
