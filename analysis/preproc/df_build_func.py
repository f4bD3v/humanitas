from csv_to_df import csv2df_bulk
import os
import cPickle as pickle
from time import time
import numpy as np
import pandas as pd
import sys
import csv
import collections
import matplotlib.pyplot as plt

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
    print 'replace NR in prices with NaN'
    df['price'].replace('NR', np.nan, inplace=True)

    missing_cities= list(set(df_raw["city"]) - set(df_reg["city"]))
    if len(missing_cities) != 0:
        print "Cities not joined with states", missing_cities
        with open('missing_cities.csv', 'wb') as f:
            wr = csv.writer(f)
            wr.writerow(missing_cities)
        if missing_cities != ['NR']: #exception case in the weekly dataset
            raise Exception('missing cities as above')

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


def examine_fullness(df, leng, with_interpolation):
    passed = True
    for (state, city, product, subproduct), group in \
            df.groupby(['state', 'city','product','subproduct']):
        if group.shape[0] < leng:
            passed = False
            print 'not full', group.shape, (state, city, product, subproduct), group.shape
        elif group.shape[0] > leng:
            passed = False
            print 'over full', group.shape, (state, city, product, subproduct), group.shape
        if with_interpolation:
            if group['price'].count() < leng:
                passed = False
                print 'not fully interpolated', (state, city, product, subproduct), group['price'].count()

    if passed:
        print 'examine df_full succeeds.'
    else:
        print 'examine df_full failed!'


def examine_df_ts_fullness(df_ts, leng, with_interpolation):
    passed = True
    for label in list(df_ts.columns):
        if df_ts[label].shape[0] < leng:
            passed=False
            print 'length not equal to full length', label, df_ts[label].shape[0],'/',leng
        elif df_ts[label].shape[0] > leng:
            passed=False
            print 'length larger than full length', label, df_ts[label].shape[0],'/',leng
        if with_interpolation:
            if df_ts[label].count() < leng:
                passed=False
                print 'not fully interpolated', label, df_ts[label].count(),'/',leng
    if passed:
        print 'examine df_ts fullness succeeds.'
    else:
        print 'examine df_ts fullness failed!'

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
    err_count = 0
    df_full = pd.DataFrame()
    df_ts = pd.DataFrame()

    print 'Using df_full?', using_df_full
    print 'Using df_ts?', using_df_ts
    print 'filter list = ', filter_lst

    dup_records = []
    #empty_subproduct = []

    for (state, city, product, subproduct, country, freq), group in \
            df.groupby(['state', 'city','product','subproduct', 'country', 'freq']):

        # missing_dates = list(set(all_dates) - set(group['date']))
        # # print missing_dates
        # # print len(all_dates), len(group['date']), len(missing_dates)
        # # break
        # missing_piece = get_piece(missing_dates, group.iloc[0,])

        #common part

        #filter out things not in filter_lst
        if len(filter_lst) != 0 and product not in filter_lst:
            continue

        #skip those with only NaN data
        if group['price'].count() == 0:
            continue

        #data with empty subproduct in daily dataset is incorrect
        if freq == 'day':
            if subproduct == '':
                print 'ignore empty daily subproduct',(state, city, product, subproduct, country, freq)
                #empty_subproduct.append(((state, city, product, subproduct, country, freq), group.shape))
                continue


        group.set_index('date', inplace=True)

        try:
            group = group.reindex(all_dates)
        except Exception, e:
            print e, (state, city, product, subproduct, country, freq)
            err_count += 1
            group.reset_index(inplace=True)
            group.columns = mod_header(group.columns)
            dupdf, dup_dates = extract_duplicates(group)
            dup_records.append(((state, city, product, subproduct, country, freq), dupdf))

            if freq == 'week':
                continue
            else:
                #handle duplicates of daily datasets
                group.drop_duplicates(cols='date', inplace=True)
                #fill NaN in the missing dates again
                group.set_index('date', inplace=True)
                group = group.reindex(all_dates)
                print 'duplicate handled, new length', group.shape[0], '/', len(all_dates)

        #skip those with more NaN than na_cutoff_rate
        if 1. - group['price'].count() * 1. / len(all_dates) > na_cutoff_rate:
            continue

        if with_interpolation:
            group['price'] = group['price'].interpolate().bfill().ffill()

        #df_ts part
        if using_df_ts:
            df_ts[(state, city, product, subproduct)] = group['price']

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
            if freq == 'day':
                group['tonnes'] = group['tonnes'].apply(lambda x: replace_nan_with(x, -1))

            pieces.append(group)

        count += 1

    print 'number of labels = ', count
    print 'number of labels with errors = ', err_count
    print 'patch series in ', (time()-start_time)/60.0, ' min.'



    #fix empty date header problem
    #df_ts.reset_index(inplace=True)
    #df_ts.columns = ['date']+list(df_ts.columns)[1:len(df_ts.columns)]
    #print df_ts.index.name


    #report
    if using_df_full:
        print 'combining'
        df_full = pd.concat(pieces)
        print 'sorting by dates'
        df_full = df_full.sort('date')
        print 'size of df_full = ', df_full.shape

    if using_df_ts:
        print 'size of df_ts = ', df_ts.shape

    return df_full, df_ts, dup_records


def extract_duplicates(group):
    df_ret = pd.DataFrame()
    dup_dates = list(group[group.duplicated('date')].date)
    for d in dup_dates:
        df_ret = df_ret.append(group[group['date']==d])
    return df_ret, dup_dates
