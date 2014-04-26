"""
	Author: Fabian Brix

	inspired by
	http://minds.jacobs-university.de/mantas
"""

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
		# one element of prediction granularity less than actually available data
		self._N = 1825 # 5 years worth of daily data?
		self._initN = 365 # 1 year worth of initialization
		self._Ny = 1

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
		random.seed(42)

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
		self._Yt = data[initN+1:N+1] 

		# leaking rate - selected as free parameter
		self._alpha = 0.3

		# select v for concrete reservoir using validation, just rerun Y=W_out.bUX for different v
		self._nu

	def teacher_forced_run(self):		
		# initial run vs. training
		"""
			Teacher forcing - use Y_target as input
		"""
		self._x = zeros((Nx,1))
		for t in range(N):
			# data contains a set of timeseries making u a vector
			u = data[t]
			xlast = self._x
			xnext = tanh(dot(Win, vstack((1,u)))+dot(W,xlast))
			self._x = (1-self._alpha)*xlast+self._alpha*xnext

	def ridge_regression(self):
		"""
			Run regulized regression once after training (BATCH)
		"""
		bUXT = self._bUX.T
		self._Wout = dot(dot(self._Yt,bUXT), linalg.inv(dot(self._bUX,bUXT)+self._nu*eye(1+self._Nu+self._Nx)) )

		# specify prediction horizon when calling function
	def generative_run(self, horizon, pred_test = False):
		Y = zeros((Ny,horizon))
		# use last training points as input to make first prediction
		u = data[N]
		for t in range(horizon):
			xlast = self._x
			xnext = tanh( dot( Win, vstack((1,u)))+dot(W,xlast)))
    		self._x = (1-self._a)*xlast + self._a*xnext
    		y = dot(self._Wout, vstack((1,u,x)) )
    		Y[:,t] = y

    		# use prediction as input to the network
    		u = y 

    	if pred_test: 
    		return calc_pred_err(Y, horizon)
    	else:
    		return Y

    def calc_pred_err(self, Y, horizon):
		mse = sum( square( data[N+1:Nx+horizon+1] - Y[0,0:horizon] ) ) / horizon 
		return mse


def main():

	# load data and stuff	

if __name__ == "__main__":
	main()


