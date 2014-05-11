import pandas as pd

retail_daily_fn = '../../data/india/csv_preprocessed/preproc_retail_daily/india_timeseries_retail_daily_interpolated_0.4.csv'

wholesale_daily_fn = '../../data/india/csv_preprocessed/preproc_wholesale_daily/india_timeseries_wholesale_daily_interpolated_0.4.csv'

climate_fn = 'climate.csv'

oilprices_fn = '../../data/oil/international_oilprices.csv'

retail_good_series = [
    ('Andhra Pradesh', 'Rice'),
]

wholesale_good_series = [
]

retail = pd.read_csv(retail_daily_fn, parse_dates=['date'])
wholesale = pd.read_csv(retail_daily_fn, parse_dates=['date'])
climate = pd.read_csv(climate_fn, parse_dates=['date'])
oil = pd.read_csv(oilprices_fn, parse_dates=['date'], index_col=False)

retail_range = pd.date_range(retail['date'].min(),
                             retail['date'].max())
wholesale_range = pd.date_range(wholesale['date'].min(),
                                wholesale['date'].max())

climate_ds = DataSource()
climate_ds.window_size = 9 # 9 months
climate_ds.series_columns = ['TM', 'Tm']
climate_ds.renamed_series_columns = climate_ds.series_columns

price_ds = DataSource()
price_ds.window_size = 2
price_ds.series_columns = ['price']

oil['value'] = normalize(oil['value'])
oil_ds = DataSource()
oil_ds.window_size = 9
oil_ds.data = oil
oil_ds.series_columns = ['value']
oil_ds.renamed_series_columns = ['oil']
#oil_ds.window_transformation_procedure = to_percentage_change

retail_oil_columns = expand_data_source(retail_range, oil_ds)
wholesale_oil_columns = expand_data_source(wholesale_range, oil_ds)
