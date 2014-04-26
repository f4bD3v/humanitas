from sklearn.decomposition import PCA
from sklearn_pandas import DataFrameMapper, cross_val_score
import pandas as pd
import numpy as np
import cPickle as pickle


if __name__ == '__main__':
    with open('pk_in','rb') as f:
        df = pickle.load(f)
    print 'df loaded in'

    treasure = dict()


    #TODO
    #untested!!!
    for state, sgroup in df.groupby('state'):
        for product, pgroup in sgroup.groupby('product'):
            cols = []
            for (subproduct, city), group in pgroup.groupby('subproduct','city'):
                cols.append(group)
            mat = pd.concat(cols)
            pca = PCA(1)
            mapper = DataFrameMapper([(list(M.columns), pca)])
            axis = mapper.fit_transform(mat)
            treasure[(state, city, product, subproduct)] = pca
            #mat_star = pca.inverse_transform(axis)
