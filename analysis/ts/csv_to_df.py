import sys
sys.path.insert(0, '../common')
from csv_to_df import csv2df_bulk
import os
import pickle

fp = os.environ['HOME']+"/work/india_data/all_commodities_weekly_india_"
pk = 'all_India_week.pickle'

if __name__ == "__main__":
    fp_lst = []
    for i in range(2005,2015):
        fp_lst.append("{}{}{}".format(fp,i,".csv"))

    df = csv2df_bulk(fp_lst)

    # sample query: find fine rice price at city Mumbai for whole range of period (2013-2014 as above)
    #q = df.query('product=="Rice" & sub=="Fine" & city=="Mumbai"')

    with open(pk, 'w') as f:
        pickle.dump([df],f)

    print "df dumped to "+pk
