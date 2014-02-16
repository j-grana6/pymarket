import numpy as np

class Institution(Trader):
    def __init__(self):
        super(Institution, self).__init__()

    def valuation(self, truep, vt_1=None):
        self.val =  truep + np.random.normal(0, self.delta)
        return self.val
