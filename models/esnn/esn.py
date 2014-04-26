
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
	def __init__(self, data, N, R, P, input_size):

		self._data = data

		self._Nu = R*P
		self._N = 1825 # 5 years worth of daily data?
		self._initN = 365 # 1 year worth of initialization

		"""
			Reservoir size
		"""
		# "the bigger the size of the space of reservoir signals x(n), the easier it is to find a linear combination of the signals to approximate y_target(n)"
		# N > 1+Nu+Nx should hold true
		self._Nx = 1000 


		"""
			###
			RANDOM GENERATION 
			###
		"""

		"""tan
			+Input weight scaling
		"""
		self._Win = (random.rand(self._Nx,1+self._Nu)-0.5) * 1


		"""
			Sparsity of the reservoir
		"""
		# recurrent connection matrix
		# speedup computation by making the reservoir matrix sparse - few connections between neurons in reservoir
		# "fixed fanout number regardless of network size"
		# uniform distribution of non-zero elements
		self._W = random.rand(self._Nx,self._Nx)-0.5 

		"""
			Spectral radius
		"""
		eigValuesVectors = linalg.eig(self._W)
		eigvalues = eigValuesVectors[0]

		# spectral radius - max abs eigenvalue
		rhoW = max(abs(eigValues))

		# normalize random weight matrix with spectral radius
		self._W/=rhoW

		# for nonzero inputs u(n) rhoW < 1 is not a necessary condition for the echo state property 
		# the spectral radius determines how fast the influence of an input dies out in a reservoir with time
		# and how stable reservoir activations are
		# => the spectral radius should be greater in tasks requiring longer memory of the input

		"""
			Design matrix [1,U,X]
			keep N-initN time-steps in the design matrix, discard the initial initN steps
		"""
		self._bUX = zeros((1+Nu+Nx,N-initN))

		"""
			Target matrix 
			same as input sequence, only shifted by 1 timestep 
		"""
		Yt = data[initN+1:N+1] 

		# leaking rate - selected as free parameter
		self._alpha =

	def train(self):		
		# initial run vs. training
		for t in range(N):
			u = data[t]
			xlast = self._x
			xnext = tanh(dot(Win, vstack((1,u))+dot(W,xlast)
			x = (1-self._alpha)*xlast+self._alpha*xnext

	def get_error(self):





