import pandas as pd
import numpy as np
import os

description = '''
        This script converts CPI inflation rates into usable format for discounting price series

        Author: Ching-Chia
'''
csv_in = os.getcwd()+'/../../data/india/inflation/inflation_data_processed.csv'


if __name__ == '__main__':
    inf = pd.read_csv(csv_in)
    inf.date = pd.to_datetime(inf.date)
    inf.set_index('date', inplace=True)
    inf = pd.DataFrame(inf.iloc[:,1])
    inf.columns = ['inflation_for_discount']
    inf = inf[inf.index >= '2005-01-01']

    inf2 = inf/inf.shift(1)
    inf2.iloc[0,0] = 1.0

    inf3 = inf2.cumprod(axis=0)

    all_dates = pd.date_range('2005-01-01', '2014-03-31', freq='D')
    inf3 = inf3.reindex(all_dates)
    inf3 = inf3.interpolate()
