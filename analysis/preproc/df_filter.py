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
    for key in na_record.keys():
        (prod, sub, city) = key
        if isinstance(sub, str):
            na_table[city][(prod,sub)] = na_record[key][0]
            nalen_table[city][(prod,sub)] = na_record[key][1]
        else:
            na_table[city][(prod, ' ')] = na_record[key][0]
            nalen_table[city][(prod,' ')] = na_record[key][1]
    return na_table, nalen_table



def main():
    with open(pk_in) as f:
        df_ts = pickle.load(f)
    print pk_in+' is loaded'

    regions = get_regions()

    for region in regions:
        for city in region:
            for product, subproduct
    #na analysis
    #TODO modify to per region version
    na_table, nalen_table = na_analysis(na_record, all_cities, all_prod_subs)


    #generate weekly return dataframes
    df_ts_ret = df_ts_cut/df_ts_cut.shift(1)-1

    #output valuable variables
    na_table.to_csv('na_table.csv')
    nalen_table.to_csv('nalen_table.csv')


if __name__ == '__main__':
    main()
