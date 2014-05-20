from csv_to_df import csv2df_bulk
import os
import cPickle as pickle
from time import time
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import sys

description = '''
        This script is outdated and not used.
        See df_run.py and df_build_func.py
'''


fp_csv = os.getcwd()+'/../../data/india/csv_weekly/rpms.dacnet.nic.in/all_commodities_weekly_india_'
fp_state = os.getcwd()+'/../../data/india/csv_daily/agmarknet.nic.in/regions.csv'

pk_out1 = 'india_week_df_full.pickle'
pk_out2 = 'india_week_df_ts.pickle'
csv_out1 = 'india_week_full.csv'
csv_out2 = 'india_week_timeseries.csv'
date_freq = 'W-FRI'
with_interpolation = False
na_cutoff_rate = 0.3
using_df_ts = True

def get_raw():
    fp_lst = []
    for i in range(2005,2015):
        fp_lst.append("{}{}{}".format(fp_csv,i,".csv"))
    return csv2df_bulk(fp_lst)

def get_state():
    return pd.read_csv(fp_state)

def get_data():
    start_time = time()
    df_raw = get_raw()
    df_reg = get_state()
    df = pd.merge(df_raw, df_reg, how="left", on="city")
    print 'formatting dates'
    df['date'] = pd.to_datetime(df['date'], format='%d/%m/%Y')
    print 'sorting by dates'
    df = df.sort('date')
    print("Cities not joined with states: "+str(list(set(df_raw["city"]) - set(df_reg["city"]))))
    print "{} {} {}".format("csv loaded into df in",(time()-start_time),'secs.')
    print "{} {}".format("size of df =", df.shape)
    return df

def get_all_dates(df):
    all_dates_raw = sorted(list(set(df['date'])))
    return pd.date_range(all_dates_raw[0], all_dates_raw[-1],freq=date_freq)

def mod_header(cols):
    cols = list(cols)
    cols[cols=='index'] = 'date'
    return cols


def examine_fullness(df, leng):
    for (state, city, product, subproduct), group in \
            df.groupby(['state', 'city','product','subproduct']):
        if group.shape[0] < leng:
            print 'not full', group.shape, (state, city, product, subproduct)
        # elif group.shape[0] > leng:
        #     print 'over full', group.shape, (state, city, product, subproduct)

def replace_nan_with(x, t):
    return x if isinstance(x, str) or isinstance(x, int) else t

#
# def get_piece(missing_dates, old_row):
#     pieces = []
#     for date in missing_dates:
#         data =  [date]+list(old_row[1:6])+[float('nan'),old_row[-1]]
#         new_row = pd.DataFrame(data, index = list(old_row.index)).T
#         #print new_row
#         pieces.append(new_row)
#
#     return pd.concat(pieces)

def get_full_data(df, all_dates):
    start_time = time()
    pieces = []
    count = 0
    df_ts = pd.DataFrame()

    print 'Using df_ts?', using_df_ts

    for (state, city, product, subproduct, country, freq), group in \
            df.groupby(['state', 'city','product','subproduct', 'country', 'freq']):

        # missing_dates = list(set(all_dates) - set(group['date']))
        # # print missing_dates
        # # print len(all_dates), len(group['date']), len(missing_dates)
        # # break
        # missing_piece = get_piece(missing_dates, group.iloc[0,])

        #common part
        group.set_index('date', inplace=True)

        try:
            group = group.reindex(all_dates)
        except:
            print (state, city, product, subproduct), 'dup dates'
            continue

        #df_ts part
        # note that it's "larger than" valid_rate
        if using_df_ts and group['price'].count() * 1. / len(all_dates) > 1. - na_cutoff_rate:
            if with_interpolation:
                df_ts[(product, subproduct, city, state)] = \
                    group['price'].interpolate().bfill()
            else:
                df_ts[(product, subproduct, city, state)] = group['price']

        #df_full part
        group.reset_index(inplace=True)
        group.columns = mod_header(group.columns)

        group['freq'] = group['freq'].apply(lambda x: replace_nan_with(x, freq))
        group['country'] = group['country'].apply(lambda x: replace_nan_with(x, country))
        group['city'] = group['city'].apply(lambda x: replace_nan_with(x, city))
        group['product'] = group['product'].apply(lambda x: replace_nan_with(x, product))
        group['subproduct'] = group['subproduct'].apply(lambda x: replace_nan_with(x, subproduct))
        group['state'] = group['state'].apply(lambda x: replace_nan_with(x, state))

        pieces.append(group)

        count += 1

    print 'number of labels = ', count
    print 'find all missing pieces in ', (time()-start_time)/60.0, ' min.'

    print 'combining'
    df_full = pd.concat([df]+pieces)
    print 'sorting by dates'
    df_full = df_full.sort('date')
    print 'size of df_full = ', df_full.shape

    return df_full, df_ts


def main():
    df = get_data()
    all_dates = get_all_dates(df)
    df_full, df_ts = get_full_data(df, all_dates)
    #examine_fullness(df_full, len(all_dates))

    with open(pk_out1, 'wb') as f:
        pickle.dump(df_full, f)

    df_full.to_csv(csv_out1)

    if using_df_ts:
        with open(pk_out2, 'wb') as f:
            pickle.dump(df_ts, f)
        df_ts.to_csv(csv_out2)

if __name__ == '__main__':
    main()
