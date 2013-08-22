import numpy as np

def get_soil_mask(near_ir_data,limit=7200)
	data = np.percentile(near_ir_data,90,0)
	data[data<=limit] = 0
	data[data>limit] = 1
	return data
