from csv_to_df import csv2df_bulk
import os
import cPickle as pickle
from time import time
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import sys

initialize = False
fp = os.getcwd()+'/../../data/india/csv_weekly/rpms.dacnet.nic.in/all_commodities_weekly_india_'
pk_in = 'all_India_week.pickle'
pk_out = 'all_India_week_timeseries.pickle'
date_freq = 'W-FRI'

all_dates = []
all_cities = []
all_products = []
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

    if initialize:
        df = csv2df_bulk(fp_lst)
        with open(pk_in, 'w') as f:
            pickle.dump([df],f)
        print "df dumped to "+pk_in
        sys.exit(0)

    with open(pk_in) as f:
        [df] = pickle.load(f)
    print pk_in+' is loaded.'

    # query Fine Rice in Mumbai:
    # df[(df['product']=='Rice') & (df['city']=='Mumbai') & (df['sub']=='Fine')]

    #generate metadata: all_dates, all_cities...
    all_dates_raw = sorted(list(set(df['date'])))
    all_dates = pd.date_range(all_dates_raw[0], all_dates_raw[-1],
            freq=date_freq)
    date_diff = list(set(all_dates) - set(all_dates_raw))
    all_cities = sorted(list(set(df['city'])))
    all_products = sorted(list(set(df['product'])))
    prod_set = set(df['product'])
    all_prod_subs = {}
    for prod in prod_set:
        subs = list(set(df[df['product']==prod]['subproduct']))
        #if isinstance(sub_lst.iloc[0], str):
        #    subs = list(set(sub_lst))
        #elif np.isnan(sub_lst.iloc[0]):
        #    subs = [float('nan')]
        #else:
        #    raise Exception('type other than str or NaN')
        if prod not in all_prod_subs:
            all_prod_subs[prod] = set()
        all_prod_subs[prod].update(subs)
    
    print 'Elapsed time phase 1: '+str(time()-start_time)+' sec'

    # build up dataframe where columns are time serieses
    df_ts = pd.DataFrame()
    df_mulidx = df.set_index(['product','subproduct','city'])
    validcounts = []
    empty_label = []
    reindex_total_time = 0.
    setindex_total_time = 0.
    query_total_time = 0.
    for product, subproducts in all_prod_subs.iteritems():
        product_df = df_mulidx[df_mulidx.product == product,:]
        for subproduct in subproducts:
            subproduct_df = product_df[product_df.subproduct == subproduct,:]
            for city in all_cities:
                subdf = subproduct_df[subproduct_df.city == city]
                #if isinstance(subproduct, str):
                #    predicate = 'product=="{}" & subproduct=="{}" & city=="{}"'.format(product, subproduct, city)
                #else:
                #    predicate = 'product=="{}" & city=="{}"'.format(product, city)
                label = (product,subproduct,city)

                #crt_time = time()
                #subdf = df_mulidx.query(predicate)
                #query_total_time += time()-crt_time
                #print '@df_mulidx.query: %.2fs total: %.2fs' % (
                #    time()-crt_time, query_total_time)

                if subdf.shape[0] == 0:
                    empty_label.append(label)
                    #validcounts.append(0)
                else:
                    
                    crt_time = time()
                    subdf.set_index('date', inplace=True)
                    setindex_total_time += time()-crt_time
                    print '@subdf.set_index: %.2fs total: %.2fs' % (
                        time()-crt_time, setindex_total_time)
                    try:
                        crt_time = time()
                        subdf = subdf.reindex(all_dates)
                        reindex_total_time += time()-crt_time
                        print '@subdf.reindex: %.2fs total: %.2fs' % (
                            time()-crt_time, reindex_total_time)
                    except: #handle series with duplicate dates
                        print str(label)+ ' has duplicated dates.'
                        continue
                        subdf.reset_index(inplace=True)
                        dupdf = extract_duplicates(subdf)
                        dup_records.append((label, dupdf))
                        dup_dates = list(set(dupdf['date']))
                        non_dup_index = subdf['date'].map(lambda x: x not in dup_dates)
                        subdf = subdf[non_dup_index]
                        subdf.set_index('date', inplace=True)
                        subdf = subdf.reindex(all_dates)
                    df_ts[label] = subdf['price']
                    #validcounts.append(subdf.count().price)

    with open(pk_out, 'w') as f:
        pickle.dump([df_ts, validcounts, dup_records, all_dates, all_cities, all_products, all_prod_subs], f)
    print 'Everything dumped to '+pk_out

    print 'Elapsed time: '+str(time()-start_time)+' sec'
