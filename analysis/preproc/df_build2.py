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

pk_out = 'india_week_df_full.pickle'
csv_out1 = 'india_week_full.csv'
csv_out2 = 'india_week_timeseries.csv'
date_freq = 'W-FRI'


def get_raw():
    fp_lst = []
    for i in range(2005,2015):
        fp_lst.append("{}{}{}".format(fp_csv,i,".csv"))
    return csv2df_bulk(fp_lst)

def get_data():
    start_time = time()
    df_raw = get_raw()
    df_reg = get_state()
    df = pd.merge(df_raw, df_reg, how="left", on="city")
    print("Cities not joined with states: "+str(list(set(df_raw["city"]) - set(df_reg["city"]))))
    print "{} {} {}".format("csv loaded into df in",(time()-start_time),'secs.')
    print "{} {}".format("size of df =", df.shape)
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

def flatten(df, one = False):
    df_ts = pd.DataFrame()
    for (state, city, product, subproduct), group in \
            df.groupby(['state', 'city','product','subproduct']):
        group.set_index('date')
        df_ts[(state, city, product, subproduct)] = group['price']
        if one:
            break
    return df_ts

def examine_fullness(df, leng):
    for (state, city, product, subproduct), group in \
            df.groupby(['state', 'city','product','subproduct']):
        if group.shape[0] < leng:
            print 'not full', group.shape, (state, city, product, subproduct)
        # elif group.shape[0] > leng:
        #     print 'over full', group.shape, (state, city, product, subproduct)

def get_piece(missing_dates, old_row):
    pieces = []
    for date in missing_dates:
        data =  [date]+list(old_row[1:6])+[float('nan'),old_row[-1]]
        new_row = pd.DataFrame(data, index = list(old_row.index)).T
        #print new_row
        pieces.append(new_row)

    return pd.concat(pieces)

def get_full_data(df, all_dates, examine=True, verbose=False):
    #fill NaN into missing dates
    #by generating missing date data
    #and combining them with df

    pieces = []
    start_time = time()
    count = 0

    for (state, city, product, subproduct), group in \
            df.groupby(['state', 'city','product','subproduct']):

        count += 1
        if verbose or (count % 1000 == 1):
            print count, (state, city, product, subproduct)

        missing_dates = list(set(all_dates) - set(group['date']))
        missing_piece = get_piece(missing_dates, group.iloc[0,])
        pieces.append(missing_piece)

    print 'number of labels = ', count
    print 'find all missing pieces in ', (time()-start_time)/60.0, ' min.'

    print 'combining'
    df_full = pd.concat([df]+pieces)
    print 'sorting by dates'
    df_full['date'] = pd.to_datetime(df_full['date'])
    df_full = df_full.sort('date')
    print 'size of df_full = ', df_full.shape

    #verify df_full contains all_dates
    if examine:
        examine_fullness(df_full, len(all_dates))
    return df_full


def main():
    df = get_data()
    all_dates = get_all_dates(df)
    df_full = get_full_data(df, all_dates)

    with open(pk_out, 'wb') as f:
        pickle.dump(df_full, f)

    df_full.to_csv(csv_out1)
    flatten(df_full, one=True).to_csv(csv_out2)

if __name__ == '__main__':
    main()
    # df = get_data()
    # all_dates = get_all_dates(df)
    # #df_full = get_full_data(df, all_dates)
    # pieces = []
    # for (state, city, product, subproduct), group in \
    #         df.groupby(['state', 'city','product','subproduct']):
    #
    #     missing_dates = list(set(all_dates) - set(group['date']))
    #     missing_piece = get_piece(missing_dates, group.iloc[0,])
    #     pieces.append(missing_piece)
    #     break
