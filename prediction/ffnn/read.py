import pandas as pd
import time
from itertools import islice

# Taken from
# http://stackoverflow.com/questions/6822725/rolling-or-sliding-window-iterator-in-python
def slidingWindow(seq, n=2):
    "Returns a sliding window (of width n) over data from the iterable"
    "   s -> (s0,s1,...s[n-1]), (s1,s2,...,sn), ...                   "
    it = iter(seq)
    result = tuple(islice(it, n))
    if len(result) == n:
        yield result    
    for elem in it:
        result = result[1:] + (elem,)
        yield result


# input: table (region, product, time, value)
# output: table (window, region, product, initial, changes)
# where changes = a list of T-1 ratios, separated by |
def windowData(data, T):
    ret = []
    print 'iterating through groups'
    for (region, product), rows in data.groupby(['region', 'product']):
        rows.set_index(['time'])
        print (region, product), len(rows)
        for i, window in enumerate(slidingWindow(rows.value[1:], T+1)):
            roll = pd.rolling_apply(pd.Series(window), 2,
                    lambda x:float(x[1])/x[0]-1.)[1:]
            ret.append((i, region, product, window[0], 
                '|'.join(map(str,roll)))
            )
    print 'windowData done'
    return pd.DataFrame(ret, 
            columns=['window', 'region', 'product', 'initial', 'changes'])

def getOrderedRegionsOfDataset(d):
    regions = d.state.unique()
    regions.sort()
    return {r : i for i, r in enumerate(regions)}
    
def getOrderedDatesOfDataset(d):
    dates = d.date.unique()
    dates.sort()
    return {d : i for i, d in enumerate(dates)}


def getDailyRetailData():
    print 'loading file'
    data = pd.read_csv('india_original_retail_daily_interpolated_0.4.csv')
    products = ['Atta (Wheat)', 'Gram Dal', 'Onion', 'Rice', 
        'Salt Pack (Iodised)', 'Sugar', 'Tea Loose', 
        'Tur/Arhar Dal', 'Vanaspati']
    products.sort()
    products = {p : i for i, p in enumerate(products)}
    regions = getOrderedRegionsOfDataset(data)
    dates = getOrderedDatesOfDataset(data)
    print 'iterating through groups'
    ret = []
    for (region, product), rows in data.groupby(['state', 'product']):
        try:
            product = products[product]
        except:
            continue
        print (region, product)
        region = regions[region]
        # skip ignored products
        if product < 0:
            continue
        t = time.time()
        rows.sort('date')
        print 'bf2:', time.time()-t
        t = time.time()
        for i, row in rows.iterrows():
            # flattening time into integers => when using multiple datasets, we
            # have to write a linear relationship between them so that we don't
            # accidentaly use values from the future
            ret.append((region, product, dates[row['date']], row['price']))
        print 'af:', time.time()-t
    print 'getDailyRetailData done'
    return pd.DataFrame(ret, columns=['region', 'product', 'time', 'value'])



def transformDailyRetailData():
    d1 = getDailyRetailData()
    print 'saving daily-retail1-csv'
    d1.to_csv('daily-retail-1.csv')
    d1 = pd.read_csv('daily-retail-1.csv')
    d2 = windowData(d1, 100)
    print 'saving daily-retail2-csv'
    d2.to_csv('daily-retail-2.csv')

def main():
    transformDailyRetailData()

if __name__ == '__main__':
    main()
