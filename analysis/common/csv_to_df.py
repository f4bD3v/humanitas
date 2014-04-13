import csv
import string
import pandas as pd
from time import time
from collections import namedtuple

DataTuple = namedtuple('DataTuple', 'date freq country city product sub price')

def get_usage():
    usage_str = """
        csv2df     : read one csv file to one dataframe
        csv2df_bulk: read a sequence of csv files to one big dataframe

        query usage (need to install numexpr)
        df.query('product == "Rice"')
        df.query('product == "Rice" & city == "Asansol"')
        all queries return a 2-column dataframe containing date and price, sorted by date
    """
    return usage_str

def csv2df(file_path, bulk=False):
    print 'loading '+file_path
    df = pd.read_csv(file_path, header=None)
    df.columns = ['date', 'freq', 'country', 'city', 'product', 'sub', 'price']
    df.set_index(['product','sub','country','city','freq'], inplace=True)
    if bulk == False:
        df['date'] = pd.to_datetime(df['date'])
        df = df.sort('date')
    return df

def csv2df_bulk(fp_lst):
    is_first = True
    start_time = time()
    for file_path in fp_lst:
        if is_first == True:
            df_bulk = csv2df(file_path, True)
            is_first = False
        else:
            df_bulk = df_bulk.append(csv2df(file_path, True))
    print "organizing by dates"
    df_bulk['date'] = pd.to_datetime(df_bulk['date'])
    print "sorting by dates"
    df_bulk = df_bulk.sort('date')
    print "{} {} {}".format("csv loaded into df in",(time()-start_time),'secs.')
    print "{} {}".format("size of df =", df_bulk.shape)
    return df_bulk
