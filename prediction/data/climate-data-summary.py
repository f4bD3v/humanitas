'''
create a summary of the climate data
'''

import numpy as np
import pandas as pd
import glob
from datetime import date

climate_fn = glob.glob('../../data/india/climate/climate_data_*.csv')
#climate_fn = ['../../data/india/climate/climate_data_1.csv']
states_fn = '../../data/india/csv_daily/regions.csv'

def get_climate_data():
    ret = None
    for fn in climate_fn:
        if ret is None:
            ret = pd.read_csv(fn, index_col=False, na_values=['-'])
        else:
            ret.append(pd.read_csv(fn))
    ret['Location'] = ret['Location'].map(lambda x:x.replace('_', ' ').lower())
    city_to_state = pd.read_csv(states_fn, index_col=False)
    city_to_state['city'] = city_to_state['city'].map(lambda x:x.lower())
    return pd.merge(ret, city_to_state, left_on='Location', right_on='city',
            how='left')

def trimmed_mean(d, cutoff=.9):
    if not len(d):
        # TODO nans still exist, should interpolate here
        return np.nan
    return d[d <= np.percentile(d, cutoff*100.)].mean()


def main():
    data = get_climate_data()
    print data.head()
    cols = ['TM', 'Tm', 'SLP', 'H', 'PP', 'VV', 'V', 'VM']
    out = pd.DataFrame(columns=['state', 'date'] + cols)

    months = ['January', 'February', 'March', 'April', 'May', 'June',
            'July', 'August', 'September', 'October', 'November',
            'December']

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

    out.sort(['state', 'date']).to_csv('climate.csv')

if __name__ == '__main__':
    main()
