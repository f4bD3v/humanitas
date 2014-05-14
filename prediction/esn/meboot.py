"""
    MEBOOT.PY - Python package for the meboot (Maximum Entropy Bootstrap) algorithm for Time Series
    Author: Fabian Brix
    Method by H.D. Vinod, Fordham University - 
"""
import sys
import numpy as np
import matplotlib.pyplot as plt

def sort(series):
    ind_sorted = np.argsort(series)
    s_sorted = series[ind_sorted]
    return s_sorted, ind_sorted 

def get_trm_mean(series, percent):
    # FIXED
    dev = np.abs(series[1:]-series[:-1])
    n = len(dev)
    k = n*(percent/100.0)/2.0
    k = round(k,0)
    return np.mean(dev[k:n-k])

def get_intermed_pts(series, s_sorted, percent):
    zt = (s_sorted[:-1]+s_sorted[1:])/2.0
    m_trm = get_trm_mean(series, percent)
    print m_trm
    z0 = s_sorted[0]-m_trm
    zT = s_sorted[-1]+m_trm
    z = np.hstack((z0,zt,zT))
    return z 

def get_intervals(z):
    return np.vstack((z[:-1], z[1:])).T

def get_me_density(intervals):
    return 1.0/(intervals[:,1]-intervals[:,0])

def get_cpf(me_density, intervals):
    cpf = np.array([sum(me_density[:i+1]) for i in xrange(me_density.shape[0]-1)])
    return cpf/np.max(cpf)

def get_quantiles(cpf, intervals, series):
    quantiles = []
    for d in xrange(series.shape[0]):
        u = np.random.uniform(0,1)
        for i in xrange(cpf.shape[0]):
            cp = cpf[i]
            if u <= cp:
                cpm = cpf[i-1]
                if i == 0: 
                    cpm = 0
                m = (cp-cpm)/1.0*(intervals[i,1]-intervals[i,0])
                xp = (u - cpm)*1.0/m+intervals[i,0]
                quantiles.append(xp)
                break
    return np.array(quantiles)

def meboot(series, replicates):
    # ASC by default
    print series
    np.random.seed(0)

    s_sorted, ind_sorted = sort(series)

    z = get_intermed_pts(series, s_sorted, 10)
    #print 'z ', z 
    intervals = get_intervals(z)
    #print 'intervals ', intervals
    me_density = get_me_density(intervals)
    #print 'uni dens ', me_density
    cpf = get_cpf(me_density, intervals)
    #print 'cpf ', cpf
    quantiles = get_quantiles(cpf, intervals, series)
    #print 'quantiles ', quantiles
    quantiles = np.sort(quantiles)
    
    replicate = quantiles[ind_sorted]
    print 'replicate ', replicate

    # TODO: Undertand and add repeat mechanism
    plt.plot(series, color='r')
    plt.plot(replicate, color='b')
    plt.ylim(0,30)
    plt.show()

def main(args):
    series = np.array([4,12,36,20,8])
    meboot(series, 1)

if __name__ == "__main__":
    if sys.argv < 2:
        print 'hello'
    else: 
        main(*sys.argv)

