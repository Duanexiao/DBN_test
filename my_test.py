#__author__ = 'chaohua'
#import scipy
import numpy as np
import math
tt = np.concatenate((np.ones((5, 13), dtype=np.float), 2*np.ones((5, 16), dtype=np.float)), 1)
print tt
'''
tt = [[1,3,4],[2,4,5],[1,5,7],[1,5,6]]
tt2 = np.array(tt)
kk1, kk2 = tt2.shape

#print kk1
#print kk2
tt3 = tt2[1, :]
tt3 = tt3[-3:]
print tt3
tt3 = numpy.random.permutation(10)[0:3]
tt4 = math.floor(4.3)
print tt3
print tt4
#scipy.test()
'''