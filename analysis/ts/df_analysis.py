import pickle
import sys
from contextlib import contextmanager
import pandas as pd
import matplotlib.pyplot as plt

pk_in = 'all_India_week_timeseries.pickle'
pk_out = ''

@contextmanager
def redirected(stdout):
    saved_stdout = sys.stdout
    sys.stdout = open(stdout, 'w')
    yield
    sys.stdout = saved_stdout

def filter(vcounts, threshold):
    ret = 0
    for c in vcounts:
        if c >= threshold:
            ret = ret+1
    return ret

def plot_by_product(df_ts, product):
    labels = []
    for label in df_ts.columns:
        if label[0] == product:
            labels.append(label)

    df_ts[labels].plot(title = '5 percent na cutoff rate: '+product+', #labels='+str(len(labels)), legend=False)



if __name__ == '__main__':
    with open(pk_in) as f:
        [df_ts, validcounts, dup_records, all_dates, all_cities, all_products, all_prod_subs] = pickle.load(f)
    print pk_in+' is loaded'



    with redirected(stdout='dup.txt'):
        print dup_records
    print 'dup_records saved to dup.txt'

    with redirected(stdout='validcounts.txt'):
        print validcounts
    print 'validcounts saved to validcounts.txt'

    leng = [len(all_dates), len(all_dates[(len(all_dates)/2-38):])]
    start_dates = ['2005-01', '2009-01']
    df_ts_0 = [pd.DataFrame(), pd.DataFrame()]
    df_ts_5 = [pd.DataFrame(), pd.DataFrame()]
    df_ts_10 = [pd.DataFrame(), pd.DataFrame()]

    labels = [df_ts.columns[0]]
    thrsh = [0, 0.05, 0.1]

    for label in df_ts.columns:
        for i in range(0,2):
            series = df_ts[label].loc[start_dates[i]:]
            nacount = float(leng[i] - series.count())/leng[i]
            if nacount == thrsh[0]:
                df_ts_0[i][label] = series
            if nacount <= thrsh[1]:
                df_ts_5[i][label] = series
            if nacount <= thrsh[2]:
                df_ts_10[i][label] = series

    print "2005-2014"
    print "na cutoff rate "+str(thrsh[0])+", #series="+str(df_ts_0[0].shape[1])
    print "na cutoff rate "+str(thrsh[1])+", #series="+str(df_ts_5[0].shape[1])
    print "na cutoff rate "+str(thrsh[2])+", #series="+str(df_ts_10[0].shape[1])


    print "2009-2014"
    print "na cutoff rate "+str(thrsh[0])+", #series="+str(df_ts_0[1].shape[1])
    print "na cutoff rate "+str(thrsh[1])+", #series="+str(df_ts_5[1].shape[1])
    print "na cutoff rate "+str(thrsh[2])+", #series="+str(df_ts_10[1].shape[1])

    #interpolate missing data
    #for i in range(0,2):
    #    df_ts_5[i] = df_ts_5[i].interpolate() #can't use inplace for interpolate, might be a Pandas bug
    #    df_ts_10[i] = df_ts_10[i].interpolate()

    #plot time series
    #for i in range(0,2):
        #for k in range(0,df_ts_5[i].shape[1]/5):
        #    df_ts_5[i].ix[:,k*5:min(k*5+4, df_ts_5[i].shape[1]-1)].plot(title='df_ts_5')
    plot_by_product(df_ts_5[0], 'Rice')
    plot_by_product(df_ts_5[0], 'Wheat')
    plot_by_product(df_ts_5[0], 'Chicken')

    #generate weekly return dataframes
    df_ret_0 = [df_ts_0[0]/df_ts_0[0].shift(1)-1, df_ts_0[1]/df_ts_0[1].shift(1)-1]
    df_ret_5 = [df_ts_5[0]/df_ts_5[0].shift(1)-1, df_ts_5[1]/df_ts_5[1].shift(1)-1]
    df_ret_10 = [df_ts_10[0]/df_ts_10[0].shift(1)-1, df_ts_10[1]/df_ts_10[1].shift(1)-1]


    plt.show()
