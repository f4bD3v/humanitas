import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import os

wholesale_daily = True
retail_daily = False
retail_weekly = False

output_by_city = False
merge_by_prod_reg = True
plot_all = True

if wholesale_daily+retail_daily+retail_weekly != 1:
    raise Exception('exactly one option being True required!')
elif wholesale_daily:
    csv_in = os.getcwd()+'/wholesale_daily/csv_all/india_timeseries_wholesale_daily_interpolated_0.6.csv' #linear interpolated
    # csv_in = os.getcwd()+'/wholesale_daily/csv_all/india_timeseries_wholesale_daily_0.59.csv'  #not interpolated
    # csv_in = os.getcwd()+'/wholesale_daily/csv_all/india_timeseries_wholesale_daily_interpolated_0.599.csv' #spline interpolated
    # csv_in = os.getcwd()+'/wholesale_daily/csv_all/india_timeseries_wholesale_daily_interpolated_0.5999.csv' #polynomial interpolated
    out_folder = os.getcwd()+'/wholesale_daily/'
elif retail_daily:
    csv_in = os.getcwd()+'/retail_daily/csv_all/india_timeseries_retail_daily_interpolated_0.6.csv'
    out_folder = os.getcwd()+'/retail_daily/'
elif retail_weekly:
    csv_in = os.getcwd()+'/retail_weekly/csv_all/india_timeseries_retail_weekly_interpolated_0.6.csv'
    out_folder = os.getcwd()+'/retail_weekly/'


if not os.path.exists(out_folder):
    os.makedirs(out_folder)


# csv_out_wholesale_daily = 'wholesale_daily'

def subcolnames(df_ts, q1, q2):
    cnames = []
    for str_label in list(df_ts.columns):
        if (q1 in str_label) and (q2 == None or q2 in str_label):
            cnames.append(str_label)
    return cnames

def subdf(df_ts, q1, q2 = None):
    cnames = subcolnames(df_ts, q1, q2)
    return df_ts[cnames]

def clear_symbols(string_lst):
    symbols = ['(',')',',','\'']
    ret = []
    for string in string_lst:
        for s in symbols:
            string = string.replace(s, '')
        ret.append(string)
    if len(ret) != 4:
        raise Exception('incorrect label parsing: '+str(string_lst))
    return ret

def parse_strlabel_to_tuple(strlabel):
    label = clear_symbols(strlabel.split(', '))
    return label[0], label[1], label[2], label[3]

def parse_colnames_to_tuples(df_ts):
    cc = []
    for strlabel in list(df_ts.columns):
        cc.append(parse_strlabel_to_tuple(strlabel))
    return cc


def all_state_city_prod_subprod(df_ts):
    all_states = set()
    all_cities = set()
    all_products = set()
    all_subproducts = set()

    for (state, city, product, subproduct) in list(df_ts.columns):
        #  = parse_strlabel_to_tuple(strlabel)
        all_states.add(state)
        all_cities.add(city)
        all_products.add(product)
        all_subproducts.add(subproduct)

    return sorted(list(all_states)), sorted(list(all_cities)), sorted(list(all_products)), sorted(list(all_subproducts))

def run_output_by_city(df_ts, all_cities):
    df_duy = pd.DataFrame()
    for city in all_cities:
        df_city = subdf(df_ts, city)
        for (state, city, product, subproduct) in list(df_city.columns):
            df_duy[product+'_'+subproduct] = df_city[(state, city, product, subproduct)]
        fp = out_folder+'csv_by_city/'
        if not os.path.exists(fp):
            os.makedirs(fp)
        fp = fp+city+'.csv'
        df_duy.to_csv(fp, index_label='date')

def run_merge_by_prod_reg(df_ts, all_states, all_products):
    df_merge = pd.DataFrame()

    for state in all_states:
        for product in all_products:
            df_this = subdf(df_ts, state, product)

            if df_this.shape[1] == 0:
                continue

            avg_series = df_this.mean(axis=1)
            df_merge[(state, product)] = avg_series

    return df_merge


def plotter(df, fpath, fname, save=False, close=True, legend=True):
    if not os.path.exists(fpath):
        os.makedirs(fpath)
    fp = fpath+fname

    ax = df.plot(legend=legend, title='Wholesale Daily Prices of Products in '+fname[:-4])
    ax.set_ylabel('Price (Rupee) / KG')
    ax.set_xlabel('Date')

    if save:
        plt.savefig(fp)
    if close:
        plt.close()
    return True

def read_df_ts(csv_in):
    df_ts = pd.read_csv(csv_in)
    df_ts.set_index('date', inplace=True)
    df_ts.columns = parse_colnames_to_tuples(df_ts)
    return df_ts

def clear_slash(string):
    return string.replace('/', '')

if __name__ == '__main__':
    df_ts = read_df_ts(csv_in)
    all_states, all_cities, all_products, all_subproducts = all_state_city_prod_subprod(df_ts)

    if output_by_city:
        run_output_by_city(df_ts, all_cities)

    if merge_by_prod_reg:
        df_merge = run_merge_by_prod_reg(df_ts, all_states, all_products)

        for state in all_states:
            df_state = subdf(df_merge, state)
            # df_state.plot()
            plotter(df_state, fpath = out_folder+'plot_merged/', fname=state+'.png', save=True)


        #save to csv by region
        for state in all_states:
            df_reg = pd.DataFrame()
            for product in all_products:
                series = subdf(df_merge, state, product)
                if series.shape[1] != 0:
                    df_reg[product] = series.iloc[:,0]

            fp = out_folder+'csv_merged/'
            if not os.path.exists(fp):
                os.makedirs(fp)

            fp = fp+state+'.csv'
            df_reg.to_csv(fp, index_label='date')

    if plot_all:
        for label in list(df_ts.columns):
            plotter(df_ts[label], fpath = out_folder+'plot_all/', fname=str(label).replace('/','-')+'.png', save=True)
