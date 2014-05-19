import pybrain as pb
from pybrain.structure.connections import FullConnection as C, MotherConnection, \
        SharedFullConnection 
import pandas as pd
from pybrain.datasets import SupervisedDataSet
from pybrain.supervised.trainers import BackpropTrainer
#from mybackprop import BackpropTrainer
from models import *
import os
import cPickle as pickle
import numpy as np
import functools

def printModel(net):
    for mod in net.modules:
        print mod.name
        for conn in net.connections[mod]:
            print '\t%s (to %s) - %d weights' % (conn.name, conn.outmod.name,
                                          len(conn.params))

# region=None -> all regions
def toPybrainData(T, R, P, infile, outfile, small=False,region=None):
    ds = SupervisedDataSet(T * R * P, R * P)
    numDatapoints = 0
    d = pd.read_csv(infile)
    print 'correct R=',len(d.region.unique())
    if region is not None:
        d = d[d['region'] == region]
    for window, rows in d.groupby(['window']):
        rows.sort(['region', 'product'])
        in_ = []
        out_ = []
        for i, row in rows.iterrows():
            in_.append(row['initial'])
            changes = map(float, row['changes'].split('|'))
            in_ += changes[:-1]
            out_.append(changes[-1])
        ds.addSample(in_, out_)
        numDatapoints += 1
        if numDatapoints % 50 == 0:
            print 'loaded',numDatapoints,'datapoints'
        if small == True and numDatapoints > 50:
            break
    print 'saving',numDatapoints,'datapoints'
    ds.saveToFile(outfile)
    return ds


class RetailDailyTrain:
    T = 100
    R = 15
    P = 9
    TEST_PROPORTION = .85
    datapoints_in = 'daily-retail-2.csv'
    datapoints_out = 'daily-retail.pybrain'
    model_file = 'daily-retail'
    models = [None, 
                buildModel1, 
                functools.partial(buildModel2, K0=5, K1=30, K2=10),
                functools.partial(buildModel2, K0=8, K1=30, K2=80),
                functools.partial(buildModel2, K0=8, K1=20, K2=50),
            ]


    def __init__(self, modelNb=1):
        self.data = None
        self.trainData = None
        self.testData = None
        self.model = None
        self.modelNb = modelNb
        self.model_file = '%s.model%d' % (self.model_file, self.modelNb)

    def getData(self):
        if self.data is not None:
            return self.data
        if not os.path.isfile(self.datapoints_out):
            self.data = toPybrainData(self.T, self.R, self.P,
                    self.datapoints_in, self.datapoints_out,
                    small=('small' in self.datapoints_out))
            return self.data
        print 'loading',self.datapoints_out
        self.data = SupervisedDataSet.loadFromFile(self.datapoints_out)
        return self.data
    
    def getTrainData(self):
        if self.trainData is None:
            self.trainData, self.testData = \
                    self.getData().splitWithProportion(self.TEST_PROPORTION)
        return self.trainData

    def getTestData(self):
        if self.testData is None:
            self.getTrainData()
        return self.testData

    def getModel(self):
        if self.model is None:
            self.model = self.models[self.modelNb](T=self.T, R=self.R, P=self.P)
            #self.model = buildEasyModel(T=self.T, R=self.R, P=self.P)
            printModel(self.model)
        return self.model

    def trainModel(self):
        bprop = BackpropTrainer(self.getModel(), self.getTrainData(),
                verbose=True)
        for epoch in xrange(50):
            print 'training epoch',epoch
            #print self.getModel().activate(np.random.normal(size=100*15*9))
            bprop.train()
            self.testModel()
            #print self.getModel().activate(np.random.normal(size=100*15*9))
            #if epoch%4 == 0:
            with open(self.model_file+'.epoch'+str(epoch), 'wb') as f:
                pickle.dump(self.getModel(), f)
        #print 'saving model'
        with open(self.model_file, 'wb') as f:
            pickle.dump(self.getModel(), f)

    def loadModel(self, fn=None):
        if fn is None:
            fn = self.model_file
        print 'loading', fn
        with open(fn, 'rb') as f:
            self.model = pickle.load(f)

    def baselineRegression(self, data):
        ret = np.empty(data['target'].shape)
        for i, x in enumerate(data['input']):
            if np.random.randint(0, 100) <= 90:
                ret[i,] = np.zeros(data['target'].shape[1])
            else:
                ret[i,] = np.random.normal(loc=0., scale=.1, size=
                        data['target'].shape[1])
        return ret


    def testModel(self):
        activations = self.getModel().activateOnDataset(self.getTestData())
        activationsb = self.baselineRegression(self.getTestData())
        actual = self.getTestData()['target']
        errs = (activations - actual)**2
        errsb = (activationsb - actual)**2
        assert errsb.shape == errs.shape
        column_errs = np.sum(errs,axis=0) / errs.shape[0]
        column_errsb = np.sum(errsb,axis=0) / errs.shape[0]
        for i,x in enumerate(column_errs):
            print 'Average error R=%02d P=%02d: %.08f %.08f' % (
                    i//self.P, i%self.P,
                    x, column_errsb[i])
        print 'Total error:', np.sum(errs), np.sum(errsb)

        # count only non-zero rows
        for i in xrange(self.R*self.P):
            nonzero = np.where(actual[:,i] > 1e-8)
            column_errs[i] = sum((activations[nonzero,i].flatten() - \
                actual[nonzero,i].flatten())**2)/len(nonzero)
            column_errsb[i] = sum((activationsb[nonzero,i].flatten() - \
                actual[nonzero,i].flatten())**2)/len(nonzero)
        for i,x in enumerate(column_errs):
            print 'Average nonzero error R=%02d P=%02d: %.08f %.08f' % (
                    i//self.P, i%self.P,
                    x, column_errsb[i])
        print 'total nonzero errors:',sum(column_errs),sum(column_errsb)



def main():
    rdt = RetailDailyTrain(2)
    rdt.trainModel()
    #rdt.loadModel('daily-retail.model2.epoch4')
    rdt.testModel()


if __name__ == '__main__':
    main()
