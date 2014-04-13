from csv_to_df import csv2df_bulk
import os

if __name__ == "__main__":
    fp_lst = []
    for i in range(2013,2015):
        fp_lst.append("{}{}{}{}".format(os.environ['HOME'],"/work/india_data/all_commodities_weekly_india_",i,".csv"))

    df = csv2df_bulk(fp_lst)

    # sample query: find fine rice price at city Mumbai for whole range of period (2013-2014 as above)
    q = df.query('product=="Rice" & sub=="Fine" & city=="Mumbai"')
