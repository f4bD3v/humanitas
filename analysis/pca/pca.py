from sklearn.decomposition import PCA
from sklearn_pandas import DataFrameMapper, cross_val_score
import pandas as pd
import numpy as np
import cPickle as pickle

pk_in = 'india_week_df_full.pickle'

if __name__ == '__main__':
    with open('pk_in','rb') as f:
        df = pickle.load(f)
    print 'df loaded in'

    pbank = dict()
    mbank = dict()

    #TODO
    #untested!!!
    for state, sgroup in df.groupby('state'):
        for product, pgroup in sgroup.groupby('product'):
            columns = []
            for (subproduct, city), group in pgroup.groupby('subproduct','city'):
                columns.append(group)
                
            mat = pd.concat(columns)
            pca = PCA(1)
            mapper = DataFrameMapper([(list(M.columns), pca)])
            axis = mapper.fit_transform(mat)
            pbank[(state, city, p2roduct, subproduct)] = pca
            mbank[(state, city, product, subproduct)] = mapper
            #mat_star = pca.inverse_transform(axis)
