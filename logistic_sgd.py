"""
This tutorial introduces logistic regression using Theano and stochastic
gradient descent.

Logistic regression is a probabilistic, linear classifier. It is parametrized
by a weight matrix :math:`W` and a bias vector :math:`b`. Classification is
done by projecting data points onto a set of hyperplanes, the distance to
which is used to determine a class membership probability.

Mathematically, this can be written as:

.. math::
  P(Y=i|x, W,b) &= softmax_i(W x + b) \\
                &= \frac {e^{W_i x + b_i}} {\sum_j e^{W_j x + b_j}}


The output of the model or prediction is then done by taking the argmax of
the vector whose i'th element is P(Y=i|x).

.. math::

  y_{pred} = argmax_i P(Y=i|x,W,b)


This tutorial presents a stochastic gradient descent optimization method
suitable for large datasets, and a conjugate gradient optimization method
that is suitable for smaller datasets.


References:

    - textbooks: "Pattern Recognition and Machine Learning" -
                 Christopher M. Bishop, section 4.3.2

"""
__docformat__ = 'restructedtext en'

import cPickle
import gzip
import os
import sys
import time

import numpy
import scipy.io as sio
import math

import theano
import theano.tensor as T

from mpl_toolkits.mplot3d import Axes3D
import matplotlib.pyplot as plt

class LogisticRegression(object):
    """Multi-class Logistic Regression Class

    The logistic regression is fully described by a weight matrix :math:`W`
    and bias vector :math:`b`. Classification is done by projecting data
    points onto a set of hyperplanes, the distance to which is used to
    determine a class membership probability.
    """

    def __init__(self, input, n_in, n_out):
        """ Initialize the parameters of the logistic regression

        :type input: theano.tensor.TensorType
        :param input: symbolic variable that describes the input of the
                      architecture (one minibatch)

        :type n_iintn: int
        :param n_in: number of input units, the dimension of the space in
                     which the datapoints lie

        :type n_out: int
        :param n_out: number of output units, the dimension of the space in
                      which the labels lie

        """

        # initialize with 0 the weights W as a matrix of shape (n_in, n_out)
        self.W = theano.shared(value=numpy.zeros((n_in, n_out),
                                                 dtype=theano.config.floatX),
                               name='W', borrow=True)
        # initialize the baises b as a vector of n_out 0s
        self.b = theano.shared(value=numpy.zeros((n_out,),
                                                 dtype=theano.config.floatX),
                               name='b', borrow=True)

        # compute vector of class-membership probabilities in symbolic form
        self.p_y_given_x = T.nnet.softmax(T.dot(input, self.W) + self.b)

        # compute prediction as class whose probability is maximal in
        # symbolic form
        self.y_pred = T.argmax(self.p_y_given_x, axis=1)

        # parameters of the model
        self.params = [self.W, self.b]

    def negative_log_likelihood(self, y):
        """Return the mean of the negative log-likelihood of the prediction
        of this model under a given target distribution.

        .. math::

            \frac{1}{|\mathcal{D}|} \mathcal{L} (\theta=\{W,b\}, \mathcal{D}) =
            \frac{1}{|\mathcal{D}|} \sum_{i=0}^{|\mathcal{D}|} \log(P(Y=y^{(i)}|x^{(i)}, W,b)) \\
                \ell (\theta=\{W,b\}, \mathcal{D})

        :type y: theano.tensor.TensorType
        :param y: corresponds to a vector that gives for each example the
                  correct label

        Note: we use the mean instead of the sum so that
              the learning rate is less dependent on the batch size
        """
        # y.shape[0] is (symbolically) the number of rows in y, i.e.,
        # number of examples (call it n) in the minibatch
        # T.arange(y.shape[0]) is a symbolic vector which will contain
        # [0,1,2,... n-1] T.log(self.p_y_given_x) is a matrix of
        # Log-Probabilities (call it LP) with one row per example and
        # one column per class LP[T.arange(y.shape[0]),y] is a vector
        # v containing [LP[0,y[0]], LP[1,y[1]], LP[2,y[2]], ...,
        # LP[n-1,y[n-1]]] and T.mean(LP[T.arange(y.shape[0]),y]) is
        # the mean (across minibatch examples) of the elements in v,
        # i.e., the mean log-likelihood across the minibatch.
        return -T.mean(T.log(self.p_y_given_x)[T.arange(y.shape[0]), y])

    def errors(self, y):
        """Return a float representing the number of errors in the minibatch
        over the total number of examples of the minibatch ; zero one
        loss over the size of the minibatch

        :type y: theano.tensor.TensorType
        :param y: corresponds to a vector that gives for each example the
                  correct label
        """

        # check if y has same dimension of y_pred
        if y.ndim != self.y_pred.ndim:
            raise TypeError('y should have the same shape as self.y_pred',
                            ('y', target.type, 'y_pred', self.y_pred.type))
        # check if y is of the correct datatype
        if y.dtype.startswith('int'):
            # the T.neq operator returns a vector of 0s and 1s, where 1
            # represents a mistake in prediction
            return T.mean(T.neq(self.y_pred, y))
        else:
            raise NotImplementedError()


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
    #train_set, valid_set, test_set format: tuple(input, target)
    #input is an numpy.ndarray of 2 dimensions (a matrix)
    #witch row's correspond to an example. target is a
    #numpy.ndarray of 1 dimensions (vector)) that have the same length as
    #the number of rows in the input. It should give the target
    #target to the example with the same index in the input.

    def shared_dataset(data_xy, borrow=True):
        """ Function that loads the dataset into shared variables

        The reason we store our dataset in shared variables is to allow
        Theano to copy it into the GPU memory (when code is run on GPU).
        Since copying data into the GPU is slow, copying a minibatch everytime
        is needed (the default behaviour if the data is not in a shared
        variable) would lead to a large decrease in performance.
        """
        data_x, data_y = data_xy
        shared_x = theano.shared(numpy.asarray(data_x,
                                               dtype=theano.config.floatX),
                                 borrow=borrow)
        shared_y = theano.shared(numpy.asarray(data_y,
                                               dtype=theano.config.floatX),
                                 borrow=borrow)
        # When storing data on the GPU it has to be stored as floats
        # therefore we will store the labels as ``floatX`` as well
        # (``shared_y`` does exactly that). But during our computations
        # we need them as ints (we use labels as index, and if they are
        # floats it doesn't make sense) therefore instead of returning
        # ``shared_y`` we will have to cast it to int. This little hack
        # lets ous get around this issue
        return shared_x, T.cast(shared_y, 'int32')

    test_set_x, test_set_y = shared_dataset(test_set)
    valid_set_x, valid_set_y = shared_dataset(valid_set)
    train_set_x, train_set_y = shared_dataset(train_set)

    rval = [(train_set_x, train_set_y), (valid_set_x, valid_set_y),
            (test_set_x, test_set_y)]
    return rval


