import numpy as np

def adapt(matrix, shape):
	m_shape = matrix.shape
	for i in range(len(shape)):
		matrix = np.repeat(matrix, shape[i]/m_shape[i], i)
	return matrix
