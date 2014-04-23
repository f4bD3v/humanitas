import matplotlib.pyplot as plt
import pickle
import pandas as pd
import numpy as np
from time import time

product = 'Rice'
country = 'India'
freq = 'week'
pk_source = '%s_%s_%s.pickle' %(product, country, freq)
pk_target = 'nacounter.pickle'

def after_date(all_dates, date):
    i=len(all_dates)-1
    while(i>=0):
        if all_dates[i] <= pd.to_datetime(date):
            return all_dates[i:]
        i = i-1
    raise

if __name__ == "__main__":
    with open(pk_source) as f:
        [df_prod, subdf_lst, subs, labels, all_dates, all_cities, all_products, all_subs] = pickle.load(f)
    print pk_source+" is loaded into workspace"


    #count na's in each series
    start_time = time()
    nacounts = []
    nacounts_5y = []
    nacounts_bydate = [0]*len(all_dates)
    for subdf in subdf_lst:
        subdf_5y = subdf[subdf['date'] > '2009-01-01']
        length = subdf.shape[0]
        length_5y = subdf_5y.shape[0]
        if length != 0:
            nacounts.append(length - subdf.count().price)
            nacounts_5y.append(length_5y - subdf_5y.count().price)
            subdf_one = subdf.fillna(-1)
            for i in range(0, len(all_dates)):
                if subdf_one.iloc[i].price == -1.0:
                    nacounts_bydate[i] = nacounts_bydate[i] + 1
        else:
            nacounts.append(0)
            nacounts_5y.append(0)

    print "Elapsed time = "+str(time()-start_time)

    df_na = pd.DataFrame(nacounts, index=labels, columns=['#NaN'])/len(all_dates)*100
    df_na_5y = pd.DataFrame(nacounts_5y, index=labels, columns=['#NaN'])/len(after_date(all_dates, '2009-01-01'))*100
    df_na_bydate = pd.DataFrame(nacounts_bydate, index=all_dates, columns=['#NaN'])/ (len(subs)*len(all_cities))*100
