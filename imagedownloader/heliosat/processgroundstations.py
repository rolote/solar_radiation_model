#!/usr/bin/env python

import glob
from datetime import datetime
import numpy as np
import pylab as pl

def listallfiles():
	return glob.glob('/datos-medidos/*.dat')

def getinfo(filename):
	f = open(filename, 'r')
	info = {}
	for i in range(1,9):
		data = f.readline()
		data = data.split()
		info[data[0][1:-1]] = data[1]
	dates = [datetime.strptime(d,"%Y%m%d") for d in (filename.split("_")[1]).split("-")]
	info['range'] = dates
	info['filename'] = filename
	f.close()
	return info

def getstationsinformation():
	l = listallfiles()
	l.sort()
	return [getinfo(f) for f in l]
	
def inc(station, year):
	years = np.array([d.year for d in station['range']])
	return years.min() <= year and years.max() >= year

def getstations(year):
	res = []
	for s in getstationsinformation():
		if inc(s, year):
			res.append(s)
	return res

def getmeasuresinstations(year, month):
	places = []
	for station in getstations(year):
		dates, globalhi = np.loadtxt(station['filename'], skiprows=9, usecols=(0,1), delimiter="\t", converters={0: lambda x: pl.strpdate2num("%d/%m/%Y %H:%M")(x.decode("utf-8"))}, unpack=True)
		globalhi = globalhi / 0.36
		measures = []
		for i in range(dates.shape[0]):
			if pl.num2date(dates[i]).month == month:
				measures.append({'timestamp': dates[i], 'ghi': globalhi[i]})
		station['measures'] = measures
		places.append(station)
	return places
