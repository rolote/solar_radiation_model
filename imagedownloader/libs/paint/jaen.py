#!/usr/bin/env python

from mpl_toolkits.basemap import Basemap
import pylab as pl
import png
import numpy as np

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

def drawmap(lat,lon, sub_lon,img,i):
	pl.ion()
	pl.figure(i)
	m = Basemap(projection='geos',lon_0=sub_lon,llcrnrlon=-90,llcrnrlat=-90,urcrnrlon=-30,urcrnrlat=-30)
	X, Y = m(lon, lat)
	cm = m.pcolormesh(X,Y,img,cmap='gist_gray')
	pl.colorbar(cm)
	pl.show()

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