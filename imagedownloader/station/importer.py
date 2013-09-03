import sys
sys.path.append("../")
from datetime import datetime, timedelta
from xlrd import open_workbook
import csv
from libs.file import netcdf as nc
from libs.geometry import jaen as geo
import numpy as np

def rows2csv(rows, filename):
	with open(filename, 'wb') as csvfile:
		spamwriter = csv.writer(csvfile, quoting=csv.QUOTE_MINIMAL)
		for i in range(len(rows)):
			spamwriter.writerow(rows[i])
			
def mvolt_to_watt(mvolt):
	mvolt_per_kwatts_m2 = 8.48
	return (mvolt / mvolt_per_kwatts_m2) * 1000

def rows2slots(rows, image_per_hour):
	resumed_slots = []
	old_slot = geo.getslots(rows[0][0],image_per_hour)
	seconds_in_slot = (rows[1][0] - rows[0][0]).total_seconds()
	mvolt = 0
	rows_by_slot = 0
	dt = rows[0][0]
	for r in rows:
		slot = geo.getslots(dt,image_per_hour)
		if not old_slot is slot:
			resumed_slots.append([slot, [dt, mvolt_to_watt((mvolt/rows_by_slot)/seconds_in_slot), rows_by_slot]])
			old_slot, rows_by_slot, mvolt = slot, 0, 0
		mvolt += r[1]
		rows_by_slot += 1
		dt = r[0]
	if not old_slot is slot:
		resumed_slots.append([slot, [dt, mvolt_to_watt((mvolt/rows_by_slot)/seconds_in_slot), rows_by_slot]])
		old_slot, rows_by_slot, mvolt = slot, 0, 0
	return resumed_slots

def rows2netcdf(rows, filename, index):
	root, is_new = nc.open(filename)
	if not is_new:
		measurements = nc.getvar(root, 'measurements', 'f4', ('timing','northing','easting'), 4)
		slots = nc.getvar(root, 'slots')
		times = [ datetime.fromtimestamp(int(t)) for t in nc.getvar(root, 'time') ]
		instant_radiation = rows2slots(rows,2)
		i_e = 0
		i_m = 0
		while i_e < len(times) and i_m < len(instant_radiation):
			#print i_e,"/", len(times) -1, " | ", i_m, "/", len(instant_radiation) - 1
			# When date estimated before date measured
			if times[i_e].date() < instant_radiation[i_m][1][0].date():
				i_e += 1
			# When date estimated after date measured
			elif times[i_e].date() > instant_radiation[i_m][1][0].date():
				i_m += 1
			else:
				if slots[i_e] < instant_radiation[i_m][0]:
					measurements[i_e, index,:] = np.array([-1, -1])
					i_e += 1
				elif slots[i_e] > instant_radiation[i_m][0]:
					i_m += 1
				else:
					value = instant_radiation[i_m][1][1]
					row_in_slot = instant_radiation[i_m][1][2]
					measurements[i_e, index,:] = np.array([value, value])
					i_e += 1
					i_m += 1
	days = [ t.date() for t in times ]
	nc.getdim(root, 'diarying')
	diary_error = nc.getvar(root, 'diaryerror', 'f4', ('diarying', 'northing', 'easting'))
	estimated = nc.getvar(root, 'globalradiation')[:]
	error_diff = nc.getvar(root, 'errordiff', 'f4', ('timing','northing','easting'), 4)
	error = nc.getvar(root, 'error', 'f4', ('timing','northing','easting'), 4)
	error_diff[:, index, :] = measurements[:,index,:] - estimated[:,index,:]
	error[:, index, :] = np.sqrt((error_diff[:, index, :])**2)
	print error_diff.shape
	nc.sync(root)
	for	i in range(len(days)):
		d = days[i].day
		print index, i, d, error_diff[i,index], diary_error[d, index]
		diary_error[d, index,:] += error_diff[i,index,:]
	diary_error[:, index,:] = np.sqrt((diary_error[:, index,:])**2)
	nc.close(root)

def get_val(sh,x,y):
	return sh.cell(y,x).value

filename = sys.argv[1]
i_sheet = int(sys.argv[2])
x_year = int(sys.argv[3])
x_julian = int(sys.argv[4])
x_timestamp = int(sys.argv[5])
utc_diff = int(sys.argv[6])
x_value = int(sys.argv[7])
y_from = int(sys.argv[8])
outputfilename = sys.argv[9]
output_index = int(sys.argv[10]) if len(sys.argv) > 10 else None

wb = open_workbook(filename)
sh = wb.sheets()[i_sheet]
rows = []
y = y_from
year, julian, time = get_val(sh,x_year,y), get_val(sh,x_julian,y), get_val(sh,x_timestamp,y)
while not(year == '' and julian == '' and time == ''):
	timestamp = datetime(int(year),1, 1) + timedelta(int(julian))
	time = str(int(time)).zfill(4)
	timestamp += timedelta(hours=int(time[0:2]), minutes = int(time[2:4]))
	delta =  timedelta(hours = abs(utc_diff))
	timestamp = (timestamp + delta if utc_diff < 0 else timestamp - delta)
	try:
		value = float(get_val(sh,x_value,y))
	except:
		value = 0
	rows.append([timestamp, value])
	y += 1
	year, julian, time = get_val(sh,x_year,y), get_val(sh,x_julian,y), get_val(sh,x_timestamp,y)
if output_index is None:
	rows2csv(rows, outputfilename)
else:
	rows2netcdf(rows,outputfilename,output_index)
