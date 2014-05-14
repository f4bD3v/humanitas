import pybrain as pb
from pybrain.structure.connections import FullConnection as C, MotherConnection, \
        SharedFullConnection 

def buildModel1(T=50, K1=10, K2=5, K3=10, R=10, P=10):
    net = pb.FeedForwardNetwork()

    l0 = pb.LinearLayer(T * R * P, name='layer 0')
    l1 = pb.TanhLayer(K1 * R * P, name='layer 1')
    l2 = pb.TanhLayer(K2 * (R + P), name='layer 2')
    l3 = pb.TanhLayer(K3, name='layer 3')
    l4 = pb.LinearLayer(R * P, name='layer 4')

    net.addInputModule(l0)
    net.addModule(l1)
    net.addModule(l2)
    net.addModule(l3)
    net.addOutputModule(l4)

    # 0-1 connections
    mother = MotherConnection(T * K1)
    for i in xrange(R*P):
        name = 'R_%02dP_%02d -> R_%02dP_%02d' % (i//P, i%P, i//P, i%P)
        net.addConnection( 
                #C(l0, l1, name, i*T, (i+1)*T, 
                SharedFullConnection(mother, l0, l1, name, i*T, (i+1)*T, 
                    i*K1, (i+1)*K1) 
        )

    # 1-2 connections
    for i in xrange(R*P):
        name = 'R_%02dP_%02d -> R_%02d' % (i//P, i%P, i//P)
        net.addConnection( 
                C(l1, l2, name, i*K1, (i+1)*K1, (i//P)*K2, (i//P+1)*K2)
        )
        name = 'R_%dP_%d -> P_%d' % (i//P, i%P, i%P)
        net.addConnection(
                C(l1, l2, name, i*K1, (i+1)*K1, K2*(R+i%P), K2*(R+i%P+1))
        )

    # 2-3 connections
    net.addConnection(C(l2, l3, 'R_i,P_j -> H'))

    # 3-4 connections
    net.addConnection(C(l3, l4, 'H -> OUT'))

    # 2-4 connections
    for i in xrange(R):
        name = 'R_%02d -> O' % i
        net.addConnection(
                C(l2, l4, name, i*K2, (i+1)*K2, i*P, (i+1)*P)
        )
    for i in xrange(P):
        name = 'P_%02d -> O' % i
        for j in xrange(R):
            net.addConnection(
                    C(l2, l4, name, (R+i)*K2, (R+i+1)*K2,
                        j*P + i, j*P+i+1)
            )

    # 1-4 connections
    for i in xrange(R*P):
        name = 'R_%02dP_%02d -> O' % (i//P, i%P)
        net.addConnection(
                C(l1, l4, name, i*K1, (i+1)*K1, i, i+1)
        )

    net.sortModules()
    #printModel(net)
    #print net.activate(np.random.normal(size=T*R*P))

    return net

def buildModel2(T=50, K0=5, K1=15, K2=30, R=10, P=10):
    net = pb.FeedForwardNetwork()

    l0 = pb.LinearLayer(T * R * P, name='layer 0')
    l1 = pb.TanhLayer((K0 + K1) * R * P, name='layer 1')
    l2 = pb.TanhLayer(K2, name='layer 2')
    l3 = pb.LinearLayer(R * P, name='layer 3')
    bias = pb.BiasUnit(name='bias')
    
    net.addInputModule(l0)
    net.addModule(l1)
    net.addModule(l2)
    net.addModule(bias)
    net.addOutputModule(l3)

    net.addConnection(C(bias, l1))
    net.addConnection(C(bias, l2))
    net.addConnection(C(bias, l3))

    mother0 = MotherConnection(K0)
    mother1 = MotherConnection((T-1)*K1)
    for i in xrange(R*P):
        name = 'initial[R_%02dP%02d] -> 1[%02d]' % (i//P, i%P, i)
        net.addConnection(SharedFullConnection(mother0, l0, l1, name, 
            i*T, i*T+1, i*(K0+K1), i*(K0+K1)+K0))
        name = 'ratios[R_%02dP%02d] -> 1[%02d]' % (i//P, i%P, i)
        net.addConnection(SharedFullConnection(mother1, l0, l1, name, 
            i*T+1, (i+1)*T, i*(K0+K1)+K0, (i+1)*(K0+K1)))

    net.addConnection(C(l1, l2))
    net.addConnection(C(l2, l3))

    net.sortModules()

    return net


def buildEasyModel(T=50, K1=10, K2=5, K3=10, R=10, P=10):
    net = pb.FeedForwardNetwork()

    l0 = pb.LinearLayer(T * R * P, name='layer 0')
    l1 = pb.SigmoidLayer(10)
    l2 = pb.SigmoidLayer(10)
    l3 = pb.LinearLayer(R * P, name='layer 4')

    net.addInputModule(l0)
    net.addModule(l1)
    net.addModule(l2)
    net.addOutputModule(l3)

    net.addConnection(C(l0, l1))
    net.addConnection(C(l1, l2))
    net.addConnection(C(l2, l3))
    
    net.sortModules()
    return net
