import pandas as pd
import numpy as np
from datetime import datetime
import matplotlib.pyplot as plt

data = pd.read_csv('../../../data/india/inflation/inflation_data.csv',
        index_col=False, na_values=['-'])

data.columns = ['date', 'monthly', 'date2', 'yearly']

del data['date2']
del data['yearly']

def fmt_date(x):
    x = x.split(' -')[0]
    return datetime.strptime(x, '%B %Y')

data['date'] = data['date'].map(fmt_date).astype(pd.datetime)

data['monthly'] = data['monthly'].map(
        lambda x:str(x).replace('%','')).astype(np.float64)

data.set_index(data['date'], inplace=True)
data.sort(['date'], inplace=True)
data['monthly'] = data['monthly'].cumsum()

data.to_csv('../../../data/india/inflation/inflation_data_processed.csv')

print data

#data['monthly'].plot()
data.plot()
#pd.Series(data['monthly'], index=data['date']).plot()
plt.show()
