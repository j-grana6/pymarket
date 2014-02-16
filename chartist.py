import numpy as np
from trader import Trader


class Chartist(Trader):
    """
    An exponential smoothing trader

    Parameters
    ----------

    bets : float
        Belief stickiness to past price
    """

    def __init__(self, beta):
        super(Chartist, self).__init__()
        self.beta = beta

    def valuation(self, truep, vt_1):
        self.val =   self.beta * self.Book.price + \
          (1 - self.beta) * vt_1 + np.random.normal(0, self.delta)
        return self.val
