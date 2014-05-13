import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from df_build_func import get_all_dates, mod_header
from time import time


usage = '''
        This script downsamples a daily dataset to a weekly one (on Fridays).
        Then apply NaN analysis on it.

'''

# csv_in = os.getcwd()+'/../../data/india/csv_preprocessed/preproc_wholesale_daily/india_original_wholesale_daily_0.4.csv'
# csv_out = os.getcwd()+'/../../data/india/csv_preprocessed/india_original_wholesale_weekly_0.4_downsampled.csv'
# csv_in = os.getcwd()+'/india_original_wholesale_daily_0.6.csv'
# csv_out = os.getcwd()+'/india_original_wholesale_weekly_0.6_downsampled.csv'
csv_in = os.getcwd()+'/india_original_retail_daily_0.4.csv'
csv_out = os.getcwd()+'/india_original_retail_weekly_0.4_downsampled.csv'
#set_first_friday = '2005-01-07' #for wholesale daily
set_first_friday = '2009-01-02' #for retail daily

# def downsample(df):


if __name__ == "__main__":
    start_time = time()
    df = pd.read_csv(csv_in)
    df['date'] = pd.to_datetime(df['date'])

    all_dates = sorted(list(set(df['date'])))
    print 'date starting from', all_dates[0]
    first_friday = pd.to_datetime(set_first_friday, format='%Y-%m-%d')
    idx_first_friday = all_dates.index(first_friday)
    print 'please verify first friday ==', set_first_friday

    ddf = pd.DataFrame()
    # ddf_ts = pd.DataFrame()
    rows = []
    count = 0
    df.set_index('date',inplace=True)

    for (state, city, product, subproduct, country, freq), group in \
            df.groupby(['state', 'city','product','subproduct', 'country', 'freq']):

        print (state, city, product, subproduct, country, freq)
        #sum up all dates from Sat to Fri
        #count non-NaNs
        #take the average
        i = idx_first_friday+1
        # pieces = []

        while(i < len(all_dates)):
            if(i+7 > len(all_dates)):
                break
            j = i+7
            avg_price = group.loc[all_dates[i:j]].mean(skipna=True).price
            friday = all_dates[j-1]

            #for ddf_ts
            # pieces.append(pd.DataFrame([avg_price], index=[friday]))

            #for ddf
            row = group.loc[[friday],:].copy() #small trick to return DataFrame instead of Series
            row.price = avg_price
            row.reset_index(inplace=True)
            row.columns = mod_header(row.columns)
            rows.append(row)

            # print all_dates[i:j]
            i += 7

        # ddf_ts[(state, city, product, subproduct)] = pd.concat(pieces)[0]
        count += 1

    ddf = pd.concat(rows)
    ddf['date'] = pd.to_datetime(ddf['date'])
    ddf = ddf.sort('date')
    ddf.to_csv(csv_out, index=False)
    print 'Elapsed time:', (time()-start_time)/60., 'minutes'
