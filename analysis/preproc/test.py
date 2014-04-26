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
    print 'formatting dates'
    df['date'] = pd.to_datetime(df['date'], format='%d/%m/%Y')
    print("Cities not joined with states: "+str(list(set(df_raw["city"]) - set(df_reg["city"]))))
    print "{} {} {}".format("csv loaded into df in",(time()-start_time),'secs.')
    print "{} {}".format("size of df =", df.shape)
    return df

def get_state():
    return pd.read_csv(fp_state)

def get_all_dates(df):
    all_dates_raw = sorted(list(set(df['date'])))
    return pd.date_range(all_dates_raw[0], all_dates_raw[-1],freq=date_freq)

def mod_header(cols):
    cols = list(cols)
    cols[cols=='index'] = 'date'
    return cols

def flatten(df, one = False):
    df_ts = pd.DataFrame()
    for (state, city, product, subproduct), group in \
            df.groupby(['state', 'city','product','subproduct']):
        group.set_index('date', inplace=True)
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

def get_full_data(df, all_dates, verbose=False):
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
        # print missing_dates
        # print len(all_dates), len(group['date']), len(missing_dates)
        # break
        missing_piece = get_piece(missing_dates, group.iloc[0,])
        pieces.append(missing_piece)

        d = group.copy()
        group.set_index('date', inplace=True)
        group.reindex(all_dates)
        print group.head()
        print group.tail()

        break

    print 'number of labels = ', count
    print 'find all missing pieces in ', (time()-start_time)/60.0, ' min.'

    print 'combining'
    df_full = pd.concat([df]+pieces)
    print 'sorting by dates'
    #df_full['date'] = pd.to_datetime(df_full['date'], format = '%d/%m/%Y')
    df_full = df_full.sort('date')
    print 'size of df_full = ', df_full.shape

    return df_full
    
def replace_nan_with(x, t):
    return x if isinstance(x, str) or isinstance(x, int) else t


def main():
    df = get_data()
    all_dates = get_all_dates(df)
    df_full = get_full_data(df, all_dates)
    #examine_fullness(df_full, len(all_dates))

    with open(pk_out, 'wb') as f:
        pickle.dump(df_full, f)

    df_full.to_csv(csv_out1)
    flatten(df_full, one=True).to_csv(csv_out2)

if __name__ == '__main__':
    #main()

    df = get_data()
    all_dates = get_all_dates(df)

    #fill NaN into missing dates
    #by generating missing date data
    #and combining them with df

    pieces = []
    start_time = time()
    count = 0
    verbose = False
    for (state, city, product, subproduct, country, freq), group in \
            df.groupby(['state', 'city','product','subproduct', 'country', 'freq']):

        count += 1
        if verbose or (count % 1000 == 1):
            print count, (state, city, product, subproduct)
        #
        # missing_dates = list(set(all_dates) - set(group['date']))
        # # print missing_dates
        # # print len(all_dates), len(group['date']), len(missing_dates)
        # # break
        # missing_piece = get_piece(missing_dates, group.iloc[0,])
        group.set_index('date', inplace=True)
        try:
            group = group.reindex(all_dates)
        except:
            print (state, city, product, subproduct), 'dup dates'

        group.reset_index(inplace=True)
        group.columns = mod_header(group.columns)

        group['freq'] = group['freq'].apply(lambda x: replace_nan_with(x, freq))
        group['country'] = group['country'].apply(lambda x: replace_nan_with(x, country))
        group['city'] = group['city'].apply(lambda x: replace_nan_with(x, city))
        group['product'] = group['product'].apply(lambda x: replace_nan_with(x, product))
        group['subproduct'] = group['subproduct'].apply(lambda x: replace_nan_with(x, subproduct))
        group['state'] = group['state'].apply(lambda x: replace_nan_with(x, state))

        pieces.append(group)
        break

    print 'number of labels = ', count
    print 'find all missing pieces in ', (time()-start_time)/60.0, ' min.'

    print 'combining'
    df_full = pd.concat([df]+pieces)
    print 'sorting by dates'
    #df_full['date'] = pd.to_datetime(df_full['date'], format = '%d/%m/%Y')
    df_full = df_full.sort('date')
    print 'size of df_full = ', df_full.shape
