import pandas as pd
import numpy as np
import cPickle as pickle
import sys
import os
# sys.path.insert(0, '../preproc')
from df_build_func import get_all_dates, mod_header

description = '''
        This script is for data usability analysis

        Author: Ching-Chia
'''


na_cutoff_rate = 0.6
date_freq = 'W-Fri'
#csv_df_full = os.getcwd()+'/../../data/india/csv_preprocessed/wholesale_daily/india_original_wholesale_daily.csv'
#csv_df_full = os.getcwd() + '/../preproc/india_original_wholesale_daily_'+str(na_cutoff_rate)+'.csv'
# csv_df_full = os.getcwd() + '/../preproc/india_original_retail_daily_'+str(na_cutoff_rate)+'.csv'
#csv_df_full = os.getcwd() + '/../preproc/india_original_wholesale_weekly_0.4_downsampled.csv'
#csv_df_full = os.getcwd() + '/../preproc/india_original_wholesale_weekly_'+str(na_cutoff_rate)+'_downsampled.csv'
csv_df_full = os.getcwd() + '/../preproc/india_original_retail_weekly_'+str(na_cutoff_rate)+'_downsampled.csv'

def subsample(df, begin_date):
    df['date'] = pd.to_datetime(df['date'])
    begin_date = pd.to_datetime(begin_date)
    return df[df['date'] >= begin_date]

def na_analysis(df, date_freq):
    all_dates = get_all_dates(df,date_freq)
    all_states = list(set(df['state']))
    all_prod_subs = []
    for (product, subproduct), group in df.groupby(['product', 'subproduct']):
        if subproduct != 'Other':
            all_prod_subs.append((product, subproduct))


    num_cities = pd.DataFrame(columns=all_states, index=all_prod_subs)
    best_non_na = pd.DataFrame(columns=all_states, index=all_prod_subs)
    #find good subproduct across all regions
    for product, prod_group in df.groupby('product'):
        for subproduct, sub_group in prod_group.groupby('subproduct'):
            if subproduct != 'Other':
                for state, stat_group in sub_group.groupby('state'):
                    num_cities[state][(product, subproduct)] = stat_group.shape[0] / len(all_dates)
                    valid_counts = []
                    for city, city_group in stat_group.groupby('city'):
                        valid_counts.append(city_group['price'].count() * 1. / len(all_dates))
                    best_non_na[state][(product, subproduct)] = max(valid_counts)

    return num_cities, best_non_na


def na_analysis_by_reg_prod(df, date_freq):
    ddf = df.copy()
    if 'date' not in ddf.columns:
        ddf.reset_index(inplace=True)
        ddf.columns = mod_header(ddf.columns)

    all_dates = get_all_dates(ddf,date_freq)
    all_states = list(set(ddf['state']))
    all_products = list(set(ddf['product']))

    # ddf = ddf[ddf['subproduct']!='Other']

    num_series = pd.DataFrame(columns=all_states, index=all_products)
    best_non_na = pd.DataFrame(columns=all_states, index=all_products)
    #find good subproduct across all regions
    for product, prod_group in ddf.groupby('product'):
        for state, stat_group in prod_group.groupby('state'):
            num_series[state][product] = stat_group.shape[0] / len(all_dates)
            valid_counts = []
            for (subproduct, city), group in stat_group.groupby(['subproduct', 'city']):
                valid_counts.append(group['price'].count() * 1. / len(all_dates))
            best_non_na[state][product] = max(valid_counts)

    return num_series, best_non_na

def main():
    df = pd.read_csv(csv_df_full)

    num_cities, best_non_na = na_analysis(df, date_freq)
    num_cities.to_csv('num_cities_downsampled'+str(na_cutoff_rate)+'.csv')
    best_non_na.to_csv('best_non_na_downsampled'+str(na_cutoff_rate)+'.csv')
