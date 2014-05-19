import numpy as np
import pandas as pd
import os
import glob
import sys
import copy
import re
import IPython
from gen_data_config import *

#debug = True
debug = False

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
    # can use to_percentage_change to change [2,4,4,4,6] to [2,1,0,0,.5] or
    # normalization
    window_transformation_procedure = None

    def __init__(self):
        self.data = DataSource.data
        self.date_column = DataSource.date_column

    def get_date(self, rownum):
        return self.data.iloc[rownum][self.date_column]

def to_percentage_change(d):
    #print d
    ret = [d[0]]
    assert abs(d[0]) >= 1e-8 # not zero pls
    for i in xrange(1, len(d)):
        assert abs(d[i]) >= 1e-8
        ret.append( d[i]*1. / d[i-1] - 1.)
    return ret

def normalize(d):
    return (d - d.min()) * 2. / (d.max() - d.min()) - 1.

def dataframes_concat(l):
    # remove None ones
    l = filter(lambda x:x is not None, l)
    # column bind them
    data = np.hstack(map(pd.DataFrame.as_matrix, l))
    # compute column names
    cols = reduce(lambda x,v:x+list(v.columns), l, [])
    return pd.DataFrame(data, columns=cols)

# myself=True means the datasource is the time series itself
def expand_data_source(dates, ds, myself=False, j_hop=1):
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
        if debug and myself:
            print 'at',date
        # slide the window until `date'
        while (not myself and ds.get_date(j) < date) or \
              (myself and j < len(ds.data) and ds.get_date(j) <= date):
            new = ds.data[np.array(cols)].irow(j)[:]
            #print '\t\tadding',ds.get_date(j)#,':',new
            window.append(new)
            if debug and myself:
                print '\tinserting',j,':',new[0],'corresponding to',\
                        ds.get_date(j)
            j += j_hop
        #print '\t\t-'
        # get rid of old stuff
        window = window[-jmp * wnd:]
        if len(window) != jmp * wnd:
            if not myself:
                print 'Warning: not enough data points to align ' \
                    'the data for %s, moving on?' % date
                sys.exit(-1)
            else:
                continue
        if debug and myself:
            print 'adding window:',window
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
    try:
        os.makedirs(dest_folder, exist_ok=True)
    except:
        pass
    # the series will typically be slightly smaller because we've
    # skipped a few datapoints in the beginning to create the window
    offset = price_ds.window_size - 1

    #for s in good_series:
    for sname in all_series.columns:
        if sname[0] != '(':
            continue
        #state = s[0]
        #print '* creating features for',s,'state=',state
        state = re.search(r"\('([^']+)',", sname).group(1)
        print '* creating features for',sname,'state=',state
        climate_ds.data = climate[climate['state'] == state].reset_index()
        # normalize all used climate columns
        if len(climate_ds.data):
            for col in climate_ds.series_columns:
                climate_ds.data[col] = normalize(climate_ds.data[col])
        else:
            print '\twarn: no climate data'

        print '\tcomputing climate columns...'
        climate_columns = expand_data_source(series_range, climate_ds)

        # spikes are followed very poorly without price normalization
        #series = pd.DataFrame(
                #{'date' : pd.Series(series_range),
                 # pandas madness
                 # TODO normalize
                 #'price': 
                 #pd.Series(all_series[sname].as_matrix(),index=all_series['date']).reindex(series_range),
                 #columns=['price']
                 #}
        #)

        # pandas retarded stuff
        series = pd.DataFrame(
                {'date': all_series['date'],
                 'price': normalize(all_series[sname])}
        ).set_index('date').reindex(series_range).reset_index()
        series.columns = ['date', 'price']

        price_ds.data = series
        print '\tcomputing series columns...'
        series = expand_data_source(series_range, price_ds, myself=True)

        print offset, len(series), len(oil_columns), len(inflation_columns)
        print '\tmerging columns...'
        data = dataframes_concat([
            climate_columns[offset:] if climate_columns is not None else None, 
            oil_columns[offset:],
            inflation_columns[offset:],
            series
        ])
        data['date'] = series_range[offset:]
        data = data.set_index('date')
        #to_fn = dest_folder+'/'+series_type+'-'+('-'.join(s))+'.csv' 
        to_fn = dest_folder+'/'+series_type+'-'+sname+'.csv' 
        print '\tdumping to',to_fn
        data.to_csv(to_fn)

if __name__ == '__main__':
    main()
