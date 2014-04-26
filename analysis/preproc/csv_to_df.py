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
    pieces = []
    for file_path in fp_lst:
        print 'loading '+file_path
        pieces.append(pd.read_csv(file_path))
    df_bulk = pd.concat(pieces)
    
    return df_bulk
