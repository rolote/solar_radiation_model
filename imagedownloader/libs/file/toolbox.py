#!/usr/bin/env python2.7

import sys
import numpy as np
import netcdf as nc
from libs.console import *
from libs.linke import toolbox as linke
from datetime import datetime

def cut(filename, i_from, i_to):
	img_from = int(i_from)
	img_to = int(i_to)
	img_range = img_to - img_from
	root, is_new = nc.open(filename)
	lat = nc.getvar(root, 'lat')
	lon = nc.getvar(root, 'lon')
	data = nc.getvar(root, 'data')
	time = nc.getvar(root, 'time')
	root_cut, is_new = nc.open('cut.' + filename)
	timing_d = nc.getdim(root_cut, 'timing', img_range)
	northing_d = nc.getdim(root_cut, 'northing', data.shape[1])
	easting_d = nc.getdim(root_cut, 'easting', data.shape[2])
	lat_cut = nc.getvar(root_cut, 'lat', 'f4', ('northing','easting',),4)
	lon_cut = nc.getvar(root_cut, 'lon', 'f4', ('northing','easting',),4)
	lat_cut[:] = lat[:]
	lon_cut[:] = lon[:]
	data_cut = nc.getvar(root_cut, 'data', 'f4', ('timing','northing','easting',),4)
	time_cut = nc.getvar(root_cut, 'time', 'f4', ('timing',),4)
	for i in range(img_range):
		data_cut[i] = data[img_from + i]
		time_cut[i] = time[img_from + i]
	nc.close(root)
	nc.close(root_cut)

def search_position(station, lat, lon):
	numrows = lat.shape[0]
	numcols = lat.shape[1]
	# This is valid because latitude and longitude values are all negative for Argentina
	# The matrix limits should be beyond stations coordinates (eg 5 pixels latitude and 5 pixels longitude)
	deltax=numrows/2-1
	deltay=numcols/2-1
	x = deltax
	y = deltay
	count = 0
	limit = int(np.ceil(np.log(max(numrows,numcols))/np.log(2)))
	for k in range(1,limit):
	    count = count + 2
	    if lat[x,y+deltay/2] > station[0]:  # +deltay/2, considering lat curvature
	        x = x + deltax
	    else:
	        x = x - deltax
	#    print "coord x: (",x,",",y,")"
	    #print x,y,";"
	    if lon[x-deltax/2,y] > station[1]:  # -deltax/2, considering long curvature
	        y = y - deltay
	    else:
	        y = y + deltay
	#    print "coord y: (",x,",",y,")"
	    #print x,y,";"
	    deltax = deltax/2
	    deltay = deltay/2
	while (lat[x,y] > station[0] or lon[x,y] > station[1]):
	    while (lat[x,y] > station[0]):
	        count = count + 1
	        x = x+1
	    while (lon[x,y] > station[1]):
	        count = count + 1
	        y = y-1
	return x, y

def cut_positions(filename, blurred, *positions):
	blurred = int(blurred)
	pos = eval("".join(positions))
	root, is_new = nc.open(filename)
	lat = nc.getvar(root, 'lat')
	lon = nc.getvar(root, 'lon')
	data = nc.getvar(root, 'data')
	time = nc.getvar(root, 'time')
	root_cut, is_new = nc.open('cut_positions.' + filename)
	timing_d = nc.getdim(root_cut, 'timing', data.shape[0])
	northing_d = nc.getdim(root_cut, 'northing', len(pos))
	easting_d = nc.getdim(root_cut, 'easting', 2)
	lat_cut = nc.getvar(root_cut, 'lat', 'f4', ('northing','easting',),4)
	lon_cut = nc.getvar(root_cut, 'lon', 'f4', ('northing','easting',),4)
	data_cut = nc.getvar(root_cut, 'data', 'f4', ('timing','northing','easting',),4)
	time_cut = nc.getvar(root_cut, 'time', 'f4', ('timing',),4)
	time_cut[:] = time[:]
	for i in range(len(pos)):
		show("\rCutting data: processing position %d / %d " % (i+1, len(pos)))
		x, y = search_position(pos[i], lat, lon)
		lat_cut[i,0] = lat[x,y]
		lon_cut[i,0] = lon[x,y]
		data_cut[:,i,0] = np.apply_over_axes(np.mean, data[:,x-blurred:x+blurred,y-blurred:y+blurred], axes=[1,2])
		lat_cut[i,1], lon_cut[i,1], data_cut[:,i,1] = lat_cut[i,0], lon_cut[i,0], data_cut[:,i,0]
	nc.close(root)
	nc.close(root_cut)

