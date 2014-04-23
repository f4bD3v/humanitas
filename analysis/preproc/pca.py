import numpy as np
import scipy.linalg

def pca(*series):
    d = np.array(np.column_stack(series),dtype='float')
    print 'input data:'
    print d

    # compute the mean by variating the first axis (i.e. across columns)
    mean = np.mean(d, axis=0)


    # make the data 0-mean
    d -= mean
    
    print 'zero-mean input data:'
    print d

    # compute SVD of d
    (U, S, V) = np.linalg.svd(d, full_matrices=False)

    # get principal component
    v1 = V[0,][:,np.newaxis]


    # project each data point onto subspace of v1
    d = d.dot(v1)

    return (mean, v1, d)

def pca_revert(mean, v1, d):
    # expand the components
    d = d.dot(v1.T)

    # add back the mean
    d += mean

    return d

if __name__ == '__main__':
    # 4 time-series observed for 2 time instances
    (mean, v1, d) = pca([2400, 1300], [5500, 4800], [4100, 3900], [14500, 10600])
    print 'means:'
    print mean
    print 'principal component:'
    print v1
    print 'reduced version of data:'
    print d
    print 'guess:'
    print pca_revert(mean, v1, d)
