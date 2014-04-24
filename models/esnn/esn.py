


"""
	definitions:
	T - number of points in training set
	Nx - size of the reservoir
	Nu - size of the input signal


	training tips:
	- keep reservoir size small for selection of hyperparams
"""	

"""
	random generation
"""

# "the bigger the size of the space of reservoir signals x(n), the easier it is to find a linear combination of the signals to approximate y_target(n)"
# T > 1+Nu+Nx should hold true
Nx = 0

#input weights matrix 
Win =  0

# recurrent connection matrix
# speedup computation by making the reservoir matrix sparse - few connections between neurons in reservoir
# "fixed fanout number regardless of network size"
# uniform distribution of non-zero elements
W =



# leaking rate - selected as free parameter
alpha =
