import numpy as np

def pixels_from_coordinates(lat, lon, max_y, max_x):
	x = np.zeros(lon.shape)
	y = np.zeros(lat.shape)
	x_ratio = max_x/360.
	y_ratio = max_y/180.
	x = (lon + 180.) * x_ratio
	y = (lat + 90.) * y_ratio
	return x, y

def transform_data(data, x, y):
	result = np.zeros(x.shape)
	e_x = np.round(x)
	e_y = np.round(y)
	for (i,j), v in np.ndenumerate(e_x):
		tmp = data[int(e_y[i,j]),int(e_x[i,j])]
		result[i,j] = tmp if tmp >= 0 else 0
	ds = None
	return result