def sgd_optimization_mnist(learning_rate=0.13, n_epochs=1000,
                           dataset='mnist.pkl.gz',
                           batch_size=600):
    """
    Demonstrate stochastic gradient descent optimization of a log-linear
    model

    This is demonstrated on MNIST.

    :type learning_rate: float
    :param learning_rate: learning rate used (factor for the stochastic
                          gradient)

    :type n_epochs: int
    :param n_epochs: maximal number of epochs to run the optimizer

    :type dataset: string
    :param dataset: the path of the MNIST dataset file from
                 http://www.iro.umontreal.ca/~lisa/deep/data/mnist/mnist.pkl.gz

    """
    datasets = load_data(dataset)

    train_set_x, train_set_y = datasets[0]
    valid_set_x, valid_set_y = datasets[1]
    test_set_x, test_set_y = datasets[2]

    # compute number of minibatches for training, validation and testing
    n_train_batches = train_set_x.get_value(borrow=True).shape[0] / batch_size
    n_valid_batches = valid_set_x.get_value(borrow=True).shape[0] / batch_size
    n_test_batches = test_set_x.get_value(borrow=True).shape[0] / batch_size

    ######################
    # BUILD ACTUAL MODEL #
    ######################
    print '... building the model'

    # allocate symbolic variables for the data
    index = T.lscalar()  # index to a [mini]batch
    x = T.matrix('x')  # the data is presented as rasterized images
    y = T.ivector('y')  # the labels are presented as 1D vector of
    # [int] labels

    # construct the logistic regression class
    # Each MNIST image has size 28*28
    classifier = LogisticRegression(input=x, n_in=28 * 28, n_out=10)

    # the cost we minimize during training is the negative log likelihood of
    # the model in symbolic format
    cost = classifier.negative_log_likelihood(y)

    # compiling a Theano function that computes the mistakes that are made by
    # the model on a minibatch
    test_model = theano.function(inputs=[index],
                                 outputs=classifier.errors(y),
                                 givens={
                                     x: test_set_x[index * batch_size: (index + 1) * batch_size],
                                     y: test_set_y[index * batch_size: (index + 1) * batch_size]})

    validate_model = theano.function(inputs=[index],
                                     outputs=classifier.errors(y),
                                     givens={
                                         x: valid_set_x[index * batch_size:(index + 1) * batch_size],
                                         y: valid_set_y[index * batch_size:(index + 1) * batch_size]})

    # compute the gradient of cost with respect to theta = (W,b)
    g_W = T.grad(cost=cost, wrt=classifier.W)
    g_b = T.grad(cost=cost, wrt=classifier.b)

    # specify how to update the parameters of the model as a list of
    # (variable, update expression) pairs.
    updates = [(classifier.W, classifier.W - learning_rate * g_W),
               (classifier.b, classifier.b - learning_rate * g_b)]

    # compiling a Theano function `train_model` that returns the cost, but in
    # the same time updates the parameter of the model based on the rules
    # defined in `updates`
    train_model = theano.function(inputs=[index],
                                  outputs=cost,
                                  updates=updates,
                                  givens={
                                      x: train_set_x[index * batch_size:(index + 1) * batch_size],
                                      y: train_set_y[index * batch_size:(index + 1) * batch_size]})

    ###############
    # TRAIN MODEL #
    ###############
    print '... training the model'
    # early-stopping parameters
    patience = 5000  # look as this many examples regardless
    patience_increase = 2  # wait this much longer when a new best is
    # found
    improvement_threshold = 0.995  # a relative improvement of this much is
    # considered significant
    validation_frequency = min(n_train_batches, patience / 2)
    # go through this many
    # minibatche before checking the network
    # on the validation set; in this case we
    # check every epoch

    best_params = None
    best_validation_loss = numpy.inf
    test_score = 0.
    start_time = time.clock()

    done_looping = False
    epoch = 0
    while (epoch < n_epochs) and (not done_looping):
        epoch = epoch + 1
        for minibatch_index in xrange(n_train_batches):

            minibatch_avg_cost = train_model(minibatch_index)
            # iteration number
            iter = (epoch - 1) * n_train_batches + minibatch_index

            if (iter + 1) % validation_frequency == 0:
                # compute zero-one loss on validation set
                validation_losses = [validate_model(i)
                                     for i in xrange(n_valid_batches)]
                this_validation_loss = numpy.mean(validation_losses)

                print('epoch %i, minibatch %i/%i, validation error %f %%' % \
                      (epoch, minibatch_index + 1, n_train_batches,
                       this_validation_loss * 100.))

                # if we got the best validation score until now
                if this_validation_loss < best_validation_loss:
                    #improve patience if loss improvement is good enough
                    if this_validation_loss < best_validation_loss * \
                            improvement_threshold:
                        patience = max(patience, iter * patience_increase)

                    best_validation_loss = this_validation_loss
                    # test it on the test set

                    test_losses = [test_model(i)
                                   for i in xrange(n_test_batches)]
                    test_score = numpy.mean(test_losses)

                    print(('     epoch %i, minibatch %i/%i, test error of best'
                           ' model %f %%') %
                          (epoch, minibatch_index + 1, n_train_batches,
                           test_score * 100.))

            if patience <= iter:
                done_looping = True
                break

    end_time = time.clock()
    print(('Optimization complete with best validation score of %f %%,'
           'with test performance %f %%') %
          (best_validation_loss * 100., test_score * 100.))
    print 'The code run for %d epochs, with %f epochs/sec' % (
        epoch, 1. * epoch / (end_time - start_time))
    print >> sys.stderr, ('The code for file ' +
                          os.path.split(__file__)[1] +
                          ' ran for %.1fs' % ((end_time - start_time)))


