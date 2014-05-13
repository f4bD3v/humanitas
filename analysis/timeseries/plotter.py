import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import os, sys
sys.path.insert(0, '../preproc')
sys.path.insert(0, '../pca')
from df_build_func import get_all_dates
from na_analysis import na_analysis_by_reg_prod


csv_in_wholesale_daily = os.getcwd()+'/../../data/india/csv_preprocessed/india_original_wholesale_daily_0.4.csv'
csv_in_retail_daily = os.getcwd()+'/../../data/india/csv_preprocessed/india_original_retail_daily_0.4.csv'
csv_in_wholesale_weekly = os.getcwd()+'/india_original_wholesale_weekly_0.6_downsampled.csv'
csv_in_retail_weekly = os.getcwd()+'/india_original_retail_weekly_0.6_downsampled.csv'


retail_product_list = ['Atta (Wheat)', 'Gram Dal', 'Onion', 'Potato', 'Rice', 'Sugar', 'Tea Loose', 'Tur/Arhar Dal', 'Vanaspati']
region_list = []
good_rate = 0.8
good_rate_for_rice_wheat_potato = 0.8
save_fig = True
show_fig = False

run_wholesale_daily = True
run_wholesale_weekly = False
run_retail_daily = False
run_retail_weekly = False




#15 most populated cities
selected_cities = ['Mumbai', 'Delhi', 'Bangalore', 'Hyderabad','Ahmedabad','Chennai','Kolkata',\
                 'Surat','Pune','Jaipur','Lucknow','Kanpur','Nagpur','Indore','Thane']

#states of the 15 most populated cities
# selected_regions = ['Maharashtra','Delhi','Karnataka','Andhra Pradesh','Gujarat', \
#                     'Tamil Nadu','West Bengal','Rajasthan','Uttar Pradesh','Madhya Pradesh',\
#                     'Bihar']
# selected_regions = ['Tamil Nadu','West Bengal','Rajasthan','Uttar Pradesh','Madhya Pradesh']

#most frequently used and has good data in general
selected_products = ['Rice','Wheat','Apple','Potato','Onion']

def subdf(df_ts, q1, q2=None, q3=None):
    cols = list(df_ts.columns)
    ret = []
    for c in cols:
        if (q1 in c) and (q2 == None or q2 in c) and (q3 == None or q3 in c):
            ret.append(c)
    return df_ts[ret]

def eliminate_spikes(ddf, ddf_ret, threshold):

    ddf = ddf[ddf_ret<threshold]
    ddf_ret = ddf_ret[ddf_ret<threshold]
    ddf = ddf[ddf_ret > -threshold]
    ddf_ret = ddf_ret[ddf_ret > -threshold]

    return ddf, ddf_ret

def get_ret(df_ts):
    ret = pd.DataFrame()
    for label in list(df_ts.columns):
        s = df_ts[label]/df_ts[label].shift(1) - 1
        ret[label] = s

    return ret* 100

def plotter(showlegend, path, subdir, df_ts, ret, categories1, categories2=[None]):
    path = path+str(subdir)+'/'
    if not os.path.exists(path):
        os.makedirs(path)

    for c1 in list(categories1):
        for c2 in list(categories2):

            try:
                ddf = subdf(df_ts, c1, c2)
                ddf_ret = subdf(ret, c1, c2)
                label = (c1, c2)

                #eliminate spikes
                # ddf, ddf_ret = eliminate_spikes(ddf, ddf_ret, threshold = 100)

                ybound = 100
                fig, axes = plt.subplots(nrows=2, ncols=1)
                ddf.plot(ax=axes[0], legend=False)
                axes[0].set_title('price of '+str(label), )
                axes[0].set_ylabel('price')
                ddf_ret.plot(ylim=[-ybound,ybound], ax=axes[1], legend=showlegend)
                axes[1].set_title('daily difference of '+str(label))
                axes[1].set_ylabel("daily difference in %")
                if save_fig:
                    print 'saving fig', label
                    # savefigure(label)
                    plt.savefig(path+str(label)+'.png')
                if not show_fig:
                    plt.close()
            except Exception, e:
                print e, 'at', (c1, c2)
                continue


def get_df_ts(df, all_dates):

    df_ts = pd.DataFrame()
    states = set()
    cities = set()

    for (state, city, product, subproduct), group in df.groupby(['state','city','product','subproduct']):
        valid_rate = round(group['price'].count() * 1./len(all_dates), 2)
        involve = False
        if product == 'Rice' or product == 'Wheat' or product == 'Potato':
            if valid_rate >= good_rate_for_rice_wheat_potato:
                involve = True
        elif valid_rate >= good_rate:
            involve = True

        #if state == 'West Bengal':
        if involve:
            df_ts[(state, city, product, subproduct, valid_rate)] = group['price'].copy();
            states.add(state)
            cities.add(city)

    return df_ts, states, cities


def get_df_ts_reg_best(df, all_dates):
    # compute regional best
    df_ts_reg_best = pd.DataFrame()

    for state, state_group in df.groupby('state'):
        for product, product_group in state_group.groupby('product'):
            valid_rates = []
            labels = []
            subdf_ts = pd.DataFrame()
            for (city, subproduct), group in product_group.groupby(['city', 'subproduct']):
                v = round(group['price'].count() * 1./len(all_dates),2)
                valid_rates.append(v)
                labels.append((state, city, product, subproduct, v))
                subdf_ts[(state, city, product, subproduct, v)] = group['price']
            best_idx = valid_rates.index(max(valid_rates))
            if valid_rates[best_idx] >= good_rate:
                df_ts_reg_best[labels[best_idx]] = subdf_ts[labels[best_idx]]

    return df_ts_reg_best



