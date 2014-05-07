"""
    MEBOOT.PY - Python package for the meboot (Maximum Entropy Bootstrap) algorithm for Time Series
    Author: Fabian Brix
    Method by H.D. Vinod, Fordham University - 
"""

import numpy as np

def get_trm_mean(s_sorted):
    # TODO: trim series by a certain percentage before computing the 'trimmed mean'
    m_trm = np.sum(s_sorted[1:]-s_sorted[:-1])/(1.0*(len(s_sorted)-1))
    return m_trm

def get_intermed_pts(s_sorted):
    zt = (s_sorted[:-1]+s_sorted[1:])/2.0
    m_trm = get_trm_mean(s_sorted)
    z0 = s_sorted[0]-m_trm
    zT = s_sorted[-1]-m_term
    z = np.vstack((z0,zt,zT))
    return z 

def get_intervals(z):
    return np.vstack((z[:-1], z[1:])).T

def get_me_density(intervals):
    return 1.0/(intervals[:,1]-intervals[:,0])

def sort(series):
    ind_sorted = np.argsort(series)
    s_sorted = series[ind_sorted]
    return s_sorted, ind_sorted 

def meboot(series, replicates):
    # ASC by default
    s_sorted, ind_sorted = sort(series)

    z = get_intermed_pts(s_sorted)

    intervals = get_intervals(z)

    me_density = get_me_density(intervals)

    # TODO: Generate random numbers from the [0,1] uniform interval, compute sample quantiles of the ME density at those points and sort them.

    # TODO: Undertand and add repeat mechanism
    
    
