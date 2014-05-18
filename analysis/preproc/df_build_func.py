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
        get_raw_weekly           : read india weekly csv into one big dataframe, df_raw
        get_raw_daily            : read india wholesale daily csv into one big dataframe, df_raw
        get_raw_daily_retail     : read india retail daily csv into one big dataframe, df_raw
        get_state                : read regions.csv into dataframe, df_reg
        get_data                 : join df_raw and df_reg on 'city' into df, format 'date'
                                   column into Pandas datetime format, and sort df by dates
        get_all_dates            : get all dates from the dataframe using pd.date_range
        mod_header               : replace 'index' by 'date'
        examine_fullness         : examine if df_full has all dates for all labels and if it is properly interpolated.
        examine_df_ts_fullness   : examine if df_ts has all dates for all labels and if it is properly interpolated.
        replace_nan_with         : helper
        get_piece                : unused function. patch df with missing dates manually
        get_full_data            : given df, return df_full or df_ts by option. The com-
                                   putation of both is done all at once, thus no overhead.
        extract_duplicates       : return duplicated parts and dates of a data frame
        remove_spikes            : remove suspicious spikes in datasets
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

def get_raw_daily_retail(fp_csv):
    return csv2df_bulk([fp_csv])

def get_state(fp_state):
    return pd.read_csv(fp_state)

def get_data(fp_csv, fp_state, product_lst):
    start_time = time()
    #wholesale daily
    if 'agmarknet' in fp_csv:
        if len(product_lst) == 0:
            raise Exception('empty product_lst')
        df_raw = get_raw_daily(fp_csv, product_lst)
    #retail daily
    elif 'fcainfoweb' in fp_csv:
        df_raw = get_raw_daily_retail(fp_csv)
        df_raw['subproduct'] = df_raw['subproduct'].apply(lambda x: 'None')
        df_raw['price'] = df_raw['price'].apply(lambda x: np.nan if x == 'NR' else x)
    #retail weekly
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
    if df.shape[0] == 0:
        return
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
    if df_ts.shape[0] == 0:
        return
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

def init_valid_table():
    ret = pd.DataFrame(columns=[10,20,30,40,50,60,70,80,90,100], index=['count'])
    ret.fillna(0, inplace=True)
    return ret

def get_full_data(df, all_dates, \
                    using_df_full, using_df_ts, valid_rate, with_interpolation, \
                    interpolation_method, interpolation_order, filter_lst, na_len_limit_ratio):
    start_time = time()
    pieces = []
    count = 0
    err_count = 0
    df_full = pd.DataFrame()
    df_ts = pd.DataFrame()
    valid_table = init_valid_table()
    probe = pd.Series()

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

        #wrong data
        if (state, city, product, subproduct, freq) == \
            ('West Bengal', 'Kolkata', 'Urad Dal', 'None','day'):
            print (state, city, product, subproduct, freq)
            print group[group['date'] == pd.to_datetime('2011-02-03')]
            group[group['date'] == pd.to_datetime('2011-02-03')] = np.nan

        if (state, city, product, subproduct, freq) == \
            ('Rajasthan', 'Jaipur', 'Salt Pack (Iodised)', 'None', 'day'):
            print (state, city, product, subproduct, freq)
            print group[group['date'] == pd.to_datetime('2010-05-05')]
            group[group['date'] == pd.to_datetime('2010-05-05')] = np.nan
            group[group['date'] == pd.to_datetime('2010-05-06')] = np.nan
            group[group['date'] == pd.to_datetime('2010-05-07')] = np.nan

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
                #print 'ignore empty daily subproduct',(state, city, product, subproduct, country, freq)
                #empty_subproduct.append(((state, city, product, subproduct, country, freq), group.shape))
                continue


        group.set_index('date', inplace=True)

        try:
            group = group.reindex(all_dates)
        except Exception, e:
            print 'handle exception:', (state, city, product, subproduct, country, freq)
            err_count += 1
            group.reset_index(inplace=True)
            group.columns = mod_header(group.columns)
            dupdf, dup_dates = extract_duplicates(group)
            dup_records.append(((state, city, product, subproduct, country, freq), dupdf))

            # if freq == 'week':
            #     continue
            # else:
            # #handle duplicates of daily datasets
            group.drop_duplicates(cols='date', inplace=True)
            #fill NaN in the missing dates again
            group.set_index('date', inplace=True)
            group = group.reindex(all_dates)
            #print 'duplicate handled, new length', group.shape[0], '/', len(all_dates)

        #skip those with less valid data rate than valid_rate
        if group['price'].count() * 1. / len(all_dates) < valid_rate:
            continue

        #convert str to float
        group['price'] = group['price'].astype(float)
        #remove suspicious spikes
        # probe = group.copy()
        #break
        group['price'] = remove_spikes_series(group['price'], 100)

        max_nan_len = get_max_nan_len(group['price'])
        if max_nan_len > na_len_limit_ratio*len(all_dates):
            print (state, city, product, subproduct), max_nan_len, 'exceeds max consecutive NaN length', '*********************************************'
            continue


        if with_interpolation:
            group['price'] = group['price'].interpolate(method=interpolation_method, order=interpolation_order).bfill().ffill()


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

    return df_full, df_ts, dup_records, valid_table, probe


def extract_duplicates(group):
    df_ret = pd.DataFrame()
    dup_dates = list(group[group.duplicated('date')].date)
    for d in dup_dates:
        df_ret = df_ret.append(group[group['date']==d])
    return df_ret, dup_dates


def remove_spikes(df_ts, threshold):
    ddf = df_ts.copy()
    ddf_ret = get_ret(ddf)

    ddf = ddf[ddf_ret<threshold]
    ddf_ret = ddf_ret[ddf_ret<threshold]
    ddf = ddf[ddf_ret > -threshold]
    ddf_ret = ddf_ret[ddf_ret > -threshold]

    return ddf

def get_ret(df_ts):
    ret = pd.DataFrame()
    for label in list(df_ts.columns):
        s = df_ts[label]/df_ts[label].shift(1) - 1
        ret[label] = s

    return ret* 100



def remove_spikes_series(series, threshold):
    ddf = series.copy()
    ddf_ret = get_ret_series(ddf)

    ddf = ddf[ddf_ret<threshold]
    ddf_ret = ddf_ret[ddf_ret<threshold]
    ddf = ddf[ddf_ret > -threshold]
    ddf_ret = ddf_ret[ddf_ret > -threshold]

    return ddf


def get_ret_series(series):
    #print series.head()
    ret = series/series.shift(1) - 1

    return ret* 100


def get_max_nan_len(series):
    bool_series = series >= 0
    max_len = 0
    current_len = 0
    for idx in list(bool_series.index):
        if bool_series[idx] == False:
            current_len += 1
        else:
            current_len = 0

        if current_len > max_len:
            max_len = current_len

    return max_len