def cut_projected_linke(filename):
	root, is_new = nc.open(filename)
	lat = nc.getvar(root, 'lat')
	lon = nc.getvar(root, 'lon')
	data = nc.getvar(root, 'data')
	time = nc.getvar(root, 'time')
	root_cut, is_new = nc.open('wlinke.' + filename)
	timing_d = nc.getdim(root_cut, 'timing', data.shape[0])
	northing_d = nc.getdim(root_cut, 'northing', data.shape[1])
	easting_d = nc.getdim(root_cut, 'easting', data.shape[2])
	lat_cut = nc.getvar(root_cut, 'lat', 'f4', ('northing','easting',),4)
	lon_cut = nc.getvar(root_cut, 'lon', 'f4', ('northing','easting',),4)
	data_cut = nc.getvar(root_cut, 'data', 'f4', ('timing','northing','easting',),4)
	time_cut = nc.getvar(root_cut, 'time', 'f4', ('timing',),4)
	lat_cut[:] = lat[:]
	lon_cut[:] = lon[:]
	data_cut[:] = data[:]
	time_cut[:] = time[:]
	linke.cut_projected(root_cut)
	nc.close(root)
	nc.close(root_cut)

def cut_projected_terrain(filename):
	from libs.dem import dem
	root, is_new = nc.open(filename)
	lat = nc.getvar(root, 'lat')
	lon = nc.getvar(root, 'lon')
	data = nc.getvar(root, 'data')
	time = nc.getvar(root, 'time')
	root_cut, is_new = nc.open('wterrain.' + filename)
	timing_d = nc.getdim(root_cut, 'timing', data.shape[0])
	northing_d = nc.getdim(root_cut, 'northing', data.shape[1])
	easting_d = nc.getdim(root_cut, 'easting', data.shape[2])
	lat_cut = nc.getvar(root_cut, 'lat', 'f4', ('northing','easting',),4)
	lon_cut = nc.getvar(root_cut, 'lon', 'f4', ('northing','easting',),4)
	data_cut = nc.getvar(root_cut, 'data', 'f4', ('timing','northing','easting',),4)
	time_cut = nc.getvar(root_cut, 'time', 'f4', ('timing',),4)
	lat_cut[:] = lat[:]
	lon_cut[:] = lon[:]
	data_cut[:] = data[:]
	time_cut[:] = time[:]
	dem.cut_projected(root_cut)
	nc.close(root)
	nc.close(root_cut)

def chunk_report(bytes_so_far, chunk_size, total_size):
	percent = float(bytes_so_far) / total_size
	percent = round(percent*100, 2)
	replace = ("Downloaded %d of %d bytes (%0.2f%%)" % (bytes_so_far, total_size, percent)).ljust(80)
	say("\r"+replace)
	if bytes_so_far >= total_size:
		sys.stdout.write('\n')

def chunk_download(response, destiny, chunk_size=8192, report_hook=None):
	total_size = response.info().getheader('Content-Length').strip()
	total_size = int(total_size)
	bytes_so_far = 0
	with open(destiny, 'w') as local:
		while 1:
			chunk = response.read(chunk_size)
			bytes_so_far += len(chunk)

			if not chunk:
				break
			local.write(chunk)
			if report_hook:
				report_hook(bytes_so_far, chunk_size, total_size)
	return bytes_so_far

def download(source, destiny):
	import urllib2
	remote = urllib2.urlopen(source)
	meta = remote.info()
	filename = source.split("/")[-1]
	say("Downloading of "+filename+"... ")
	chunk_download(remote, destiny, report_hook=chunk_report)

def unzip(source_filename, dest_dir):
	import zipfile,os.path
	with zipfile.ZipFile(source_filename) as zf:
		for member in zf.infolist():
			# Path traversal defense copied from
			# http://hg.python.org/cpython/file/tip/Lib/http/server.py#l789
			words = member.filename.split('/')
			path = dest_dir
			for word in words[:-1]:
				drive, word = os.path.splitdrive(word)
				head, word = os.path.split(word)
				if word in (os.curdir, os.pardir, ''): continue
				path = os.path.join(path, word)
			zf.extract(member, path)

if __name__=="__main__":
	functions = { 'cut' : cut,
		 'cut_positions' : cut_positions,
		 'get_tlinke': cut_projected_linke,
		 'get_terrain' : cut_projected_terrain,
		 'download': download,
		 'unzip': unzip }
	functions[sys.argv[1]](*(sys.argv[2:]))
	show("\nReady.\n")

#station = [-34.5880556, -59.0627778] # Lujan
#station = [-36.541704, -63.990947] # Anguil
#station = [-31.84894, -60.536117] # Parana
#station = [-37.763199, -58.297519] # Balcarce
#station = [-33.944332, -60.568668] # Pergamino
#station = [-32.568348, -62.082349] # MarcosJuarez
#station = [-36.766174, -59.881312] # Azul

# Lujan, Anguil, Parana, Balcarce, Pergamino, Marcos Juarez, Azul
#cut_positions goes13.all.BAND_01.nc 0 [[-34.5880556, -59.0627778],[-36.541704, -63.990947],[-31.84894, -60.536117],[-37.763199, -58.297519],[-33.944332, -60.568668],[-32.568348, -62.082349],[-36.766174, -59.881312]]
