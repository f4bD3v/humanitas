import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import os

csv_in1 = os.getcwd()+'/../../data/india/csv_preprocessed/preproc_wholesale_daily/india_timeseries_wholesale_daily_interpolated_0.4.csv'
csv_in2 = os.getcwd()+'/../../data/india/csv_preprocessed/preproc_retail_daily/india_timeseries_retail_daily_interpolated_0.4.csv'


if __name__ == "__main__":
    wholesale = pd.read_csv(csv_in1)
    retail = pd.read_csv(csv_in2)
