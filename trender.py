from numpy.linalg import pinv
import numpy as np
from statsmodels.tools import add_constant

class Trender(Trader):

    def __init__(self, horizon, lookback):
        super(Trender, self).__init__()
        self.horizon = horizon
        self.lookback = sm.add_constant(np.arange(self.horizon))

    def valuation(self, truep, vt_1):
        betas = np.dot(pinv(self.lookback), self.Book._close_price[-self.horizon:])
        self.val = np.dot(betas, np.array([[1], [self.horizon*2]]))
        return self.val
