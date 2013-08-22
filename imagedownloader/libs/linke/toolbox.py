import numpy as np
from osgeo import gdal
from libs.file import netcdf as nc
from libs.geometry import project as p
from datetime import datetime
import os
path = os.path.dirname(__file__)

def project_coordinates(lat, lon):
	ds = gdal.Open(path + "/tifs/01_longlat_wgs84.tif")
	return p.pixels_from_coordinates(lat, lon, ds.RasterYSize, ds.RasterXSize)

def cut_month(x, y, month):
	ds = gdal.Open(path + "/tifs/"+str(month).zfill(2)+"_longlat_wgs84.tif")
	linke = ds.ReadAsArray()
	result = p.transform_data(linke,x,y)
	return np.float32(result)/20.

def cut_projected(root):
	lat = nc.getvar(root, 'lat')
	lon = nc.getvar(root, 'lon')
	time = nc.getvar(root, 'time')
	months = list(set([ (datetime.fromtimestamp(int(t))).month for t in time ]))
	months_d = nc.getdim(root, 'monthing')
	months_cut = nc.getvar(root, 'months', 'i2', ('monthing',))
	linke = nc.getvar(root, 'linketurbidity', 'f4', ('monthing','northing','easting',),4)
	linke_x, linke_y = project_coordinates(lat[:], lon[:])
	months_cut[:] = np.array(list(months))
	for i in range(len(months)):
		linke[i] = cut_month(linke_x, linke_y, months[i])
	return linke[:], linke_x, linke_y