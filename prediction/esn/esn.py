"""
	Author: Fabian Brix

	inspired by
	http://minds.jacobs-university.de/mantas
"""

import numpy as np
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import scipy.linalg as lg 
import inspect
import time
import pickle

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
    def __init__(self, data, split_ind, initN):
        self._dates = data[0]
        data = data[1]
        self._data = data
        self._N = split_ind
        self._train = data[0:split_ind]
        self._test = data[split_ind:]

        try:
            self._Nu = self._data.shape[1]
        except IndexError:
            self._Nu = 1

        self._initN = initN
        # one element of prediction granularity less than actually available data
        #self._N = 1825 # 5 years worth of daily data?
        #self._initN = 365 # 1 year worth of initialization
        self._x = np.zeros(self._Nu)
        self._y = 0
        # select v for concrete reservoir using validation, just rerun Y=W_out.bUX for different v
        self._nu = 0.005

    def init_reservoir(self, Nx):
        # "the bigger the size of the space of reservoir signals x(n), the easier it is to find a linear combination of the signals to approximate y_target(n)"
        # N > 1+Nu+Nx should hold true
        self._Nx = Nx
        self._Ny = 1
        self.init_Weights()

    def init_Weights(self):
        np.random.seed(42)

        self._Win = (np.random.rand(self._Nx,1+self._Nu)-0.5) * 1

        self._Wb = np.zeros((self._Ny, self._Nx))
        print self._Wb

        # Internal connection - to speed up computation make matrix sparse (set random entries to zero)
        self._W = np.random.rand(self._Nx, self._Nx)-.5

        # Compute W's eigenvalues
        eigValuesVectors = lg.eig(self._W)
        eigValues = eigValuesVectors[0]

        # Compute spectral radius = max abs eigenvalue
        # the spectral radius determines how fast the influence of an input dies out in a reservoir with time and how stable reservoir activations are
        # => the spectral radius should be greater in tasks requiring longer memory of the input
        rhoW = np.max(np.abs(eigValues))

        # Normalize random weight matrix by spectral radius
        self._W/=rhoW

        # Rescale matrix - Parameter to be TUNED
        rescale = 1.05
        self._W*=rescale

    def online_update(self):
        self._Cinv = self._lambda*self._Cinv-(1.0/self._lambda)*np.dot(np.outer(self._k,self._x),self._Cinv)
        # !!! numerical problems for x(n)-->0 and lambda<1 !!!
        # alleviate loss of symmetry in P(n): [P(n) + P.T(n)] /2
        self._Cinv = (self._Cinv+self._Cinv.T)/2.0

        # k(n) is representation of x(n) on the column space of C - always vector
        self._k = np.dot(self._Cinv, self._x)

        # Wout can either be a matrix or a vector
        err = self._y - np.dot(self._x, self._Wout)

        # RLS weight update
        self._Wout = self._Wout + np.dot(k,err)

        
    def run_training(self, mode, teacher_forcing, feedback, xTransOrder = False, leaky = False):
        params = self.run_training.func_code.co_varnames[:self.run_training.func_code.co_argcount]
        x_feedback = 0

        for t in range(self._N):
            # data contains a set of timeseries making u a vector
            u = self._data[t]
            uext = np.zeros(u.shape)
            xlast = self._x
            xect = np.zeros(xlast.shape)
            if isinstance(xTransOrder, int) and xTransOrder > 1:
                uext = np.power(u, xTransOrder)
                xext = np.power(xlast, xTransOrder)
                xlast = np.vstack((uext,xect))
            xOut = np.vstack((1,u,xlast))
            # check this function again
            if feedback:
                # put equation here Wback x y
                x_feedback = np.dot(self._Wb, self._y)
            xnext = np.tanh(np.dot(self._Win, np.vstack((1,u))+np.dot(self._W,xlast))+x_feedback)
            self._x = xnext
            if leaky:
                self._x = (1-self._alpha)*xlast+self._alpha*xnext
            if t >= self._initN:
                # TODO: find out WHY slicing at the end
                self._bUX[:,t-self._initN] = xOut[:,0]
                if mode == 'o':
                    self.online_update()

        if mode == 'b':
            self.batch_update()

        if isinstance(runs, int) and runs > 1:
            # Depending on online or batch collect bUX or 
            self.init_W()
            self._runcnt += 1
            if mode == 'o':
                self.runs = np.vstack((self.runs, self._y))
            elif mode == 'b':
                # TODO: check this - how to store runs
                self.runs = np.vstack((self.runs, self._bUX))
            self.run_training(*params) 

    def init_training(self):
        """
            Design matrix [1,U,X]
            keep N-initN time-steps in the design matrix, discard the initial initN steps
        """
        self._bUX = np.zeros((1+self._Nu+self._Nx,self._N-self._initN))
        """
            Target matrix 
            same as input sequence in teacher forcing, only shifted by 1 timestep 
        """
        self._Yt = data[self._initN+1:self._N+1] 

    def predef_training(self, pref_fn):
        # Load params into list from file
        self.train_run(*params)
        return self.train_err()

    def custom_training(self, mode, teacher_forcing, feedback, xTransOrder = False, leaky = False, runs = False):
        params = func_code.co_varnames[:func.func_code.co_argcount]
        self.init_training()
        print params

        self._x = np.zeros((self._Nx,self._Nu))

        if feedback:
            self._Wb = (np.random.rand(self._Ny, self._Nx)-.5) * 1
        if not leaky:
            self._alpha = 0.3
            # TODO: code command line prompt for alpha param
            raise Exception('I require a leak parameter')

        self._Wout = np.zeros(self._Nx+self._inputDim*2, self._Ny)

        if mode == 'o':
            self._p = 0
            delta = (1-self._lambda)*variance(x)
            self._Cinv = delta*np.indentity(self._Nx+self._inputDim*2)

        self.train_run(*params)
        # TODO print error, prompt save params? use pickle for dumping
        return self.train_err() 

    def batch_update(self):
        # Run regulized regression once in BATCH mode after training
        bUXT = self._bUX.T
        self._Wout = np.dot(np.dot(self._Yt,bUXT), lg.inv(np.dot(self._bUX,bUXT)+self._nu*np.eye(1+self._Nu+self._Nx)) )

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

    Ny = 1
    # Num. Regions and Products : R,P
    esn = ESN(data, split_ind, initN)
    esn.init_reservoir(Nx) 
    esn.run_training(mode = 'o', teacher_forcing = True, feedback = True, xTransOrder = 2, leaky = True)
    
    #Y = esn.generative_run(36, pred_test = False)
    #print Y
    #esn.plot_pred(Y, 'Oil price prediction example', 'Oil price')

    """
    TODO: 
    * be able to switch from applying an additional nonlinear function to output
        => Wout: dim(order*N+2) CHECK
    * include possibility to save parameters after training
    * be able to switch between batch and online algorithm
        implement online RLS algorithm
    * integrate me bootstrap
    """


if __name__ == "__main__":
	main()

    
