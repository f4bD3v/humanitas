from pybrain.structure import FeedForwardNetwork, LinearLayer, TanhLayer 
from pybrain.structure.connections import FullConnection, IdentityConnection, MotherConnection, SharedFullConnection
from pybrain.structure.connections.connection import Connection
from pybrain.structure.moduleslice import ModuleSlice

class FFN:

	def __init__(self, R, P, T):

		"""
		FeedForwardNetworks are networks that do not work for sequential data. 
		Every input is treated as independent of any previous or following inputs.

		"""

		self._ffn = FeedForwardNetwork()

		"""
			Input layer:
		    R_iP_j (region i, product j) at times (t-T, .., t-1)

		    T - time interval
		    R - number of regions
		    P - number of products

		    RPT - dimensionality of input layer

		    ***
		    input SORTED in ORDER RPT
		    ***
		"""

		dim = T*R*P

		inputL = LinearLayer(T, name="input layer")

		"""
			Layer 1:
		    groups of neurons for R_iP_j
		    k_1*R*P
		"""

		k1 = T/3
		hiddenL_1 = TanhLayer(k1*R*P, name="hidden layer 1 - R_iP_j")

		k2 = k1
		hiddenL_2 = TanhLayer(k2*(R+P), name="hidden layer 2 - R_i, P_j")

		k3 = 2*(R+P)
		hiddenL_3 = TanhLayer(k3, name="hidden layer 3 - random nodes")

		outputL = LinearLayer(R*P, "output layer")


		"""
			add layers to network
		"""
		self._ffn.addInputModule(inputL)
		self._ffn.addOutputModule(outputL)

		self._ffn.addModule(hiddenL_1)
		self._ffn.addModule(hiddenL_2)
		self._ffn.addModule(hiddenL_3)

		"""
			create connections between layers
		"""

		# INPUT => 1ST HIDDEN LAYER

		# T*k2 weights per slice 
		# mother connection to hold shared weights
		mc1 = MotherConnection(T*k1,name="sharedConnection")

		# keep slice indices to check
		inSlices = dict()
		outSlices = dict()

		# keep slices to check
		inputSlices = dict()
		h1Slices = dict()

		# keep connections to check
		sharedConn = dict()

		for i in range(R*P):
			outSlices[i] = (i*T,(i+1)*T-1)
			inSlices[i] = (i*k1, (i+1)*k1-1)

			#print outSlices[i], inSlices[i]

			inputSlices[i] = ModuleSlice(inputL, inSliceFrom=outSlices[i][0], inSliceTo=outSlices[i][1], outSliceFrom=outSlices[i][0], outSliceTo=outSlices[i][1])
			#print inputSlices[i]
			h1Slices[i] = ModuleSlice(hiddenL_1, inSliceFrom=inSlices[i][0], inSliceTo=inSlices[i][1], outSliceFrom=inSlices[i][0],outSliceTo=inSlices[i][1])
			#print h1Slices[i]

			sharedConn[i] = SharedFullConnection(mc1,inputSlices[i],h1Slices[i])
			#print sharedConn[i].params

		for conn in sharedConn.itervalues():
			print conn
			print conn.params
			self._ffn.addConnection(conn)

		# 1ST HIDDEN LAYER => 2ND HIDDEN LAYER
		h2_inIndices = dict()
		h2_inSlices = dict()	
		for i in range(R+P):
			h2_inIndices[i] = (k2*i,k2*(i+1)-1)
			print h2_inIndices[i]
			# no outSlices for h2 since it will be fully connected to h3
			h2_inSlices[i] = ModuleSlice(hiddenL_2, inSliceFrom=h2_inIndices[i][0], inSliceTo=h2_inIndices[i][1])#outSliceFrom=h2_inIndices[i][0], outSliceTo=h2_inIndices[i][1])

		# link each R_iP_j h1Slice with R_i and P_j h2_inSlices respectively
		h1h2Conn = dict()
		# there are R*P h1 slices, take every P slices and link them to P_i
		rj = 0 
		pj = R	
		for i in range(R*P):
			if (i+1)%P==0:
				rj=rj+1
				pj=R
			else:
				pj=pj+1

			h1h2Conn[i] = FullConnection(h1Slices[i], h2_inSlices[rj])
			h1h2Conn[R*P+i] = FullConnection(h1Slices[i], h2_inSlices[pj])

		for conn in h1h2Conn.itervalues():
			print conn
			print conn.params
			self._ffn.addConnection(conn)
				
		# full connection between Region and State layer and random hidden layer
		self._ffn.addConnection(FullConnection(hiddenL_2, hiddenL_3))

		# full connection from random to output layer
		self._ffn.addConnection(FullConnection(hiddenL_3, outputL))

		self._ffn.sortModules()

		#self.to_string()

		#self._ffn.activate()

	def to_string(self):
		for mod in self._ffn.modules:
			for conn in self._ffn.connections[mod]:
				print conn
				for cc in range(len(conn.params)):
					print conn.whichBuffers(cc), conn.params[cc]


if __name__ == "__main__":
	T=10#days
	R=3 #regions
	P=2 #products
	ffn = FFN(R,P,T)		
