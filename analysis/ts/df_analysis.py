import pickle
import sys
from contextlib import contextmanager
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import collections

pk_in = 'all_India_week_timeseries.pickle'
pk_out = ''

@contextmanager
def redirected(stdout):
    saved_stdout = sys.stdout
    sys.stdout = open(stdout, 'w')
    yield
    sys.stdout = saved_stdout

def save_print_dict(d, file):
    with redirected(stdout=file):
        for key, val in d.iteritems():
            print key, ': ', val
    print 'some dict saved to '+file

def save_print(var, file):
    with redirected(stdout=file):
        print var
    print 'some print saved to '+file

def filter(vcounts, threshold):
    ret = 0
    for c in vcounts:
        if c >= threshold:
            ret = ret+1
    return ret

def plot_by(df_ts, q, title=None, legend=False):
    subdf = subset(df_ts, q)
    subdf.plot(title= title+': '+q+', #labels='+str(len(subdf.columns)), legend=legend)

def subset(df_ts, q1, q2=None, q3=None):
    cn_lst = []
    colnames = list(df_ts.columns)
    for cn in colnames:
        if (q1 in cn) and ((q2 == None) or q2 in cn) and (q3 == None or q3 in cn):
            cn_lst.append(cn)
    return df_ts[cn_lst]

def subrcd(na_record, q):
    nm_lst = []

def len_longest_na(series):
    len_na = 0
    longest = 0
    for elem in series.iteritems():
        if np.isnan(elem[1]):
            len_na = len_na+1
        else:
            len_na=0
        if len_na > longest:
            longest = len_na
    return longest

def na_analysis(na_record):
    

if __name__ == '__main__':
    with open(pk_in) as f:
        [df_ts, validcounts, dup_record, all_dates, all_cities, all_products, all_prod_subs] = pickle.load(f)
    print pk_in+' is loaded'

    leng = [len(all_dates), len(all_dates[(len(all_dates)/2-38):])]
    start_dates = ['2005-01', '2009-01']
    thrsh = [0, 0.05, 0.1, 0.2, 0.3, 0.4, 0.5]

    #generate dataframes of different cutoff rate
    df_ts_0 = [pd.DataFrame(), pd.DataFrame()]
    df_ts_5 = [pd.DataFrame(), pd.DataFrame()]
    df_ts_10 = [pd.DataFrame(), pd.DataFrame()]
    df_ts_20 = [pd.DataFrame(), pd.DataFrame()]
    na_record = [dict(), dict()]

    for label in df_ts.columns:
        for i in range(0,2):
            series = df_ts[label].loc[start_dates[i]:]
            nacount = float(leng[i] - series.count())/leng[i]
            nalen = len_longest_na(series)
            na_record[i][label] = (nacount, nalen)
            if nacount == thrsh[0]:
                df_ts_0[i][label] = series
            if nacount <= thrsh[1]:
                df_ts_5[i][label] = series
            if nacount <= thrsh[2]:
                df_ts_10[i][label] = series
            if nacount <= thrsh[3]:
                df_ts_20[i][label] = series

    #sort na_record
    na_record = [collections.OrderedDict(sorted(na_record[0].items())), collections.OrderedDict(sorted(na_record[1].items()))]

    print "2005-2014"
    print "na cutoff rate "+str(thrsh[0])+", #series="+str(df_ts_0[0].shape[1])
    print "na cutoff rate "+str(thrsh[1])+", #series="+str(df_ts_5[0].shape[1])
    print "na cutoff rate "+str(thrsh[2])+", #series="+str(df_ts_10[0].shape[1])
    print "na cutoff rate "+str(thrsh[3])+", #series="+str(df_ts_20[0].shape[1])


    print "2009-2014"
    print "na cutoff rate "+str(thrsh[0])+", #series="+str(df_ts_0[1].shape[1])
    print "na cutoff rate "+str(thrsh[1])+", #series="+str(df_ts_5[1].shape[1])
    print "na cutoff rate "+str(thrsh[2])+", #series="+str(df_ts_10[1].shape[1])
    print "na cutoff rate "+str(thrsh[3])+", #series="+str(df_ts_20[1].shape[1])

    #linearly interpolate missing data
    df_ts_5_itpo = []
    df_ts_10_itpo = []
    df_ts_20_itpo = []
    for i in range(0,2):
        df_ts_5_itpo.append(df_ts_5[i].interpolate())
        df_ts_10_itpo.append(df_ts_10[i].interpolate())
        df_ts_20_itpo.append(df_ts_20[i].interpolate())

    #generate weekly return dataframes
    df_ret_0 = [df_ts_0[0]/df_ts_0[0].shift(1)-1, df_ts_0[1]/df_ts_0[1].shift(1)-1]
    df_ret_5 = [df_ts_5[0]/df_ts_5[0].shift(1)-1, df_ts_5[1]/df_ts_5[1].shift(1)-1]
    df_ret_10 = [df_ts_10[0]/df_ts_10[0].shift(1)-1, df_ts_10[1]/df_ts_10[1].shift(1)-1]


    #plot time series
    #plot_by(df_ts_5[0], 'Rice', 'na cutoff 5%')
    #plot_by(df_ts_5[0], 'Wheat', 'na cutoff 5%')
    #plot_by(df_ts_5[0], 'Chicken', 'na cutoff 5%')
    #plot_by(df_ts_5_itpo[0], 'Rice', 'na cutoff 5% (interpolated)')
    #plot_by(df_ts_5_itpo[0], 'Wheat', 'na cutoff 5% (interpolated)')
    #plot_by(df_ts_5_itpo[0], 'Chicken', 'na cutoff 5% (interpolated)')


    plt.show()

    #output valuable variables
    save_print(dup_record, 'dup.txt')
    save_print_dict(na_record[0], 'na2005.txt')
    save_print_dict(na_record[1], 'na2009.txt')
