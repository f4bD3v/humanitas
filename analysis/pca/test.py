from sklearn_pandas import DataFrameMapper, cross_val_score
import numpy as np
import pandas as pd
from sklearn.decomposition import PCA

d = pd.DataFrame({'pet':      ['cat', 'dog', 'dog', 'fish', 'cat', 'dog', 'cat', 'fish'],\
                      'children': [4., 6, 3, 3, 2, 3, 5, 4],\
                      'salary':   [90, 24, 44, 27, 32, 59, 36, 27]})

p = PCA(1)
mapper = DataFrameMapper([(['children', 'salary'], p)])
vec = mapper.fit_transform(d)
dd = p.inverse_transform(vec)

print d
print p
print mapper
print vec
print dd
