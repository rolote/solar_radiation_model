from netCDF4 import Dataset
import os

def open(filename):
	is_new = not os.path.exists(filename)
	try:
		root = (Dataset(filename, mode='w',format='NETCDF4') if is_new else Dataset(filename,mode='a'))
	except:
		root = Dataset(filename, mode='r')
	return root, is_new

def getdim(root,name,size=None):
	if not name in root.dimensions:
		d = root.createDimension(name, size)
	else:
		d = root.dimensions[name]
	return d

def getvar(root, name, vtype='f4', dimensions=(), digits=0):
	try:
		v = root.variables[name]
	except KeyError:
		if digits > 0:
			v = root.createVariable(name, vtype, dimensions, zlib=True, least_significant_digit=digits)
		else:
			v = root.createVariable(name, vtype, dimensions, zlib=True)
	return v

def sync(root):
	return root.sync()

def close(root):
	return root.close()
