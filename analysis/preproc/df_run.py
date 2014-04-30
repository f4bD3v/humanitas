from df_build_func import *



usage = '''
    This script read India daily and/or weekly csv files into Pandas dataframes, df_full and/or df_ts

    output:
        india_df_full_weekly.pickle    india_df_full_daily.pickle
        india_df_ts_weekly.pickle      india_df_ts_daily.pickle
        india_full_weekly.csv          india_full_daily.csv
        india_timeseries_weekly.csv    india_timeseries_daily.csv

    description:
        df      : an aggregate dataframe containing all csv data
        df_full : a patched version of df with all missing dates filled with NaN price
        df_ts   : a flattened version of df_full. Each column is a time series of
                  prices of tuple (state, city, product, subproduct)

    general options:
        run_retail_weekly         : True then convert india weekly into df_full and/or df_ts
        run_wholesale_daily          : True then convert india daily into df_full and/or df_ts
        run_saving         : True then output all df_full and df_ts to pickles and csv's
        using_df_full      : True then compute df_full
        using_df_ts        : True then compute df_ts
        daily_product_lst  : A list of products for importing daily dataset
        filter_lst         : A list of products for pre-filtering on dataframes.
                             Empty list means no pre-filtering. Once we decide
                             which products to use, we set filter_lst = daily_product_lst,
                             to avoid creating very large df_full and df_ts
        with_interpolation : True then do linear interpolation on processed series
        na_cutoff_rate     : filter out those series with more NaN than this rate

'''

##============options================

run_retail_weekly = False
run_wholesale_daily = False
run_retail_daily = True
saving_csv = True
saving_pickle = False

using_df_full = True
using_df_ts = True

daily_product_lst = ['Rice','Wheat','Banana', 'Apple','Coriander','Potato', 'Onion']#['Rice','Banana','Wheat', 'Apple','Coriander','Potato']
filter_lst = []

with_interpolation = False

na_cutoff_rate = 0.4

##====================================

fp_csv_weekly = os.getcwd()+'/../../data/india/csv_weekly/rpms.dacnet.nic.in/all_commodities_weekly_india_'
fp_csv_daily = os.getcwd()+'/../../data/india/csv_daily/agmarknet.nic.in/daily/india_daily_'
fp_csv_daily_retail = os.getcwd()+'/../../data/india/csv_daily/fcainfoweb.nic.in/india_daily_fcainfo_retail_2009-2014.csv'
fp_state = os.getcwd()+'/../../data/india/csv_daily/agmarknet.nic.in/regions.csv'

pk_out1_template = 'india_df_full.pickle'   ## => "india_df_full_daily.pickle"
pk_out2_template = 'india_df_ts.pickle'     ## => "india_df_ts_daily.pickle"

csv_out1_template = 'india_original.csv'        ## => "india_full_daily.csv"
csv_out2_template = 'india_timeseries.csv'  ## => "india_timeseries_daily.csv"

date_freq_weekly = 'W-FRI'
date_freq_daily = 'D'



if __name__ == '__main__':
#def main():
    global run_retail_weekly, run_wholesale_daily

    for i in range(0,run_retail_weekly+run_wholesale_daily+run_retail_daily):

        if run_retail_weekly:
            print '\n\nRunning weekly ===============================\n\n'
            mid = '_retail_weekly'
            if with_interpolation:
                mid = mid + '_interpolated'
            csv_out1_weekly = csv_out1_template.split('.')[0] + mid + '.' + csv_out1_template.split('.')[1]
            csv_out2_weekly = csv_out2_template.split('.')[0] + mid + '.' + csv_out2_template.split('.')[1]
            pk_out1_weekly = pk_out1_template.split('.')[0] + mid + '.' + pk_out1_template.split('.')[1]
            pk_out2_weekly = pk_out2_template.split('.')[0] + mid + '.' + pk_out2_template.split('.')[1]

            [fp_csv, date_freq, csv_out1, csv_out2, pk_out1, pk_out2] = \
            [fp_csv_weekly, date_freq_weekly, csv_out1_weekly, csv_out2_weekly, pk_out1_weekly, pk_out2_weekly]

            run_retail_weekly = False

        elif run_wholesale_daily:
            print '\n\nRunning wholesale daily ===============================\n\n'
            mid = '_wholesale_daily'
            if with_interpolation:
                mid = mid + '_interpolated'
            csv_out1_daily = csv_out1_template.split('.')[0] + mid + '.' + csv_out1_template.split('.')[1]
            csv_out2_daily = csv_out2_template.split('.')[0] + mid + '.' + csv_out2_template.split('.')[1]
            pk_out1_daily = pk_out1_template.split('.')[0] + mid + '.' + pk_out1_template.split('.')[1]
            pk_out2_daily = pk_out2_template.split('.')[0] + mid + '.' + pk_out2_template.split('.')[1]

            [fp_csv, date_freq, csv_out1, csv_out2, pk_out1, pk_out2] = \
            [fp_csv_daily, date_freq_daily, csv_out1_daily, csv_out2_daily, pk_out1_daily, pk_out2_daily]
            run_wholesale_daily = False

        elif run_retail_daily:
            print '\n\nRunning retail daily ===============================\n\n'
            mid = '_retail_daily'
            if with_interpolation:
                mid = mid + '_interpolated'
            csv_out1_daily = csv_out1_template.split('.')[0] + mid + '.' + csv_out1_template.split('.')[1]
            csv_out2_daily = csv_out2_template.split('.')[0] + mid + '.' + csv_out2_template.split('.')[1]
            pk_out1_daily = pk_out1_template.split('.')[0] + mid + '.' + pk_out1_template.split('.')[1]
            pk_out2_daily = pk_out2_template.split('.')[0] + mid + '.' + pk_out2_template.split('.')[1]

            [fp_csv, date_freq, csv_out1, csv_out2, pk_out1, pk_out2] = \
            [fp_csv_daily_retail, date_freq_daily, csv_out1_daily, csv_out2_daily, pk_out1_daily, pk_out2_daily]


        df = get_data(fp_csv, fp_state, daily_product_lst)

        all_dates = get_all_dates(df, date_freq)

        df_full, df_ts, dup_records = get_full_data(df, all_dates, \
                using_df_full, using_df_ts, na_cutoff_rate, with_interpolation,\
                filter_lst)

        #print dup_records
        examine_fullness(df_full, len(all_dates), with_interpolation)
        examine_df_ts_fullness(df_ts, len(all_dates), with_interpolation)

        if saving_pickle:

            if using_df_full:

                print 'saving df_full to pickle'
                with open(pk_out1, 'wb') as f:
                    pickle.dump(df_full, f)


            if using_df_ts:

                print 'saving df_ts to pickle'
                with open(pk_out2, 'wb') as f:
                    pickle.dump(df_ts, f)

        if saving_csv:

            if using_df_full:
                print 'saving df_full to csv'
                df_full.to_csv(csv_out1, index=False)

            if using_df_ts:
                print 'saving df_ts to csv'
                df_ts.to_csv(csv_out2, index_label='date')

#if __name__ == '__main__':
    #main()
