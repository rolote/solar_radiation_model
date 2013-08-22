import numpy as np
try:
	from pycuda.compiler import SourceModule
	import pycuda.gpuarray as gpuarray
	import pycuda.driver as cuda
	import pycuda.autoinit
	cuda_can_help = True
except ImportError: 
	cuda_can_help = False 

pi = np.pi
ma = np.ma

_pi = str(np.float32(pi))
_deg2rad_ratio = str(np.float32(pi / 180))
_rad2deg_ratio = str(np.float32(180 / pi))

def _gpu_exec(func, *matrixs):
	matrixs = [ np.matrix(m).astype(np.float32) for m in matrixs]
	matrixs_gpu = [ cuda.mem_alloc(m.nbytes) for m in matrixs ]
	for i in range(len(matrixs)):
		cuda.memcpy_htod(matrixs_gpu[i], matrixs[i])
	m_shapes = [ list(m.shape) for m in matrixs ]
	for m_s in m_shapes:
		while len(m_s) < 3:
			m_s.insert(0,1);
	func(*matrixs_gpu, grid=tuple(m_shapes[0][1:3]), block=tuple([m_shapes[0][0],1,1]))
	result = np.empty_like(matrixs[0])
	cuda.memcpy_dtoh(result, matrixs_gpu[0])
	for m in matrixs_gpu:
		m.free()
	return result

def deg2rad(deg):
	return np.deg2rad(deg)

def rad2deg(rad):
	return np.rad2deg(rad)

def sin(rad):
	return np.sin(rad)

def cos(rad):
	return np.cos(rad)

def arccos(x):
	return np.arccos(x)

def arcsin(x):
	return np.arcsin(x)

def sqrt(x):
	return np.sqrt(x)

def power(x, power):
	return np.power(x, power)

def exp(x):
	return np.exp(x)

def int(x):
	return np.int(x)

def trunc(x):
	return np.trunc(x)

def round(x):
	return np.round(x)

def iterable(x):
	return np.iterable(x)

def zeros(shape):
	return np.zeros(shape)

def zeros_like(x):
	return np.zeros_like(x)

def array(x):
	return np.array(x)

def amin(*args, **kwargs):
	return np.amin(*args, **kwargs)
