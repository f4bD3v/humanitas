from csv_to_df import csv2df_bulk
import os
import cPickle as pickle
from time import time
import numpy as np
import pandas as pd
import sys

usage = '''
        get_raw_weekly   : read india weekly csv into one big dataframe, df_raw
        get_raw_daily    : read india daily csv into one big dataframe, df_raw
        isDaily          : True if the path is a daily one
        get_state        : read regions.csv into dataframe, df_reg
        get_data         : join df_raw and df_reg on 'city' into df, format 'date'
                           column into Pandas datetime format, and sort df by dates
        get_all_dates    : get all dates from the dataframe using pd.date_range
        mod_header       : replace 'index' by 'date'
        examine_fullness : examine if df_full has all dates for all label.
        replace_nan_with : helper
        get_piece        : unused function. patch df with missing dates manually
        get_full_data    : given df, return df_full or df_ts by option. The com-
                           putation of both is done all at once, thus no overhead.
'''


def get_raw_weekly(fp_csv):
    fp_lst = []
    for i in range(2005,2015):
        fp_lst.append("{}{}{}".format(fp_csv,i,".csv"))
    return csv2df_bulk(fp_lst)

#india_daily_Rice_2005-2014.csv
def get_raw_daily(fp_csv, product_lst):
    fp_lst = []
    for p in product_lst:
        fp_lst.append("{}{}{}".format(fp_csv,p,'_2005-2014.csv'))
    return csv2df_bulk(fp_lst)

def isDaily(fp_csv):
    return 'csv_daily' in fp_csv

def get_state(fp_state):
    return pd.read_csv(fp_state)

def get_data(fp_csv, fp_state, product_lst):
    start_time = time()
    if isDaily(fp_csv):
        if len(product_lst) == 0:
            raise Exception('empty product_lst')
        df_raw = get_raw_daily(fp_csv, product_lst)
    else:
        df_raw = get_raw_weekly(fp_csv)
    df_reg = get_state(fp_state)
    df = pd.merge(df_raw, df_reg, how="left", on="city")
    print 'formatting dates'
    df['date'] = pd.to_datetime(df['date'], format='%d/%m/%Y')
    print 'sorting by dates'
    df = df.sort('date')
    print("Cities not joined with states: "+str(list(set(df_raw["city"]) - set(df_reg["city"]))))
    print "{} {} {}".format("csv loaded into df in",(time()-start_time),'secs.')
    print "{} {}".format("size of df =", df.shape)
    return df

def get_all_dates(df, date_freq):
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


def get_piece(missing_dates, old_row):
    pieces = []
    for date in missing_dates:
        data =  [date]+list(old_row[1:6])+[float('nan'),old_row[-1]]
        new_row = pd.DataFrame(data, index = list(old_row.index)).T
        #print new_row
        pieces.append(new_row)

    return pd.concat(pieces)

def get_full_data(df, all_dates, \
                    using_df_full, using_df_ts, na_cutoff_rate, with_interpolation, \
                    filter_lst):
    start_time = time()
    pieces = []
    count = 0
    dup_count = 0
    df_ts = pd.DataFrame()

    print 'Using df_full?', using_df_full
    print 'Using df_ts?', using_df_ts
    print 'filter list = ', filter_lst

    for (state, city, product, subproduct, country, freq), group in \
            df.groupby(['state', 'city','product','subproduct', 'country', 'freq']):

        # missing_dates = list(set(all_dates) - set(group['date']))
        # # print missing_dates
        # # print len(all_dates), len(group['date']), len(missing_dates)
        # # break
        # missing_piece = get_piece(missing_dates, group.iloc[0,])

        #common part

        if product in filter_lst:
            continue

        group.set_index('date', inplace=True)

        try:
            group = group.reindex(all_dates)
        except:
            print (state, city, product, subproduct), 'dup dates'
            dup_count += 1
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
        if using_df_full:
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
    print 'number of labels with dup dates = ', dup_count
    print 'patch series with no dup dates in ', (time()-start_time)/60.0, ' min.'


    #report
    if using_df_full:
        print 'combining'
        df_full = pd.concat([df]+pieces)
        print 'sorting by dates'
        df_full = df_full.sort('date')
        print 'size of df_full = ', df_full.shape

    if using_df_ts:
        print 'size of df_ts = ', df_ts.shape

    return df_full, df_ts
