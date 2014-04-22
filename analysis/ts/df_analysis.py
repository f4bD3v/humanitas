import pickle
import sys
from contextlib import contextmanager
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import collections

pk_in = 'all_India_week_timeseries.pickle'
pk_out = ''
pk_in2 = 'all_India_week.pickle'

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


def plot_by(df_ts, q, title=None, legend=False):
    subdff = subdf(df_ts, q)
    subdff.plot(title= title+': '+q+', #labels='+str(len(subdff.columns)), legend=legend)

def subdf(df_ts, q1, q2=None, q3=None):
    cn_lst = []
    colnames = list(df_ts.columns)
    for cn in colnames:
        if (q1 in cn) and ((q2 == None) or q2 in cn) and (q3 == None or q3 in cn):
            cn_lst.append(cn)
    return df_ts[cn_lst]

def subrcd(na_record, q):
    rcd_lst = dict()
    for key in na_record:
        if q in key:
            rcd_lst[key] = na_record[key]
    return rcd_lst

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

def na_analysis(na_record, all_cities, all_prod_subs):
    na_table = pd.DataFrame(columns=all_cities, index=all_prod_subs)
    nalen_table = pd.DataFrame(columns=all_cities, index=all_prod_subs)
    for key in na_record:
        (prod, sub, city) = key
        na_table[city][(prod, sub)] = na_record[key][0]
        nalen_table[city][(prod, sub)] = na_record[key][1]
    return na_table, nalen_table

def verify_none_nan(df):
    leng = df.shape[0]
    for label in df.columns:
        if df[label].count() != leng:
            raise Exception("Inter/Extrapolation failed at "+label)

if __name__ == '__main__':
    with open(pk_in) as f:
        [df_ts, validcounts, dup_record, all_dates, all_cities, all_products, all_prod_subs] = pickle.load(f)
    print pk_in+' is loaded'

    with open(pk_in2) as f:
        [df] = pickle.load(f)
    print pk_in2+' is loaded.'


    leng = len(all_dates)
    start_date = '2005-01'
    thrsh = [0.1,0.2,0.3]

    #generate dataframes of different cutoff rate
    df_ts_cut = dict()
    for t in thrsh:
        df_ts_cut[t] = pd.DataFrame()
    na_record = dict()

    for label in df_ts.columns:
        series = df_ts[label].loc[start_date:]
        nacount = int(float(leng - series.count())/leng*100)/100.0
        nalen = len_longest_na(series)
        na_record[label] = (nacount, nalen)
        for t in thrsh:
            if nacount <= t:
                df_ts_cut[t][label] = series

    #sort na_record
    na_record = collections.OrderedDict(sorted(na_record.items()))

    print "2005-2014"
    for t in thrsh:
        print "na cutoff rate "+str(t)+", #series="+str(df_ts_cut[t].shape[1])

    #linearly interpolate missing data
    df_ts_itpo = dict()
    for t in thrsh:
        df_ts_itpo[t] = df_ts_cut[t].interpolate().bfill()
        verify_none_nan(df_ts_itpo[t])

    #generate weekly return dataframes
    df_ts_ret = dict()
    for t in thrsh:
        df_ts_ret[t] = df_ts_cut[t]/df_ts_cut[t].shift(1)-1

    #na analysis
    na_table, nalen_table = na_analysis(na_record, all_cities, all_prod_subs)

    #plot time series
    plot_by(df_ts_cut[0.3], 'Rice', 'na cutoff 0.3')
    plot_by(df_ts_cut[0.3], 'Wheat', 'na cutoff 0.3')
    plot_by(df_ts_cut[0.3], 'Chicken', 'na cutoff 0.3')
    plot_by(df_ts_itpo[0.3], 'Rice', 'na cutoff 0.3 (interpolated)')
    plot_by(df_ts_itpo[0.3], 'Wheat', 'na cutoff 0.3 (interpolated)')
    plot_by(df_ts_itpo[0.3], 'Chicken', 'na cutoff 0.3 (interpolated)')


    plt.show()

    #output valuable variables
    save_print(dup_record, 'dup.txt')
    save_print_dict(na_record, 'na.txt')
    na_table.to_csv('na_table.csv')
    nalen_table.to_csv('nalen_table.csv')
