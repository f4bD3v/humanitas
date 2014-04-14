from time import time
import matplotlib.pyplot as plt
import pickle

pk_all = 'all_india_weekly.pickle'
pk_rice = 'rice_india_weekly.pickle'

def get_metadata(df, title = '', verbose = True):
    index = df.index.values
    c,p,s = [],[],[]
    for i in range(0, len(index)):
        tp = index[i]
        c.append(tp[3])
        p.append(tp[0])
        s.append((tp[0],tp[1]))
    d = df['date'].reset_index(drop=True).drop_duplicates().tolist()
    c = list(set(c))
    p = list(set(p))
    s = list(set(s))
    if verbose:
        print title
        print "number of dates    = %3i, from %s to %s" %(len(d),str(d[0].date()),str(d[-1].date()) )
        print "number of cities   = %3i, from %s to %s" %(len(c), c[0], c[-1])
        print "number of products = %3i, from %s to %s" %(len(p), p[0], p[-1])
        print "number of subs     = %3i, from %s to %s" %(len(s), s[0], s[-1])
    return d,c,p,s

def get_subs_of(all_subs, product):
    sub_lst = []
    for sub in all_subs:
        if sub[0] == product:
            sub_lst.append(sub[1])
    return sub_lst

if __name__ == "__main__":

    with open(pk_all) as f:
        [df] = pickle.load(f)
    print pk_all+" is loaded into df"
    # sample query: find fine rice price at city Mumbai for the whole period (2005-2014)
    #q = df.query('product=="Rice" & sub=="Fine" & city=="Mumbai"')
    #plt.figure()
    #q.plot()
    #plt.show()

    #create metadata lists
    all_dates,all_cities,all_products,all_subs = get_metadata(df, 'dataframe of all data')

    #loop all combinations of Rice
    start_time = time()
    product = 'Rice'
    subs = get_subs_of(all_subs, product)
    subdf_rice_lst = []
    count = 0
    df_rice = df.query('product=="%s"' %(product))
    for city in all_cities:
        for sub in subs:
            predicate = 'product=="%s" & sub=="%s" & city=="%s"' %(product,sub,city)
            subdf_rice_lst.append(df_rice.query(predicate))
            count = count + 1
    print "All sub-df of "+product+" extracted."
    print "Number of loops: "+str(count)+", Elapsed time: "+str(time()-start_time)+" secs"

    with open(pk_rice, 'w') as f:
        pickle.dump([df_rice, subdf_rice_lst, all_dates, all_cities, all_products, all_subs], f)
    print 'df_rice, subdf_rice_lst, all_dates... dumped to '+pk_rice

    
    #for subdf_rice in subdf_rice_lst:
    #    a,b,c,d = get_metadata(subdf_rice, '')
