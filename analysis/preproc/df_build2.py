from csv_to_df import csv2df_bulk
import os
import cPickle as pickle
from time import time
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import sys

fp = os.getcwd()+'/../../data/india/csv_weekly/rpms.dacnet.nic.in/all_commodities_weekly_india_'
pk_in = 'all_India_week.pickle'
pk_out = 'all_India_week_timeseries.pickle'
date_freq = 'W-FRI'
na_cutoff_rate = .3
with_interpolation = True

def get_data():
    if not os.path.isfile(pk_in):
        fp_lst = []
        for i in range(2005,2015):
            fp_lst.append("{}{}{}".format(fp,i,".csv"))
        df = csv2df_bulk(fp_lst)
        with open(pk_in, 'wb') as f:
            pickle.dump([df],f)
        print "df dumped to "+pk_in
    else:
        with open(pk_in, 'rb') as f:
            [df] = pickle.load(f)

    return df

def get_all_dates(df):
    all_dates_raw = sorted(list(set(df['date'])))
    return pd.date_range(all_dates_raw[0], all_dates_raw[-1],
            freq=date_freq)

def main():
    df = get_data()
    all_dates = get_all_dates(df)

    df_ts = pd.DataFrame()

    for (product, subproduct, city), group in \
            df.groupby(['product', 'subproduct', 'city']):
        group.set_index('date', inplace=True)
        try:
            group = group.reindex(all_dates)
        except Exception, e:
            print (product, subproduct, city)
            print e
            print 'duplicated dates'
            continue

        if group['price'].count() * 1. / len(all_dates) < 1. - na_cutoff_rate:
            continue

        if with_interpolation:
            df_ts[(product, subproduct, city)] = \
                group['price'].interpolate().bfill()
        else:
            df_ts[(product, subproduct, city)] = group['price']

    with open(pk_out, 'wb') as f:
        pickle.dump(df_ts, f)
    df_ts.to_csv('time-series.csv')


if __name__ == '__main__':
    main()
