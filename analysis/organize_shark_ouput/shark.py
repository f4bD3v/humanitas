import pandas as pd
import numpy as np
import os, sys
sys.path.insert(0, '../preproc')
from df_build_func import *

indicator = 'tweet_count'

fp = os.getcwd()+'/shark_out/'
fp_out = os.getcwd()+'/'+indicator+'/'

if not os.path.exists(fp_out):
    os.makedirs(fp_out)

all_states = ['Andhra Pradesh', 'Arunachal Pradesh', 'Assam', 'Bihar', \
'Chattisgarh', 'NCT of Delhi', 'Goa', 'Gujarat', 'Haryana', 'Himachal Pradesh', \
'Jammu and Kashmir', 'Jharkhand', 'Karnataka', 'Kerala', 'Madhya Pradesh', 'Maharashtra', \
'Manipur', 'Meghalaya', 'Mizoram', 'Nagaland', 'Orissa', 'Punjab', 'Rajasthan', 'Sikkim', \
'Tamil Nadu', 'Tripura', 'Uttar Pradesh', 'Uttarakhand', 'West Bengal']

def convert_to_capital(name):
    if name[0:3] == 'nct':
        name = name[0:3].upper() + name[3:]
    else:
        name = name[0].upper() + name[1:]
    name = list(name)
    after_space = False
    for i in range(1, len(name)):
        if after_space:
            if name[i:i+2] != ['o', 'f'] and name[i:i+3] != ['a', 'n', 'd']:
                name[i] = name[i].upper()
            after_space = False
        if name[i] == ' ':
            after_space = True

    name_ret = ''.join(name)
    return name_ret


def find_not_in(states, all_states):
    ret = []
    for s in states:
        if s not in all_states:
            ret.append(s)
    return ret


if __name__ == "__main__":
    file_lst = os.listdir(fp)

    pieces = []
    for file in file_lst:
        product = file[:-4]
        file = fp+file
        print file
        df_temp = pd.read_csv(file, header=0, index_col=0)
        subdf = pd.DataFrame()
        subdf['state'] = df_temp['state']
        subdf[product] = df_temp[indicator]

        pieces.append(subdf)

    df = pd.concat(pieces)

    df.reset_index(inplace=True)
    df.date = pd.to_datetime(df.date, format='%Y-%m-%d')
    df = df.sort('date')

    #convert states to the correct names
    df.state = df.state.map(convert_to_capital)

    #ignore those not in all_states
    ignore_lst = find_not_in(list(set(df.state)), all_states)
    for ig in ignore_lst:
        df = df[df.state != ig]

    #reindex and fill nan with 0
    all_dates = pd.date_range('2009-01-01', '2014-05-11')

    dup_records = []
    for state, group in df.groupby('state'):
        print state
        df_state = pd.DataFrame()

        group.set_index('date', inplace=True)
        try:
            group = group.reindex(all_dates)
        except Exception, e:
            group.reset_index(inplace=True)
            group.columns = mod_header(group.columns)
            dupdf, dup_dates = extract_duplicates(group)
            dup_records.append((state, dupdf))
            group.drop_duplicates(cols='date', inplace=True)
            #fill NaN in the missing dates again
            group.set_index('date', inplace=True)
            group = group.reindex(all_dates)

        group.fillna(0, inplace=True)
        for colname in list(group.columns):
            if colname == 'state':
                continue

            df_state[colname] = group[colname]

        df_state = df_state.astype(int)
        df_state.to_csv(fp_out+state+'.csv', index_label='date')



    df.to_csv('df.csv')
