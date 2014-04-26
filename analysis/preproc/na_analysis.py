import cPickle as pickle
import numpy as np
import pandas as pd


pk_in = 'india_week_df_full.pickle'


def len_longest_na(series):
    len_na = 0
    longest = 0
    for elem in series.iteritems():
        if np.isnan(elem[1]):
            len_na = len_na+1
        else:
            len_na=0
        if len_na > longest:
            longest = len_na
    return longest

def na_analysis(df):
    all_cities = list(set(df['city']))
    all_states = list(set(df['state']))
    #all_prod_subs =
    na_table = pd.DataFrame(columns=all_states, index=all_prod_subs)
    nalen_table = pd.DataFrame(columns=all_states, index=all_prod_subs)

    for key in na_record.keys():
        (prod, sub, city) = key
        if isinstance(sub, str):
            na_table[city][(prod,sub)] = na_record[key][0]
            nalen_table[city][(prod,sub)] = na_record[key][1]
        else:
            na_table[city][(prod, ' ')] = na_record[key][0]
            nalen_table[city][(prod,' ')] = na_record[key][1]

    return na_table, nalen_table


if __name__ == '__main__':
    with open(pk_in, 'rb') as f:
        df = pickle.load(f)
    print "df loaded in"

    #na_table, nalen_table = na_analysis(df)
