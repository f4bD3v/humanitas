# -*- coding: utf-8 -*-
"""
A minimalistic ESN demo with Makey-Glass delay 17 data using Oger toolbox
from http://reservoir-computing.org/oger .
by Mantas Lukoševičius 2012
http://minds.jacobs-university.de/mantas
"""
from numpy import *
from matplotlib.pyplot import *
import Oger

# load the data
trainLen = 2000
testLen = 2000

initLen = 100

data = loadtxt('MackeyGlass_t17.txt')

# plot some of it
figure(10).clear()
plot(data[0:1000])

# generate the ESN reservoir
inSize = outSize = 1
resSize = 1000
a = 0.3

random.seed(42)
reservoir = Oger.nodes.LeakyReservoirNode(output_dim=resSize, leak_rate=a, \
    input_scaling=0.5, bias_scaling=0.5, spectral_radius=1.25, reset_states=False) 

# Tell the reservoir to save its states for later plotting 
Oger.utils.make_inspectable(Oger.nodes.LeakyReservoirNode)
 
# create the output   
reg = 1e-8   
readout = Oger.nodes.RidgeRegressionNode( reg )

# connect them into ESN
flow = Oger.nodes.FreerunFlow([reservoir, readout], freerun_steps=testLen)

# train
flow.train([[], [[data[0:trainLen+1,None]]]])

# save states for plotting
X = reservoir.inspect()[0]

# run in a generative mode
Y = flow.execute(array(data[trainLen-initLen:trainLen+testLen+1,None]))
# discard the first elements (just a numbering convention)
Y = Y[initLen+1:] 

# compute MSE for the first errorLen time steps
errorLen = 500
mse = sum( square( data[trainLen+1:trainLen+errorLen+1] - Y[0:errorLen,0] ) ) / errorLen
print 'MSE = ' + str( mse )

# plot some signals
figure(1).clear()
plot( data[trainLen+1:trainLen+testLen+1], 'g' )
plot( Y )
title('Target and generated signals $y(n)$')

figure(2).clear()
plot( X[initLen:initLen+200,0:20] )
title('Some reservoir activations $\mathbf{x}(n)$')

figure(3).clear()
bar( range(1+resSize), readout.beta[:,0] )
title('Output weights $\mathbf{W}^{out}$')

show()