from sklearn.decomposition import PCA
from sklearn_pandas import DataFrameMapper, cross_val_score
import pandas as pd
import numpy as np
import cPickle as pickle
import sys
import os
sys.path.insert(0, '../preproc')
from df_build_func import get_all_dates

#csv_df_full = os.getcwd()+'/../../data/india/csv_preprocessed/wholesale_daily/india_original_wholesale_daily.csv'
csv_df_full = os.getcwd() + '/../preproc/india_original_wholesale_daily_0.4.csv'


if __name__ == '__main__':

    df = pd.read_csv(csv_df_full)
    pcabank = dict()
    mapbank = dict()





    # for state, sgroup in df.groupby('state'):
    #     for product, pgroup in sgroup.groupby('product'):
    #         cols = []
    #         for (subproduct, city), group in pgroup.groupby(['subproduct','city']):
    #             group.set_index('date',inplace=True)
    #             if group['price'].count() * 1. / len(all_dates) < 1 - na_cutoff_rate:
    #                 continue
    #             #group = group.interpolate().bfill()
    #             cols.append(group['price'])
    #
    #         mat = pd.concat(cols)
    #         pca = PCA(1)
    #         mapper = DataFrameMapper([(list(mat.columns), pca)])
    #         axis = mapper.fit_transform(mat)
    #         mat_star = pca.inverse_transform(axis)
    #         pcabank[(state, city, product, subproduct)] = pca
    #         mapbank[(state, city, product, subproduct)] = mapper
    #         break
