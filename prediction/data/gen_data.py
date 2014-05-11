import numpy as np
import pandas as pd
import os
import glob
import sys
import copy
from gen_data_config import *

class DataSource(object):
    data = None
    # the column in `data' which represents the date (must be of datetime type)
    date_column = 'date'
    # the columns interesting for learning
    series_columns = ['']
    # can be equal to series_columns unless you want to make things look nicer
    renamed_series_columns = ['']
    # how many instances from the past are we interested in
    window_size = 20
    # every how many instances are we interested in?
    jump = 1
    # can use to_percentage_change to change [2,4,4,4,6] to [2,1,0,0,.5]
    window_transformation_procedure = None

    def __init__(self):
        self.data = DataSource.data
        self.date_column = DataSource.date_column

    def get_date(self, rownum):
        return self.data.loc[rownum][self.date_column]

def to_percentage_change(d):
    #print d
    ret = [d[0]]
    assert abs(d[0]) >= 1e-8 # not zero pls
    for i in xrange(1, len(d)):
        assert abs(d[i]) >= 1e-8
        ret.append( d[i]*1. / d[i-1] - 1.)
    return ret

def normalize(d):
    return (d - d.min()) * 1. / (d.max() - d.min())

def dataframes_concat(l):
    # remove None ones
    l = filter(lambda x:x is not None, l)
    # column bind them
    data = np.hstack(map(pd.DataFrame.as_matrix, l))
    # compute column names
    cols = reduce(lambda x,v:x+list(v.columns), l, [])
    return pd.DataFrame(data, columns=cols)

def expand_data_source(dates, ds):
    if not len(ds.data):
        #raise Exception('no data in the source')
        return None
    # current index in the ds
    j = 0
    # current sliding window
    window = []
    # data to return
    ret = None
    jmp = ds.jump
    wnd = ds.window_size
    cols = ds.series_columns
    for date in dates:
        # slide the window until `date'
        while ds.get_date(j) < date:
            new = ds.data[np.array(cols)].irow(j)[:]
            window.append(new)
            j += 1
        # get rid of old stuff
        window = window[-jmp * wnd:]
        if len(window) != jmp * wnd:
            print 'Warning: not enough data points to align ' \
                'the data for %s, moving on?' % date
            sys.exit(-1)
            continue
        if ds.window_transformation_procedure is not None:
            wwindow = copy.deepcopy(window)
            # apply the window_transformation_procedure on each column
            for k in xrange(len(cols)):
                transf = to_percentage_change(
                        [window[jmp*v][k] for v in xrange(0, wnd)])
                for v in xrange(0, wnd):
                    wwindow[jmp*v][k] = transf[v]
        else:
            wwindow = window
        

        # merge the columns from each time window
        crt = np.array(pd.concat(wwindow[::jmp]))
        # create the dataframe with the needed columns
        if ret is None:
            if not ds.renamed_series_columns:
                ds.renamed_series_columns = cols
            ret = pd.DataFrame(columns=
                sum((map(lambda x:'%s_%d'%(x,i), ds.renamed_series_columns)
                for i in xrange(wnd)), []))
        # append the row
        ret.loc[len(ret)] = crt
    return ret

def get_series(d, *params):
    ret = None
    for c in d.columns:
        if all(("'%s'" % p in c) for p in params):
            if ret is not None:
                print 'error: multiple columns match'
                sys.exit(-1)
            ret = d[c]
    return ret


def main():
    for series_type, good_series_names, series_range, series_data in \
            (('retail', retail_good_series, retail_range, retail), 
             ('wholesale', wholesale_good_series, wholesale_range, wholesale)):
        for s in good_series_names:
            climate_ds.data = climate[climate['state'] == s[0]].reset_index()
            climate_columns = expand_data_source(series_range, climate_ds)

            series = pd.DataFrame(get_series(retail, *s), columns=['price'])
            price_ds.data = series
            series = expand_data_source(series_range, price_ds)

            data = dataframes_concat([series, climate_columns, 
                retail_oil_columns])
            data.to_csv( 'csv/'+series_type+'-'+('-'.join(s))+'.csv' )

if __name__ == '__main__':
    main()