# This function to load data from .mat file
# modified from load_data()
# Apr 15, Chaohua Wu
def mat_load_data(dataset_path):
    ''' Loads the dataset

    :type dataset: string
    :param dataset: the path to the dataset (here MNIST)
    '''

    #############
    # LOAD DATA #
    #############

    # Download the MNIST dataset if it is not present
    mat_dataset = sio.loadmat(dataset_path)
    print '... loading data'
    kalfeature_train = mat_dataset['kalfeature_train']
    kalfeature_valid = mat_dataset['kalfeature_test']
    kalfeature_test = mat_dataset['feature_test']

    trial_train, feat_dim = kalfeature_train.shape
    trial_valid = kalfeature_valid.shape[0]
    trial_test = kalfeature_test.shape[0]

    kalfeature_mean = numpy.mean(kalfeature_train, axis=0)
    kalfeature_train = kalfeature_train - numpy.tile(kalfeature_mean, (trial_train, 1))
    kalfeature_valid = kalfeature_valid - numpy.tile(kalfeature_mean, (trial_valid, 1))
    kalfeature_test = kalfeature_test - numpy.tile(kalfeature_mean, (trial_test, 1))

    kalfeature_std = numpy.std(kalfeature_train, axis=0)
    kalfeature_invstd = numpy.diag(1/kalfeature_std)
    kalfeature_train = numpy.dot(kalfeature_train, kalfeature_invstd)
    kalfeature_valid = numpy.dot(kalfeature_valid, kalfeature_invstd)
    kalfeature_test = numpy.dot(kalfeature_test, kalfeature_invstd)

    label_train = numpy.squeeze(mat_dataset['labels_train']-1)
    label_valid = numpy.squeeze(mat_dataset['labels_test']-1)
    label_test = numpy.squeeze(mat_dataset['labels_test_AR']-1)



    '''
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


    mat_dataset = sio.loadmat(dataset_path)
    print '... loading data'
    feature1 = mat_dataset['EEG_feature1']
    feature2 = mat_dataset['EEG_feature2']
    feature3 = mat_dataset['EEG_feature3']

    trial_num1, feat_dim1 = feature1.shape
    trial_num2, feat_dim2 = feature2.shape
    trial_num3, feat_dim3 = feature3.shape

    # normalize to zero-mean and unit variance
    feature_all = numpy.concatenate((feature1, feature2, feature3), axis=0)
    feature_mean = numpy.mean(feature_all, axis=0)

    feature1 = feature1 - numpy.tile(feature_mean, (trial_num1, 1))
    feature2 = feature2 - numpy.tile(feature_mean, (trial_num2, 1))
    feature3 = feature3 - numpy.tile(feature_mean, (trial_num3, 1))

    feature_std = numpy.std(feature_all, axis=0)
    feature_invstd = numpy.diag(1/feature_std)
    feature1 = numpy.dot(feature1, feature_invstd)
    feature2 = numpy.dot(feature2, feature_invstd)
    feature3 = numpy.dot(feature3, feature_invstd)

    feature_all = numpy.concatenate((feature1, feature2, feature3), axis=0)
    print numpy.mean(feature_all, axis=0)
    print numpy.std(feature_all, axis=0)




    if (feat_dim1 != feat_dim2) or (feat_dim2 != feat_dim3) or (feat_dim1 != feat_dim3):
        print 'feature dimensions do not match'

    num_train = int(0.7 * min([trial_num1, trial_num2, trial_num3]))
    num_valid = int(num_train / 7 * 2)
    num_test1 = trial_num1 - num_train - num_valid
    num_test2 = trial_num2 - num_train - num_valid
    num_test3 = trial_num3 - num_train - num_valid

    index1 = numpy.random.permutation(trial_num1)
    train_index1 = index1[0:num_train]
    valid_index1 = index1[num_train:num_train + num_valid]
    test_index1 = index1[-num_test1:] # to fix it
    index2 = numpy.random.permutation(trial_num2)
    train_index2 = index2[0:num_train]
    valid_index2 = index2[num_train:num_train + num_valid]
    test_index2 = index2[-num_test2:]
    index3 = numpy.random.permutation(trial_num3)
    train_index3 = index3[0:num_train]
    valid_index3 = index3[num_train:num_train + num_valid]
    test_index3 = index3[-num_test3:]


    train_set_label = numpy.array(
        list(numpy.zeros(num_train, dtype=numpy.int64)) + list(numpy.ones(num_train, dtype=numpy.int64)) \
        + list(2 * numpy.ones(num_train, dtype=numpy.int64)))

    valid_set_label = numpy.array(
        list(numpy.zeros(num_valid, dtype=numpy.int64)) + list(numpy.ones(num_valid, dtype=numpy.int64)) \
        + list(2 * numpy.ones(num_valid, dtype=numpy.int64)))

    test_set_label = numpy.array(
        list(numpy.zeros(num_test1, dtype=numpy.int64)) + list(numpy.ones(num_test2, dtype=numpy.int64)) \
        + list(2 * numpy.ones(num_test3, dtype=numpy.int64)))

    train_set_data = numpy.concatenate(
        (feature1[train_index1, :], feature2[train_index2, :], feature3[train_index3, :]), 0)
    valid_set_data = numpy.concatenate(
        (feature1[valid_index1, :], feature2[valid_index2, :], feature3[valid_index3, :]), 0)
    test_set_data = numpy.concatenate(
        (feature1[test_index1, :], feature2[test_index2, :], feature3[test_index3, :]), 0)

    ##############plot to verify correct import
    fig = plt.figure()
    ax = fig.add_subplot(111, projection='3d')

    for p_index in range(num_valid):
        ax.scatter(valid_set_data[p_index, 0], valid_set_data[p_index, 1], valid_set_data[p_index, 2], c='b', marker="^")

    for p_index in range(num_valid, 2 * num_valid):
        ax.scatter(valid_set_data[p_index, 0], valid_set_data[p_index, 1], valid_set_data[p_index, 2], c='r', marker="o")

    for p_index in range(2 * num_valid, 3*num_valid):
        ax.scatter(valid_set_data[p_index, 0], valid_set_data[p_index, 1], valid_set_data[p_index, 2], c='y', marker="h")

    ax.set_xlabel('X Label')
    ax.set_ylabel('Y Label')
    ax.set_zlabel('Z Label')

    plt.show()

    ####################################################

    train_shuffle_index = numpy.random.permutation(train_set_data.shape[0])
    train_set_data = train_set_data[train_shuffle_index, :]
    train_set_data *= 1000
    train_set_label = train_set_label[train_shuffle_index]

    valid_shuffle_index = numpy.random.permutation(valid_set_data.shape[0])
    valid_set_data = valid_set_data[valid_shuffle_index, :]
    valid_set_data *= 1000
    valid_set_label = valid_set_label[valid_shuffle_index]

    test_shuffle_index = numpy.random.permutation(test_set_data.shape[0])
    test_set_data = test_set_data[test_shuffle_index, :]
    test_set_data *= 1000
    test_set_label = test_set_label[test_shuffle_index]
    #train_set = [train_set_data, train_set_label]
    #valid_set = [valid_set_data, valid_set_label]
    #test_set = [test_set_data, test_set_label]
    '''
    '''
    # Load the dataset
    f = gzip.open(dataset, 'rb')
    train_set, valid_set, test_set = cPickle.load(f)
    f.close()
    '''

    #train_set, valid_set, test_set format: tuple(input, target)
    #input is an numpy.ndarray of 2 dimensions (a matrix)
    #witch row's correspond to an example. target is a
    #numpy.ndarray of 1 dimensions (vector)) that have the same length as
    #the number of rows in the input. It should give the target
    #target to the example with the same index in the input.

    def shared_dataset(data_x, data_y, borrow=True):
        """ Function that loads the dataset into shared variables

        The reason we store our dataset in shared variables is to allow
        Theano to copy it into the GPU memory (when code is run on GPU).
        Since copying data into the GPU is slow, copying a minibatch everytime
        is needed (the default behaviour if the data is not in a shared
        variable) would lead to a large decrease in performance.
        :rtype : object
        """
        # data_x, data_y = data_xy
        shared_x = theano.shared(numpy.asarray(data_x,
                                               dtype=theano.config.floatX),
                                 borrow=borrow)
        shared_y = theano.shared(numpy.asarray(data_y,
                                               dtype=theano.config.floatX),
                                 borrow=borrow)
        # When storing data on the GPU it has to be stored as floats
        # therefore we will store the labels as ``floatX`` as well
        # (``shared_y`` does exactly that). But during our computations
        # we need them as ints (we use labels as index, and if they are
        # floats it doesn't make sense) therefore instead of returning
        # ``shared_y`` we will have to cast it to int. This little hack
        # lets ous get around this issue
        return shared_x, T.cast(shared_y, 'int32')

    train_set_x, train_set_y = shared_dataset(kalfeature_train, label_train)
    valid_set_x, valid_set_y = shared_dataset(kalfeature_valid, label_valid)
    test_set_x, test_set_y = shared_dataset(kalfeature_test, label_test)

    rval = [(train_set_x, train_set_y), (valid_set_x, valid_set_y),
            (test_set_x, test_set_y)]
    return rval


if __name__ == '__main__':
    sgd_optimization_mnist()
