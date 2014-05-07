"""
	Author: Fabian Brix

	inspired by
	http://minds.jacobs-university.de/mantas
"""

import numpy as np
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import scipy.linalg as lg 
import scipy.sparse as sp

class ESN:
    """
        definitions:
        N - number of points in training set
        T - time interval of input
        Nu - size of the input signal
        Nx- size of the reservoir

        training tips:
        -keep reservoir size small for selection of hyperparams
    """	
    def __init__(self, data, split_ind, R, P, Nx, initN):
        self._dates = data[0]
        data = data[1]
        self._data = data
        self._N = split_ind
        self._train = data[0:split_ind]
        self._test = data[split_ind:]

        self._Nu = R*P

        self._initN = initN
        # one element of prediction granularity less than actually available data
        #self._N = 1825 # 5 years worth of daily data?
        #self._initN = 365 # 1 year worth of initialization
        self._Ny = 1

        """
            Reservoir size
        """
# "the bigger the size of the space of reservoir signals x(n), the easier it is to find a linear combination of the signals to approximate y_target(n)"
# N > 1+Nu+Nx should hold true
        self._Nx = Nx #1000 


        """
            ###
            RANDOM GENERATION 
            ###
        """
        np.random.seed(42)

        """tan
            +Input weight scaling
        """
        self._Win = (np.random.rand(self._Nx,1+self._Nu)-0.5) * 1


        """
            Sparsity of the reservoir
        """
# recurrent connection matrix
# speedup computation by making the reservoir matrix sparse - few connections between neurons in reservoir
# "fixed fanout number regardless of network size"
# uniform distribution of non-zero elements
        #self._W = np.random.rand(self._Nx,self._Nx)-0.5 
        self._W = np.random.rand(self._Nx, self._Nx)-.5

        """
            Spectral radius
        """
        eigValuesVectors = lg.eig(self._W)
        eigValues = eigValuesVectors[0]

# spectral radius - max abs eigenvalue
        rhoW = np.max(np.abs(eigValues))

# normalize random weight matrix with spectral radius
        self._W/=rhoW
        rescale = 1.05
        self._W*=rescale

# for nonzero inputs u(n) rhoW < 1 is not a necessary condition for the echo state property 
# the spectral radius determines how fast the influence of an input dies out in a reservoir with time
# and how stable reservoir activations are
# => the spectral radius should be greater in tasks requiring longer memory of the input

        """
            Design matrix [1,U,X]
            keep N-initN time-steps in the design matrix, discard the initial initN steps
        """
        self._bUX = np.zeros((1+self._Nu+self._Nx,self._N-self._initN))

        """
            Target matrix 
            same as input sequence, only shifted by 1 timestep 
        """
        self._Yt = data[self._initN+1:self._N+1] 

# leaking rate - selected as free parameter
        self._alpha = 0.3

# select v for concrete reservoir using validation, just rerun Y=W_out.bUX for different v
        self._nu = 0.005

    def teacher_forced_run(self):		
        # initial run vs. training
        """
            Teacher forcing - use Y_target as input
        """
        self._x = np.zeros((self._Nx,1))
        for t in range(self._N):
            # data contains a set of timeseries making u a vector
            u = self._data[t]
            xlast = self._x
            xnext = np.tanh(np.dot(self._Win, np.vstack((1,u)))+np.dot(self._W,xlast))
            self._x = (1-self._alpha)*xlast+self._alpha*xnext
            if t >= self._initN:
               self._bUX[:,t-self._initN] = np.vstack((1,u,self._x))[:,0]

    def ridge_regression(self):
        """
            Run regulized regression once after training (BATCH)
        """
        bUXT = self._bUX.T
        print bUXT
        self._Wout = np.dot(np.dot(self._Yt,bUXT), lg.inv(np.dot(self._bUX,bUXT)+self._nu*np.eye(1+self._Nu+self._Nx)) )
        print self._Wout

    # specify prediction horizon when calling function
    def generative_run(self, horizon, pred_test = False):
        Y = np.zeros((self._Ny,horizon))
# use last training points as input to make first prediction
        u = self._data[self._N]
        for t in range(horizon):
            xlast = self._x
            xnext = np.tanh(np.dot( self._Win, np.vstack((1,u)))+np.dot(self._W,xlast))
            self._x = (1-self._alpha)*xlast + self._alpha*xnext
            y = np.dot(self._Wout, np.vstack((1,u,self._x)) )
            print y
            Y[:,t] = y

            # use prediction as input to the network
            u = y 

        if pred_test: 
            return self.calc_pred_err(Y, horizon)
        else:
            return Y

    def calc_pred_err(self, Y, horizon):
		mse = np.sum( np.square( self._data[self._N:self._N+horizon+1] - Y[0,0:horizon] ) ) / horizon 
		return mse

    def plot_pred(self, Y, title, ylabel):
        fmt = mdates.DateFormatter('%d-%m-%Y')
        #loc = mdates.WeekdayLocator(byweekday=mdates.Monday)

        months = self._dates

        orig = np.zeros(len(self._data))
        orig[0:self._N] = self._train
        orig[self._N:] = np.nan
        target = np.zeros(len(self._data))
        target[0:self._N] = np.nan
        target[self._N:] = self._test
        pred = np.zeros(len(self._data))
        pred[0:self._N] = np.nan
        pred[self._N:] = Y

        plt.plot_date(x=months, y=orig, fmt="r-", color='blue')
        plt.plot_date(x=months, y=target, fmt="r-", color='black')
        plt.plot_date(x=months, y=pred, fmt="r-", color='red')
        plt.title(title)
        plt.ylabel(ylabel)
        plt.grid(True)
        plt.show()
        

def main():
    # load data and stuff	
    # two-dimensional array?; date, price for a region and commodity
    # convert date to floats
    data = np.loadtxt('oilprices.txt', delimiter=',', skiprows=1, unpack=True, converters={0 :mdates.strpdate2num('%Y-%m-%d')})

    print data

    # Split dataset into training and testset
    split_ind = len(data[0])-36

    # Reservoir size
    Nx = 500
    initN = 24  # 24 months initialization

    P = 1
    R = 1
    # Num. Regions and Products : R,P
    esn = ESN(data, split_ind, R, P, Nx, initN)

    esn.teacher_forced_run()
    esn.ridge_regression()
    Y = esn.generative_run(36, pred_test = False)
    print Y
    esn.plot_pred(Y, 'Oil price prediction example', 'Oil price')


if __name__ == "__main__":
	main()

    
