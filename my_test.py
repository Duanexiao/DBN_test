#__author__ = 'chaohua'
#import scipy

import cPickle
import gzip
import os
import sys
import time
def load_data(dataset):
    ''' Loads the dataset

    :type dataset: string
    :param dataset: the path to the dataset (here MNIST)
    '''

    #############
    # LOAD DATA #
    #############

    # Download the MNIST dataset if it is not present
    data_dir, data_file = os.path.split(dataset)
    if data_dir == "" and not os.path.isfile(dataset):
        # Check if dataset is in the data directory.
        new_path = os.path.join(os.path.split(__file__)[0], "..", "data", dataset)
        if os.path.isfile(new_path) or data_file == 'mnist.pkl.gz':
            dataset = new_path

    if (not os.path.isfile(dataset)) and data_file == 'mnist.pkl.gz':
        import urllib

        origin = 'http://www.iro.umontreal.ca/~lisa/deep/data/mnist/mnist.pkl.gz'
        print 'Downloading data from %s' % origin
        urllib.urlretrieve(origin, dataset)

    print '... loading data'

    # Load the dataset
    f = gzip.open(dataset, 'rb')
    train_set, valid_set, test_set = cPickle.load(f)
    f.close()

if __name__ == '__main__':
    dataset = 'mnist.pkl.gz'
    load_data(dataset)

'''
import numpy as np
print np.__version__


import math
#tt = np.concatenate((np.ones((3, 3), dtype=np.float), 2*np.ones((2, 3), dtype=np.float)), 0)
tt = np.random.randn(10).reshape((2,5))
tt2 = np.random.randn(10).reshape((2,5))
tt3 = np.concatenate((tt, tt2), axis=0)
print 'ori'
print tt3
tt1 = 1/tt3
print 'tt1'
print tt1
#ttmean = np.mean(tt, axis=0)
#print ttmean
print 'before shuffle'
print tt
tti = np.random.permutation(tt.shape[0])
tt2 = tt[tti]
print tti
print 'after shuffle'
print tt2

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