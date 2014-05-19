'''
create a summary of the climate data
'''

import numpy as np
import pandas as pd
import glob
import sys
from datetime import date

climate_fn = glob.glob('../../data/india/climate/climate_data_*.csv')
#climate_fn = ['../../data/india/climate/climate_data_1.csv']
states_fn = '../../data/india/csv_daily/regions.csv'

city_typos = {
    'ramgundam': 'ramagundam',
    'madras minambakkam': 'madras meenambakkam',
    'poona': 'pune',
}
city2state = {
    'ramagundam': 'Andhra Pradesh',
    'minicoy': 'Lakshadweep',
    'pbo raipur': 'Chhattisgarh',
    'madras meenambakkam': 'Tamil Nadu', # ??
    'nagpur sonegaon': 'Maharashtra',
    'new delhi safdarjung': 'South Delhi',
}


def _get_state_from_city(badcity, data):
    #print 'trying for',badcity
    exact = data['city'] == badcity
    matches = sum(exact)
    if matches == 1:
        ret = data[exact]['state'].iloc[0]
        return ret
    assert matches < 2

    # get longest word idx
    city = badcity.split(' ')
    i = np.argmax(map(len, city))
    city = city[i]
    heuristic = data['city'].map(lambda x: city in x)
    if sum(heuristic):
        ret = data[heuristic]['state']

        if len(ret) > 1:
            print 'multiple matches on heuristic',data[heuristic]
            return ''
        elif len(ret) == 1:
            #print 'heuristic match of',city,'with',ret.iloc[0]
            return ret.iloc[0]
    #print 'no match for',badcity,'or',city
    return ''

def get_state_from_city(badcity, data):
    if badcity in city_typos:
        badcity = city_typos[badcity]
    if badcity not in city2state:
        city2state[badcity] = _get_state_from_city(badcity, data)
        print 'State(%s) = %s' % (badcity, city2state[badcity])
    return city2state[badcity]


def get_climate_data():
    ret = None
    for fn in climate_fn:
        if ret is None:
            ret = pd.read_csv(fn, index_col=False, na_values=['-'])
        else:
            ret.append(pd.read_csv(fn, index_col=False, na_values=['-']))

    print ret.shape

    city_to_state = pd.read_csv(states_fn, index_col=False)
    city_to_state['city'] = city_to_state['city'].map(lambda x:x.lower())
    ret['state'] = ret['Location'].map(lambda x:
            get_state_from_city(x.replace('_', ' ').lower(), city_to_state))
    #return pd.merge(ret, city_to_state, left_on='Location', right_on='city',
    #        how='left')
    return ret

def trimmed_mean(d, cutoff=.9):
    if not len(d):
        # TODO nans still exist, should interpolate here
        return np.nan
    return d[d <= np.percentile(d, cutoff*100.)].mean()


def main():
    data = get_climate_data()
    print data.head()
    cols = ['T', 'TM', 'Tm', 'SLP', 'H', 'PP', 'VV', 'V', 'VM']
    out = pd.DataFrame(columns=['state', 'date'] + cols)

    months = ['January', 'February', 'March', 'April', 'May', 'June',
            'July', 'August', 'September', 'October', 'November',
            'December']

    print 'states discovered:',data['state'].unique()

    for group, subdata in data.groupby(['state', 'Year', 'Month']):
        month = 1 + months.index(group[2])
        row = [group[0], date(int(group[1]), month, 1)]
        for i, col in enumerate(cols):
            mean = trimmed_mean(subdata[col].dropna())
            if np.isnan(mean):
                if month != 1 and not np.isnan(prevrow[i + 2]):
                    mean = prevrow[i+2]
                else:
                    print 'could not solve nan for',group,col, \
                            'filling with overall average'
                    mean = trimmed_mean(
                        data.query('Year == "%s" and Month == "%s"' %
                            (group[1], group[2])), .7)
            row.append(mean)
        prevrow = row
        out.loc[len(out)] = row

    out.sort(['state', 'date']).reset_index().drop('index',1).to_csv('../../data/india/climate/climate_processed.csv')

if __name__ == '__main__':
    main()
