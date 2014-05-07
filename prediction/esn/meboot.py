"""
    MEBOOT.PY - Python package for the meboot (Maximum Entropy Bootstrap) algorithm for Time Series
    Author: Fabian Brix
    Method by H.D. Vinod, Fordham University - 
"""

import numpy as np

def get_trm_mean(s_sorted):
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
    intervals = np.vstack((z[:-1], z[1:])).T
    return intervals

def get_me_density(intervals):
    me_dens = 1.0/(intervals[:,1]-intervals[:,0])
    return udense

def sort(series):
    return s_sorted = np.sort(series)

def meboot(series, replicates):
    # ASC by default

    
    
