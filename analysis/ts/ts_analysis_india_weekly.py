import sys
sys.path.insert(0, '../common')
from csv_to_df import *
from time import time
import os

if __name__ == "__main__":
    fp_lst = []
    for i in range(2005,2015):
        fp_lst.append("{}{}{}{}".format(os.environ['HOME'],"/work/india_data/all_commodities_weekly_india_",i,".csv"))

    df = csv2df_bulk(fp_lst)

    # sample query: find fine rice price at city Mumbai for the whole period (2005-2014)
    q = df.query('product=="Rice" & sub=="Fine" & city=="Mumbai"')
