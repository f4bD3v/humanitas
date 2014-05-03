import pandas as pd
import numpy as np
import cPickle as pickle
import sys
import os
sys.path.insert(0, '../preproc')
from df_build_func import get_all_dates

na_cutoff_rate = 0.4
#csv_df_full = os.getcwd()+'/../../data/india/csv_preprocessed/wholesale_daily/india_original_wholesale_daily.csv'
csv_df_full = os.getcwd() + '/../preproc/india_original_wholesale_daily_'+str(na_cutoff_rate)+'.csv'

def subsample(df, begin_date):
    df['date'] = pd.to_datetime(df['date'])
    begin_date = pd.to_datetime(begin_date)
    return df[df['date'] >= begin_date]

def na_analysis(df):
    all_dates = get_all_dates(df,'D')
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



if __name__ == '__main__':
    df = pd.read_csv(csv_df_full)

    num_cities, best_non_na = na_analysis(df)
    num_cities.to_csv('num_cities_'+str(na_cutoff_rate)+'.csv')
    best_non_na.to_csv('best_non_na_'+str(na_cutoff_rate)+'.csv')

    df_3y = subsample(df, '2011-01-01')
    num_cities_3y, best_non_na_3y = na_analysis(df_3y)
    num_cities_3y.to_csv('num_cities_3y_'+str(na_cutoff_rate)+'.csv')
    best_non_na_3y.to_csv('best_non_na_3y_'+str(na_cutoff_rate)+'.csv')
