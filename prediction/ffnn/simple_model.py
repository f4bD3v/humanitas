import pybrain as pb
import sys
import re
import pandas as pd
from pybrain.tools.shortcuts import buildNetwork
from pybrain.datasets import SupervisedDataSet
from pybrain.supervised.trainers import BackpropTrainer
import numpy as np
import os
import glob
import datetime

import matplotlib as mpl
mpl.use('Agg')
import matplotlib.pyplot as plt

def denormalize(d, min, max):
    '''map [-1,1] to [min,max]'''
    return (d+1.)/2. * (max - min) + min

#features_fn = '../data/csv/wholesale-daily-NCT of Delhi-Najafgarh-Wheat-Dara.csv'

hare_freq = '1D'
#tortoise_freq = '4D'
date_start = datetime.datetime(2005, 1, 1)
date_end = datetime.datetime(2014, 1, 30)
skip_first = 4*9

offerConstantFeedback = True
feedbackPeriod = 2
interpolated = True

series_orig_data = pd.read_csv('../esn/good_series_wholesale_daily.csv')


def train(fn, model):
    series_name = re.search(r'(\(.+\))', fn).group(1)
    pdata = pd.read_csv(fn, parse_dates=['date'])
    series_orig = series_orig_data[series_name]
    series_min = series_orig.min()
    series_max = series_orig.max()


    #print 'Features:'
    #print pdata.columns

    data = pdata.as_matrix()
    

    inputSize = data.shape[1]-2 # minus output and index
    outputSize = 1
    
    print 'fn:',fn
    print 'model:',model
    print 'inputSize:', inputSize

    if len(model) == 1:
        net = buildNetwork(inputSize, model[0], 3, 1)
    elif len(model) == 2:
        net = buildNetwork(inputSize, model[0], model[1], 1)
    else:
        assert len(model) == 3
        net = buildNetwork(inputSize, model[0], model[1], model[2], 1)

    ds = SupervisedDataSet(inputSize, outputSize)
    train_ds = SupervisedDataSet(inputSize, outputSize)
    test_ds = SupervisedDataSet(inputSize, outputSize)
    for i, (input, target) in enumerate(zip(data[:,1:-1], data[:,-1])):
        ds.addSample(input, target)
        if i < .85 * len(data):
            train_ds.addSample(input, target)
        else:
            test_ds.addSample(input, target)
    
    print 'variance of the test data:', np.var(test_ds['target'][:,0])

    print 'starting'

    full_date_range = pd.date_range(date_start, date_end, freq=hare_freq)
    #predicted_date_range = pd.date_range(date_start, date_end, freq=tortoise_freq)
    
    # XXX hardcoded
    #predicted_date_range = predicted_date_range[9:]
    predicted_date_range = pdata['date']

    full_date_range = full_date_range[skip_first:]

    #test = pd.DataFrame([predicted_date_range, series_orig_data['date']],
    #        columns=['mine', 'file'])
    #print test
    print 'predicted_date_range:',predicted_date_range[0], \
        predicted_date_range[len(predicted_date_range)-1], \
        len(predicted_date_range)
    print 'full_date_range:',full_date_range[0], \
        full_date_range[len(full_date_range)-1], \
        len(full_date_range)

    if interpolated:
        test_offset = 4*len(train_ds)
    else:
        test_offset = len(train_ds)


    bprop = BackpropTrainer(net, train_ds, verbose=True)
    for i in xrange(300):
        print 'At epoch',i
        bprop.train()
        if (i+1)%10 == 1:
            actual = ds['target'][:,0]
            activations_test = net.activateOnDataset(test_ds)
            actual_test = test_ds['target']
            errs = 1./len(test_ds) * (activations_test - actual_test)**2
            err = np.sum(errs)
            print 'Average test error:', err
            
            if offerConstantFeedback:
                series = net.activateOnDataset(ds)[:,0]
                series = pd.Series(series, index=predicted_date_range,
                        dtype=np.float64)
            else:
                guesses = []
                for input, target in ds:
                    if len(guesses) >= feedbackPeriod:
                        input[-feedbackPeriod-1:-1] = guesses[-feedbackPeriod:]
                    guess = net.activate(input)
                    guesses.append(guess)
                series = pd.Series(guesses, index=predicted_date_range,
                        dtype=np.float64)


            if interpolated:
                series = series.reindex(full_date_range)
                series = series.interpolate('linear')

            actual = denormalize(actual, series_min, series_max)
            series = denormalize(series, series_min, series_max)

            #series = series[len(predicted_date_range) - len(series):]
            #predicted = pd.DataFrame({'date': predicted_date_range, 
            #'pred': series,
            #'actual': ds['target'][:,0]},
            #columns=['date', 'actual', 'pred'])

            #print np.hstack( (series_orig[4*9:100:4][:,np.newaxis], 
            #                  actual[:25-9][:,np.newaxis]) )
            #sys.exit(-1)

            if interpolated:
                plt.plot(full_date_range, series, 'g-', label='pred')
                #plt.plot(full_date_range, ds['target'][:,0], label='actual')
                plt.plot(full_date_range, 
                        series_orig_data[series_name][skip_first:skip_first +
                            len(full_date_range)],
                        'b-', label='train')
                plt.plot(full_date_range[test_offset:], 
                        series[test_offset:], 'r-', label='test')
            else:
                plt.plot(predicted_date_range, series, 'g-', label='pred')
                #plt.plot(predicted_date_range, actual, label='train')
                plt.plot(predicted_date_range[test_offset:],
                        series[test_offset:], 'r-', label='test')

            #plt.plot(full_date_range, 
            #        series_orig_data[series_name][4*9:4*9 +
            #            len(full_date_range)],
            #        'b-', label='train')
            plt.title('\nmodel: %s - %s, \nepoch: %d\ntest err: %.4f' % 
                    (model, fn, i+1, err))
            plt.legend(loc=2)
            plt.grid()
            plt.savefig('svg/pred___%s___%s___epoch%d.svg' % (
                os.path.splitext(os.path.basename(fn))[0], model, i+1))
            plt.close()


for fn in glob.glob('../data/csv/19-05/wholesale-daily-*.csv'):
#for fn in glob.glob('../data/csv/wholesale-daily-*West*.csv'):
    for model in ( (15, 15), (10, 10), (15, 20), (20, 20), (10,10,5) ):
    #for model in ( (15, 15), (10, 10) ):
    #for model in ( (10,10), ):
        train(fn, model)

