from sklearn.decomposition import PCA
from sklearn_pandas import DataFrameMapper, cross_val_score
import pandas as pd
import numpy as np
import cPickle as pickle
import sys
sys.path.insert(0, '../preproc')
from df_build2 import get_all_dates

pk_in = '../preproc/india_df_full_weekly.pickle'

na_cutoff_rate = 0.3


if __name__ == '__main__':
    with open(pk_in,'rb') as f:
        df = pickle.load(f)
    print 'df loaded in'

    pcabank = dict()
    mapbank = dict()
    all_dates = get_all_dates(df)

    for state, sgroup in df.groupby('state'):
        for product, pgroup in sgroup.groupby('product'):
            cols = []
            for (subproduct, city), group in pgroup.groupby(['subproduct','city']):
                group.set_index('date',inplace=True)
                if group['price'].count() * 1. / len(all_dates) < 1 - na_cutoff_rate:
                    continue
                #group = group.interpolate().bfill()
                cols.append(group['price'])

            mat = pd.concat(cols)
            pca = PCA(1)
            mapper = DataFrameMapper([(list(mat.columns), pca)])
            axis = mapper.fit_transform(mat)
            mat_star = pca.inverse_transform(axis)
            pcabank[(state, city, product, subproduct)] = pca
            mapbank[(state, city, product, subproduct)] = mapper
            break
