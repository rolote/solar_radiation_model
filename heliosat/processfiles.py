#!/usr/bin/env python

import glob
from datetime import datetime
from config import Config

def getlistpath(domain, year, month):
	return Config.DATA_ROOT_MOUNT + 'h5files/' + domain + '/' + str(year) + "/" + str(month).zfill(2)

def listmonth(domain, year, month):
	return glob.glob(getlistpath(domain, year, month) + '/*.h5')

def getdatetime(filename):
	m = (filename.split('-')[-3]).split('.')[0]
	return datetime.strptime(m, "%Y%m%d%H%M%S")
