import csv
import string
import pandas as pd
from time import time
from collections import namedtuple

description = '''
                This script converts a list of csv files into one dataframe

                Author: Ching-Chia
'''

def csv2df(file_path, bulk=False):
    print 'loading '+file_path
    df = pd.read_csv(file_path)
    #df.columns = ['date', 'freq', 'country', 'city', 'product', 'sub', 'price']
    #df.set_index(['product','sub','country','city','freq'], inplace=True)
    df.subproduct.fillna('', inplace=True)
    if bulk == False:
        df['date'] = pd.to_datetime(df['date'])
        df = df.sort('date')
    return df

def csv2df_bulk(fp_lst):
    pieces = []
    for file_path in fp_lst:
        print 'loading '+file_path
        pieces.append(pd.read_csv(file_path))
    df_bulk = pd.concat(pieces)
    df_bulk.subproduct.fillna('', inplace=True)

    return df_bulk
