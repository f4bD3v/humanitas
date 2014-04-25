from csv_to_df import csv2df_bulk
import os
import cPickle as pickle
from time import time
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import sys
from collections import defaultdict

fp_csv = os.getcwd()+'/../../data/india/csv_weekly/rpms.dacnet.nic.in/all_commodities_weekly_india_'
fp_state = os.getcwd()+'/../../data/india/csv_daily/agmarknet.nic.in/regions.csv'

pk_in = 'all_India_week.pickle'
pk_out = 'all_India_week_timeseries.pickle'
date_freq = 'W-FRI'
#na_cutoff_rate = .3
with_interpolation = False

def get_raw():
    fp_lst = []
    for i in range(2005,2015):
        fp_lst.append("{}{}{}".format(fp_csv,i,".csv"))
    return csv2df_bulk(fp_lst)

def get_data():
    if True:#not os.path.isfile(pk_in):
        df_raw = get_raw()
        df_reg = get_state()
        df = pd.merge(df_raw, df_reg, how="left", on="city")
        print "formating dates"
        df['date'] = pd.to_datetime(df['date'], format='%d/%m/%Y')
        print "sorting by dates"
        df = df.sort('date')
        print("Cities not joined with states: "+str(list(set(df_raw["city"]) - set(df_reg["city"]))))
        with open(pk_in, 'wb') as f:
            pickle.dump(df,f)
        print "df dumped to "+pk_in
    else:
        with open(pk_in, 'rb') as f:
            df = pickle.load(f)
        print "df loaded in"
    return df


def get_state():
    return pd.read_csv(fp_state)


def get_all_dates(df):
    all_dates_raw = sorted(list(set(df['date'])))
    return pd.date_range(all_dates_raw[0], all_dates_raw[-1],
            freq=date_freq)

def mod_header(cols):
    cols = list(cols)
    cols[cols=='index'] = 'date'
    return cols

def flatten(df):
    df_ts = pd.DataFrame()
    just_one = True
    for (state, city, product, subproduct), group in \
            df.groupby(['state', 'city','product','subproduct']):
        group.set_index('date', inplace=True)
        if just_one:
            df_ts[(state, city, product, subproduct)] = group['price']
            just_one = False
    return df_ts

#def main():


if __name__ == '__main__':
    #main()
    df = get_data()
    all_dates = get_all_dates(df)

    for (state, city, product, subproduct), group in \
            df.groupby(['state', 'city','product','subproduct']):

        #fill NaN into missing dates
        group.set_index('date', inplace=True)
        try:
            group = group.reindex(all_dates)
        except Exception, e:
            #print (product, subproduct, city)
            #print e
            #print 'duplicated dates'
            continue

        #if with_interpolation:
        #    group['price'] = group['price'].interpolate().bfill()



    #verify df contains all_dates
    #TODO

    with open(pk_out, 'wb') as f:
        pickle.dump(df, f)
    df.to_csv('df.csv')
    flatten(df).to_csv('df_ts.csv')
