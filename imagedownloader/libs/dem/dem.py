from libs.console import *
from libs.file import netcdf as nc
from libs.geometry import project as p
import os
localpath = os.path.dirname(__file__)

source = "http://www.ngdc.noaa.gov/mgg/topo/DATATILES/elev/all10g.zip"
filename = source.split("/")[-1]
destiny = localpath + "/" + filename

def file_coordinates(f):
	letter = (f.split("/")[-1])[0]
	i = ord(letter) - ord('a')
	tail_x = i % 4
	tail_y = (i - tail_x) / 4
	px_x = tail_x * 10800
	shifts = [4800, 6000, 6000, 4800]
	px_y = sum(shifts[0:tail_y])
	return (px_y, px_x)

def initial_configuration():
	from libs.file.toolbox import download, unzip
	say("Downloading of "+filename+"... ")
	download(source,destiny)
	say("Unzipping "+filename+"... ")
	unzip(destiny, localpath+"/")

def merge_tails():
	import glob
	import numpy as np
	#from scipy import misc
	say("Merging all the tails in one netCDF file...")
	root, is_new = nc.open(localpath+ "/dem.nc")
	n_d = nc.getdim(root,'northing', 180 * 120) # 180 degrees * 120 px/degree
	n_e = nc.getdim(root,'easting', 360 * 120) # 360 degrees * 120 px/degree
	data = nc.getvar(root, 'dem', 'i2', ('northing','easting',))
	files = glob.glob(localpath + "/all10/all10/*10g")
	tails = [[file_coordinates(f),f] for f in files]
	for t, f in tails:
		print t, f
		tmp = np.fromfile(f,np.int16)
		dynamic = tmp.shape[0]/10800
		tmp = tmp.reshape(dynamic,10800)
		#misc.imsave(f+'.png',tmp)
		data[t[0]:t[0]+dynamic,t[1]:t[1]+10800] = tmp
	nc.close(root)

if not os.path.exists(destiny):
	initial_configuration()
if not os.path.exists(localpath+ "/dem.nc"):
	merge_tails()

def cut(lat,lon):
	import numpy as np
	root, is_new = nc.open(localpath+"/dem.nc")
	dem = nc.getvar(root, 'dem', 'i2', ('northing','easting',))
	x, y = p.pixels_from_coordinates(lat[:], lon[:], dem.shape[0], dem.shape[1])
	# In the transformation the 'y' dimension is twisted because the map is inverted.
	result = p.transform_data(dem,x,dem.shape[0] - y)
	nc.close(root)
	return result, x, y

def cut_projected(root):
	lat = nc.getvar(root, 'lat')
	lon = nc.getvar(root, 'lon')
	dem = nc.getvar(root, 'dem', 'i2', ('northing','easting',))
	dem[:], dem_x, dem_y = cut(lat, lon)
	return dem[:], dem_x, dem_y