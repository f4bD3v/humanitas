import csv
import string
import pandas as pd
from time import time
from collections import namedtuple

DataTuple = namedtuple('DataTuple', 'date freq country city product sub price')

def get_usage():
    usage_str = """
        csv2df_bulk: read a sequence of csv files to one big dataframe
    """
    return usage_str


def csv2df_bulk(fp_lst):
    start_time = time()
    is_first = True
    for file_path in fp_lst:
        print 'loading '+file_path
        if is_first == True:
            df_bulk = pd.read_csv(file_path)
            is_first = False
        else:
            df_bulk = df_bulk.append(pd.read_csv(file_path))
    print "{} {} {}".format("csv loaded into df in",(time()-start_time),'secs.')
    print "{} {}".format("size of df =", df_bulk.shape)
    return df_bulk
