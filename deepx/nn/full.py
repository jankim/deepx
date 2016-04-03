from .. import backend as T

from ..core import ShapedLayer

class Linear(ShapedLayer):

    def initialize(self):
        if not self.is_elementwise():
            self.init_parameter('W', (self.get_shape_in(), self.get_shape_out()))
            self.init_parameter('b', self.get_shape_out())

    def is_elementwise(self):
        return self._elementwise

    def _infer(self, shape_in):
        if self.is_elementwise():
            return shape_in
        return self.shape_out

    def activate(self, X):
        if self.is_elementwise():
            raise Exception("No identity nodes allowed.")
        return X

    def _forward(self, X):
        if self.is_elementwise():
            return self.activate(X)
        W, b = self.parameters['W'], self.parameters['b']
        return self.activate(T.dot(X, W) + b)

    def __str__(self):
        if self.is_elementwise():
            return "%s()" % self.__class__.__name__
        return "%s(%s, %s)" % (self.__class__.__name__,
                               self.get_shape_in(), self.get_shape_out())
class Maxout(Linear):


    def __init__(self, shape_in=None, shape_out=None, k=4, **kwargs):
        self.k = k
        super(Maxout, self).__init__(shape_in=shape_in,
                                     shape_out=shape_out,
                                     k=self.k, **kwargs)

    def __str__(self):
        return "%s(%s, %s)" % (self.__class__.__name__,
                               self.get_shape_in(), self.get_shape_out())
    def initialize(self):
        self.init_parameter('W', (self.k, self.get_shape_in(), self.get_shape_out()))
        self.init_parameter('b', (self.k, self.get_shape_out()))

    def activate(self, X):
        return T.max(X, axis=1)

class Softmax(Linear):

    def __init__(self, *args, **kwargs):
        super(Softmax, self).__init__(*args, **kwargs)
        self.T = self.config.get('T', 1.0)

    def activate(self, X):
        return T.softmax(X, self.T)

class Sigmoid(Linear):

    def activate(self, X):
        return T.sigmoid(X)

class Tanh(Linear):

    def activate(self, X):
        return T.tanh(X)

class Relu(Linear):

    def activate(self, X):
        return T.relu(X)

class Elu(Linear):

    def __init__(self, *args, **kwargs):
        super(Elu, self).__init__(*args, **kwargs)
        self.alpha = self.config.get('alpha', 1.0)

    def activate(self, X):
        return T.relu(X) + self.alpha * (T.exp((X - abs(X)) * 0.5) - 1)

class LeakyRelu(Linear):

    def __init__(self, *args, **kwargs):
        super(LeakyRelu, self).__init__(*args, **kwargs)
        self.alpha = self.config.get('alpha', 0.1)

    def activate(self, X):
        return T.relu(X, alpha=self.alpha)

class Tanlu(Linear):

    def initialize(self):
        super(Tanlu, self).initialize()
        self.init_parameter('alpha', self.get_shape_out(), value=0.5)

    def activate(self, X):
        alpha = self.get_parameter('alpha')
        constrained_alpha = T.clip(alpha, 0, 1)
        return constrained_alpha * T.tanh(X) + (1 - constrained_alpha) * T.relu(X)
