import sys
sys.path.insert(0, '../common')
from csv_to_df import csv2df_bulk
import os
import pickle
from time import time
import numpy as np
import pandas as pd

fp = os.environ['HOME']+"/work/india_data/all_commodities_weekly_india_"
pk_in = 'all_India_week.pickle'
pk_out = 'all_India_week_timeseries.pickle'

all_dates = []
all_cities = []
all_products = []
all_prod_subs = []
dup_records = []

def get_subs_of(prod):
    subs = []
    for pair in all_prod_subs:
        if pair[0] == prod:
            subs.append(pair[1])
    return subs

def extract_duplicates(subdf):
    df_ret = pd.DataFrame()
    dup_dates = list(subdf[subdf.duplicated('date')].date)
    for d in dup_dates:
        df_ret = df_ret.append(subdf[subdf['date']==d])
    return df_ret

if __name__ == "__main__":
    start_time = time()

    fp_lst = []
    for i in range(2005,2015):
        fp_lst.append("{}{}{}".format(fp,i,".csv"))

    #df = csv2df_bulk(fp_lst)
    #with open(pk_in, 'w') as f:
    #    pickle.dump([df],f)
    #print "df dumped to "+pk_in

    with open(pk_in) as f:
        [df] = pickle.load(f)
    print pk_in+' is loaded.'

    # query Fine Rice in Mumbai:
    # df[(df['product']=='Rice') & (df['city']=='Mumbai') & (df['sub']=='Fine')]

    #generate metadata: all_dates, all_cities...
    all_dates = sorted(list(set(df['date'])))
    all_cities = sorted(list(set(df['city'])))
    all_products = sorted(list(set(df['product'])))
    prod_set = set(df['product'])
    for prod in prod_set:
        sub_lst = df[df['product']==prod]['sub']
        if isinstance(sub_lst.iloc[0], str):
            subs = list(set(sub_lst))
        elif np.isnan(sub_lst.iloc[0]):
            subs = [float('nan')]
        else:
            raise Exception('type other than str or NaN')
        prods = [prod]*len(subs)
        all_prod_subs = all_prod_subs + zip(prods, subs)
    all_prod_subs = sorted(all_prod_subs)


    # build up dataframe where columns are time serieses
    df_ts = pd.DataFrame()
    df_mulidx = df.set_index(['product','sub','country','city','freq'])
    validcounts = []
    empty_label = []
    for prod_sub in all_prod_subs:
        for city in all_cities:
            predicate = 'product=="{}" & sub=="{}" & city=="{}"'.format(prod_sub[0], prod_sub[1], city)
            label = (prod_sub[0],prod_sub[1],city)
            subdf = df_mulidx.query(predicate)

            if subdf.shape[0] == 0:
                empty_label.append(label)
                validcounts.append(0)
            else:
                subdf.set_index('date', inplace=True)
                try:
                    subdf = subdf.reindex(all_dates)
                except: #handle series with duplicate dates
                    print str(label)+ ' has duplicated dates.'
                    subdf.reset_index(inplace=True)
                    dupdf = extract_duplicates(subdf)
                    dup_records.append((label, dupdf))
                    dup_dates = list(set(dupdf['date']))
                    non_dup_index = subdf['date'].map(lambda x: x not in dup_dates)
                    subdf = subdf[non_dup_index]
                    subdf.set_index('date', inplace=True)
                    subdf = subdf.reindex(all_dates)
                df_ts[label] = subdf['price']
                validcounts.append(subdf.count().price)

    with open(pk_out, 'w') as f:
        pickle.dump([df_ts, validcounts, dup_records, all_dates, all_cities, all_products, all_prod_subs], f)
    print 'Everything dumped to '+pk_out

    print 'Elapsed time: '+str(time()-start_time)
