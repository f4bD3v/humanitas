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
        self._traindates =  self._dates[initN+1:split_ind+1]
        data = data[1]
        self._data = data
        self._N = split_ind
        self._train = data[initN:split_ind+1]
        self._test = data[split_ind:]
        self._Ytrain = np.zeros(len(self._traindates))

        try:
            self._Nu = self._data.shape[1]
        except IndexError:
            self._Nu = 1

        self._initN = initN
        # one element of prediction granularity less than actually available data
        #self._N = 1825 # 5 years worth of daily data?
        #self._initN = 365 # 1 year worth of initialization
        self._y = 0
        # select v for concrete reservoir using validation, just rerun Y=W_out.bUX for different v
        self._nu = 1E-8
        self._mu = 0.3

    def init_reservoir(self, Nx):
        # "the bigger the size of the space of reservoir signals x(n), the easier it is to find a linear combination of the signals to approximate y_target(n)"
        # N > 1+Nu+Nx should hold true
        self._Nx = Nx
        self._Ny = 1

    def init_Weights(self, squared = False):
        np.random.seed(42)

        self._Win = (np.random.rand(self._Nx,1+self._Nu)-0.5) * 1

        # Internal connection - to speed up computation make matrix sparse (set random entries to zero)
        self._W = np.random.rand(self._Nx, self._Nx)-.5
        it = np.nditer(self._W, flags=['multi_index'])
        while not it.finished:
            if np.random.rand(1)[0] < 0.95:
                self._W[it.multi_index] = 0
            it.iternext()

        print self._W

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
        rescale = .8
        self._W*=rescale

        if squared:
            self._Wout = np.zeros((self._Nx*2+self._Nu*2+2,1))
        else:
            self._Wout = np.zeros((self._Nx+self._Nu+1,1))


    def init_training(self):
        self._x = np.zeros((self._Nx,1))
        """
            Design matrix [1,U,X]
            keep N-initN time-steps in the design matrix, discard the initial initN steps
        """
        self._bUX = np.zeros((1+self._Nu+self._Nx,self._N-self._initN))
        """
            Target matrix 
            same as input sequence in teacher forcing, only shifted by 1 timestep 
        """
        self._Yt = self._data[self._initN+1:self._N+1] 

    def LMS_update(self, t, out):
        stab = 2.0/np.power(np.linalg.norm(out),2)
        if self._mu >= stab:
            self._mu = stab/2.0

        err = self._data[t+1] - np.dot(self._Wout.T, out)

        nWout = self._Wout + self._mu * np.dot(out,err)
        self._Wout = nWout

    def RLS_update(self, t, out):
        pi = np.dot(out.T,self._P)

        gamma = self._lambda + np.dot(pi,out)

        self._k = pi.T / gamma

        #err = np.tanh(self._data[t+1]) - np.tanh(np.dot(self._Wout.T, out))
        err = np.tanh(self._data[t+1]) - np.dot(self._Wout.T, out)

        nWout = self._Wout + np.dot(self._k,err)
        self._Wout = nWout

        nP = (1.0/self._lambda)*(self._P-np.dot(self._k, pi))
        self._P = (nP+nP)/2.0

    def run_training(self, teacher_force = False, squared = False, leaky = False, runs = False):
        #params = self.run_training.func_code.co_varnames[1:self.run_training.func_code.co_argcount]
        self._runs = 0
        x_feedback = 0.0

        niter = 0
        # t < self._N
        for t in xrange(self._N):
            if t % 5 != 0:
                continue
            # data contains a set of timeseries making u a vector
            
            #if t >= self._initN:
            #    break
            u = self._data[t]
            print 'u ', u
            # white noise on x
            xlast = self._x + np.random.normal(0, 0.0001, self._x.shape[0])[:,np.newaxis]
            if not teacher_force:
                x_feedback = np.dot(self._Wb, self._y)

            xnext = np.tanh(np.dot(self._Win, np.vstack((1,u)))+np.dot(self._W,xlast)+x_feedback)
            self._x = xnext

            out = np.vstack((1,u,xnext))

            if leaky:
                self._x = (1-self._alpha)*xlast+self._alpha*xnext
            if t >= self._initN:
                self._bUX[:,t-self._initN] = out[:,0]
                # for the moment don't store out_sq in bUX
                if squared:
                    out_sq = np.power(out, 2)
                    out = np.vstack((out,out_sq))
                if not teacher_force:
                    # both of shape (500,1), transpose one
                    self._y = np.dot(out.T, self._Wout)
                    self._Ytrain[t-self._initN] = self._y
                    if niter % 100 == 0:
                        print 'iteration: ', niter
                        print 'y' ,self._y
                    self.LMS_update(t, out)
                    niter += 1

        if teacher_force:
            print 'one time batch update'
            self.batch_update()

        if isinstance(self._runs, int) and self._runs > 1:
            # Depending on online or batch collect bUX or 
            #self.init_W()
            self._runcnt += 1
            if teacher_force: 
                self._runs = np.vstack((self._runcnt, self._y))
            else:
                # TODO: check this - how to store runs
                self._runs = np.vstack((self._runcnt, self._bUX))
            self.run_training(*params) 

    """
    def predef_training(self, pref_fn):
        # Load params into list from file
        self.run_training()
        return# self.train_err()
    """

    def custom_training(self, teacher_force, squared = False, leaky = False, runs = False):
    #   params = self.run_training.func_code.co_varnames[1:self.run_training.func_code.co_argcount]
        self.init_training()
        self._leaky = leaky

        self.init_Weights(squared)

        if leaky:
            self._alpha = 0.3

        if not teacher_force:
            print 'adapting Wout online'
            self._lambda = .995
            print 'feedback'
            self._Wb = (np.random.rand(self._Nx, self._Ny)-.5) * 5

            std = np.std(self._data[:self._initN])
            delta = 100 * std * std
            if squared:
                self._P = delta*np.identity(self._Nx*2+self._Nu*2+2)
            else:
                self._P = delta*np.identity(self._Nx+self._Nu+1)

            print 'init Cinv ', self._P

        self.run_training(teacher_force, squared, leaky, runs)

        self.train_err()
        # TODO print error, prompt save params? use pickle for dumping

    def batch_update(self):
        # Run regulized regression once in BATCH mode after training
        bUXT = self._bUX.T
        self._Wout = np.dot(np.dot(self._Yt,bUXT), lg.inv(np.dot(self._bUX,bUXT)+self._nu*np.eye(1+self._Nu+self._Nx)) )

    # specify prediction horizon when calling function
    def generative_run(self, horizon, squared = False):
        Y = np.zeros((self._Ny,horizon))
        # use last training points as input to make first prediction
        u = self._data[self._N]
        y = self._y
        for t in range(horizon):
            xlast = self._x
            xnext = np.tanh(np.dot(self._Win, np.vstack((1,u)))+np.dot(self._W,xlast))
            if self._leaky:
                self._x = (1-self._alpha)*xlast + self._alpha*xnext
            else: 
                self._x = xnext
            out = np.vstack((1,u,self._x))
            if squared:
                    out_sq = np.power(out, 2)
                    out = np.vstack((out,out_sq))
            y = np.dot(out.T, self._Wout)
            Y[:,t] = y

            # use prediction as input to the network
            u = y 

        self.test_err(Y, horizon)
        return Y

    def train_err(self):
        mse = np.sum( np.square( self._train[1:] - self._Ytrain[:] ) ) / (self._N-self._initN)
        print 'training mse: ', mse

    def test_err(self, Y, horizon):
		mse = np.sum( np.square( self._data[self._N:self._N+horizon+1] - Y[0,0:horizon] ) ) / horizon 
		print 'test mse: ', mse

    def plot_training(self, title, ylabel):
        print 'plotting training'
        fmt = mdates.DateFormatter('%d-%m-%Y')
        #loc = mdates.WeekdayLocator(byweekday=mdates.Monday)
        months = self._traindates

        train = self._data[self._initN+1:self._N+1] 
        print train.shape
        print self._Ytrain.shape
        print self._traindates.shape
        plt.figure(10).clear()
        plt.plot_date(x=months, y=self._Ytrain, fmt="-", color='blue')
        plt.plot_date(x=months, y=train, fmt="-", color='green')

        plt.title(title)
        plt.ylabel(ylabel)
        plt.grid(True)
        plt.show()

    def plot_test(self, Y, title, ylabel):
        fmt = mdates.DateFormatter('%d-%m-%Y')
        #loc = mdates.WeekdayLocator(byweekday=mdates.Monday)
        months = self._dates[self._N:self._N+50]

        target = self._data[self._N:self._N+50] 
        pred = Y.flatten()

        plt.figure(2).clear()
        plt.plot_date(x=months, y=target, fmt="-", color='blue')
        plt.plot_date(x=months, y=pred, fmt="-", color='red')
        plt.title(title)
        plt.ylabel(ylabel)
        plt.grid(True)
        plt.show()
        

def main():
    # load data and stuff	
    # two-dimensional array?; date, price for a region and commodity
    # convert date to floats
    #data = np.loadtxt('oilprices.txt', delimiter=',', skiprows=1, unpack=True, converters={0 :mdates.strpdate2num('%Y-%m-%d')})

    data = np.genfromtxt('good_series_wholesale_daily.txt', usecols = (0, 1), delimiter=',', skiprows=1, unpack=True, converters={0:mdates.strpdate2num('%Y-%m-%d')})

    # Split dataset into training and testset
    print len(data[0])
    split_ind = len(data[0])-50

    # Reservoir size
    Nx = 500
    initN = 740# 24 months initialization

    Ny = 1
    # Num. Regions and Products : R,P
    esn = ESN(data, split_ind, initN)
    esn.init_reservoir(Nx) 
    esn.init_training()
    esn.custom_training(teacher_force = False, squared = True, leaky = False)
    esn.plot_training('Training outputs', 'Y')
    Y = esn.generative_run(50, squared = True)
    esn.plot_test(Y, 'Test run', 'Price')

    #esn.custom_training("o", teacher_forcing = True, feedback = True, xTransOrder = False, leaky = True)

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

    