if __name__ == "__main__":

    if run_wholesale_daily:

        print 'Wholesale daily ========================================================================'
        csv_out = 'wholesale_daily_'
        path = os.getcwd()+'/wholesale_daily/'
        if not os.path.exists(path):
            os.makedirs(path)

        df = pd.read_csv(csv_in_wholesale_daily, header=0)
        df['price'] = df['price']/100; #make it price per kg
        df['date'] = pd.to_datetime(df['date'])
        df = df[df['subproduct'] != 'Other']
        df = df[df['product']!='Coriander']
        all_dates = get_all_dates(df, 'D')
        df.set_index('date', inplace = True)

        df_ts, states, cities = get_df_ts(df, all_dates)
        ret = get_ret(df_ts)
        df_ts, ret = eliminate_spikes(df_ts, ret, threshold=100)
        df_ts_reg_best = get_df_ts_reg_best(df, all_dates)
        ret_reg_best = get_ret(df_ts_reg_best)

        plotter(True, path, 'per_region', df_ts, ret, states, selected_products)
        plotter(True, path, 'per_product', df_ts, ret, selected_products)
        plotter(True, path, 'per_product_regional_best', df_ts_reg_best, ret_reg_best, selected_products)

        num_series, best_non_na = na_analysis_by_reg_prod(df, 'D')
        num_series.to_csv(path+'num_series_'+csv_out+str(good_rate)+'.csv')
        best_non_na.to_csv(path+'best_non_na_'+csv_out+str(good_rate)+'.csv')


    if run_wholesale_weekly:

        print 'Wholesale weekly ========================================================================'
        csv_out = 'wholesale_weekly_'
        path = os.getcwd()+'/wholesale_weekly/'
        if not os.path.exists(path):
            os.makedirs(path)

        df = pd.read_csv(csv_in_wholesale_weekly, header=0)
        df['price'] = df['price']/100; #make it price per kg
        df['date'] = pd.to_datetime(df['date'])
        df = df[df['subproduct'] != 'Other']
        df = df[df['product']!='Coriander']
        all_dates = get_all_dates(df, 'W-Fri')
        df.set_index('date', inplace = True)

        df_ts, states, cities = get_df_ts(df, all_dates)
        df_ts_reg_best = get_df_ts_reg_best(df, all_dates)

        plotter(True, path, 'per_region', df_ts, states, selected_products)
        plotter(True, path, 'per_product', df_ts, selected_products)
        plotter(True, path, 'per_product_regional_best', df_ts_reg_best, selected_products)

        num_series, best_non_na = na_analysis_by_reg_prod(df, 'W-Fri')
        num_series.to_csv(path+'num_series_'+csv_out+str(good_rate)+'.csv')
        best_non_na.to_csv(path+'best_non_na_'+csv_out+str(good_rate)+'.csv')

    if run_retail_daily:

        print 'Retail daily ========================================================================'
        csv_out = 'retail_daily_'
        path = os.getcwd()+'/retail_daily/'
        if not os.path.exists(path):
            os.makedirs(path)

        df = pd.read_csv(csv_in_retail_daily, header=0)
        df['date'] = pd.to_datetime(df['date'])
        all_dates = get_all_dates(df, 'D')
        df.set_index('date', inplace = True)

        df_ts, states, cities = get_df_ts(df, all_dates)
        ret = get_ret(df_ts)
        df_ts, ret = eliminate_spikes(df_ts, ret, threshold=100)
        df_ts_reg_best = get_df_ts_reg_best(df, all_dates)
        ret_reg_best = get_ret(df_ts_reg_best)

        plotter(False, path, 'per_region', df_ts, ret, states, selected_products)
        plotter(False, path, 'per_product', df_ts, ret, selected_products)
        plotter(False, path, 'per_product_regional_best', df_ts_reg_best, ret_reg_best, selected_products)

        num_series, best_non_na = na_analysis_by_reg_prod(df, 'D')
        num_series.to_csv(path+'num_series_'+csv_out+str(good_rate)+'.csv')
        best_non_na.to_csv(path+'best_non_na_'+csv_out+str(good_rate)+'.csv')


    if run_retail_weekly:

        print 'Retail weekly ========================================================================'
        csv_out = 'retail_weekly_'
        path = os.getcwd()+'/retail_weekly/'
        if not os.path.exists(path):
            os.makedirs(path)

        df = pd.read_csv(csv_in_retail_weekly, header=0)
        df['date'] = pd.to_datetime(df['date'])
        all_dates = get_all_dates(df, 'W-Fri')
        df.set_index('date', inplace = True)

        df_ts, states, cities = get_df_ts(df, all_dates)
        df_ts_reg_best = get_df_ts_reg_best(df, all_dates)

        plotter(False, path, 'per_region', df_ts, states, selected_products)
        plotter(False, path, 'per_product', df_ts, selected_products)
        plotter(False, path, 'per_product_regional_best', df_ts_reg_best, selected_products)

        num_series, best_non_na = na_analysis_by_reg_prod(df, 'W-Fri')
        num_series.to_csv(path+'num_series_'+csv_out+str(good_rate)+'.csv')
        best_non_na.to_csv(path+'best_non_na_'+csv_out+str(good_rate)+'.csv')

    if show_fig:
        plt.show()
