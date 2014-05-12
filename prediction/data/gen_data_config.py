import pandas as pd
from gen_data import *


retail_daily_fn = '../../data/india/csv_preprocessed/preproc_retail_daily/india_timeseries_retail_daily_interpolated_0.4.csv'

wholesale_daily_fn = '../../data/india/csv_preprocessed/preproc_wholesale_daily/india_timeseries_wholesale_daily_interpolated_0.4.csv'

inflation_fn = '../../data/india/inflation/inflation_data_processed.csv'

climate_fn = '../../data/india/climate/climate_processed.csv'

oilprices_fn = '../../data/oil/international_oilprices.csv'

retail_good_series = [
    ('Andhra Pradesh', 'Rice'),
]

wholesale_good_series = [
]


retail = pd.read_csv(retail_daily_fn, parse_dates=['date'])
wholesale = pd.read_csv(retail_daily_fn, parse_dates=['date'])
climate = pd.read_csv(climate_fn, parse_dates=['date'])
inflation = pd.read_csv(inflation_fn, parse_dates=['date'])
oil = pd.read_csv(oilprices_fn, parse_dates=['date'], index_col=False)

retail_range = pd.date_range(retail['date'].min(),
                             retail['date'].max())
wholesale_range = pd.date_range(wholesale['date'].min(),
                                wholesale['date'].max())

dest_folder = 'csv/svr/'

############################################################
##### FOR NON-SEQUENTIAL MODELS ######
climate_ds = DataSource()
climate_ds.window_size = 9 # 9 months
climate_ds.series_columns = ['TM', 'Tm']
climate_ds.renamed_series_columns = climate_ds.series_columns

inflation_ds = DataSource()
inflation_ds.window_size = 4
inflation_ds.series_columns = ['monthly']
inflation_ds.renamed_series_columns = ['inflation']
inflation_ds.data = inflation
inflation_ds.jump = 3

price_ds = DataSource()
price_ds.window_size = 2
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
climate_ds.window_size = 1

inflation_ds.window_size = 1
inflation_ds.jump = 1

price_ds.window_size = 1

oil_ds.window_size = 1
############################################################

retail_oil_columns = expand_data_source(retail_range, oil_ds)
wholesale_oil_columns = expand_data_source(wholesale_range, oil_ds)

retail_inflation_columns = expand_data_source(retail_range, inflation_ds)
wholesale_inflation_columns = expand_data_source(wholesale_range, inflation_ds)
