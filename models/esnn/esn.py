
from numpy import *
from matplotlib.pyplot import *
import scipy.linalg

class ESN:

	"""
		definitions:
		N - number of points in training set
		T - time interval of input
		Nu - size of the input signal
		Nx - size of the reservoir


		training tips:
		- keep reservoir size small for selection of hyperparams
	"""	
	def __init__(self, N, R, P, input_size):


		"""
			random generation
		"""

		T = 30
		Nu = T*R*P
		N = 1825 # 5 years worth of daily data?


		"""
			Reservoir size
		"""
		# "the bigger the size of the space of reservoir signals x(n), the easier it is to find a linear combination of the signals to approximate y_target(n)"
		# N > 1+Nu+Nx should hold true
		Nx = 1000 

		#input weights matrix 
		"""
			Input Scaling
		"""
		Win =  0



		"""
			Sparsity of the reservoir
		"""

		# recurrent connection matrix
		# speedup computation by making the reservoir matrix sparse - few connections between neurons in reservoir
		# "fixed fanout number regardless of network size"
		# uniform distribution of non-zero elements
		W = random.rand(Nx,Nx)-0.5 


		"""
			Spectral radius
		"""

		eigValuesVectors = linalg.eig(W)
		eigvalues = eigValuesVectors[0]

		# spectral radius - max abs eigenvalue
		rhoW = max(abs(eigValues))

		# normalize random weight matrix with spectral radius
		W/=rhoW

		# for nonzero inputs u(n) rhoW < 1 is not a necessary condition for the echo state property 
		# the spectral radius determines how fast the influence of an input dies out in a reservoir with time
		# and how stable reservoir activations are
		# => the spectral radius should be greater in tasks requiring longer memory of the input


		# leaking rate - selected as free parameter
		alpha =
