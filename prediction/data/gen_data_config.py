import pandas as pd
from gen_data import *


retail_daily_fn = '../../data/india/csv_preprocessed/preproc_retail_daily/india_timeseries_retail_daily_interpolated_0.4.csv'

#wholesale_daily_fn = '../../data/india/csv_preprocessed/preproc_wholesale_daily/india_timeseries_wholesale_daily_interpolated_0.4.csv'
wholesale_daily_fn = '../esn/good_series_wholesale_daily.csv'

series_fn = wholesale_daily_fn

inflation_fn = '../../data/india/inflation/inflation_data_processed.csv'

climate_fn = '../../data/india/climate/climate_processed.csv'

oilprices_fn = '../../data/oil/international_oilprices.csv'

# first one must be state, order of rest don't matter
good_series = [
    ('NCT of Delhi', 'Najafgarh', 'Wheat', 'Dara'),
]

print 'loading series...'
all_series = pd.read_csv(series_fn, parse_dates=['date'])
print 'loading climate data...'
climate = pd.read_csv(climate_fn, parse_dates=['date'])
print 'loading inflation data...'
inflation = pd.read_csv(inflation_fn, parse_dates=['date'])
print 'loading oil data...'
oil = pd.read_csv(oilprices_fn, parse_dates=['date'], index_col=False)

price_jump = 4
series_frequency = str(price_jump) + 'D'
series_type = 'wholesale-daily'

# XXX override the regular series_range to get rid of some very new data, for
# which we do not have oil data
end = min(oil['date'].max(), inflation['date'].max(), climate['date'].max())
print 'series starting at',all_series['date'].min()
print 'series ending at',all_series['date'].max()
print 'other data ending as early as',end
series_range = pd.date_range(all_series['date'].min(),
                             end,
                             freq=series_frequency)
                             #all_series['date'].max())
print 'len(series_range)',len(series_range)


sequential_model = False

#dest_folder = 'csv/' + ('seq/' if sequential_model else 'nonseq/') + \
#        series_type + '/'
dest_folder = 'csv/19-05/'

############################################################
##### FOR NON-SEQUENTIAL MODELS ######
climate_ds = DataSource()
climate_ds.window_size = 9 # 9 months
climate_ds.series_columns = ['T', 'PP']
climate_ds.renamed_series_columns = climate_ds.series_columns

inflation['monthly'] = normalize(inflation['monthly'])
inflation_ds = DataSource()
inflation_ds.window_size = 4
inflation_ds.series_columns = ['monthly']
inflation_ds.renamed_series_columns = ['inflation']
inflation_ds.data = inflation
inflation_ds.jump = 1

price_ds = DataSource()
price_ds.window_size = 10
price_ds.jump = 1 #never change this, change series_frequency instead
price_ds.series_columns = ['price']
price_ds.renamed_series_columns = ['price']

oil['value'] = normalize(oil['value'])
oil_ds = DataSource()
oil_ds.window_size = 9
oil_ds.data = oil
oil_ds.series_columns = ['value']
oil_ds.renamed_series_columns = ['oil']
#oil_ds.window_transformation_procedure = to_percentage_change
############################################################

############################################################
##### FOR SEQUENTIAL MODELS ######
if sequential_model:
    climate_ds.window_size = 1

    inflation_ds.window_size = 1
    inflation_ds.jump = 1

    price_ds.window_size = 2

    oil_ds.window_size = 1
############################################################

print 'computing oil columns...'
oil_columns = expand_data_source(series_range, oil_ds)
print 'computing inflation columns...'
inflation_columns = expand_data_source(series_range, inflation_ds)
