import numpy as np


class Trader(object):

    def __init__(self, Book, phi, rho, mu, psi, Sigma, agentid,
                    delta, beta = None,  initval=100, horizon=20):

        """
        Parameters
        ----------

        Book : OrderBook instance
            The order book instance that the trader participates in

        delta : float
            The standard deviation for in the mean-zero random error
            of agent's  perception of the fundamental value.

        beta : float
            The exponential smoothing parameter on price change for chartist


        phi : float
            The agent's aggression parameter.  The higher phi, the more likely the agent is
            to place an order when they perceive a mis-valued asset

        rho : float
            The patience parameter.  The higher rho is, the more likely an agent is to place
            a limit order when they perceive a mis-valued asset.

        mu : float
            The  trader's size parameter.

        psi : float
            The response of order size to a perceived mis-valuation.

        Sigma : float
            The variance of order size.

        agentid : str
            Identifies the Agent

        horizon : int
            The number of periods an trend follower forecasts

        Attributes
        ----------

        position : tuple
            Either (out, 'NA'), (in, 'B'), (in, 'S).  Indicated whether the
            agent has a position in the market and whether it is a buy or sell
            position.

        val : float
            The agent's valuation of the stock

        diff : float
             The difference between the Agent's belief and observed price

        order : 4-tuple
            The agent's last limit order.  None if no orders

        oqty : float
            The agent's most recent order quantity

        oprice : float
            The agent's most recent order price
        """


        self.Book = Book
        self.delta = delta
        self.phi = phi
        self.rho = rho
        self.mu = mu
        self.psi = psi
        self.Sigma = Sigma
        self.position = ('out', 'NA')
        self._side = lambda x : 'S' if x>0 else 'B'
        self.order = None
        self.agentid = agentid
        self.beta = beta   # Only defined for Chartist
        self.diff = 10**-10
        self.Book.include_agents(self)
        self.val = initval
        self.horizon = horizon
        self.lookback = sm.add_constant(np.arange(self.horizon))
        self._exped = np.exp(np.arange(-(2 / .1+1),1,1))[::-1]
        self.oqty = 0
        self.oprice = 0 # TODO hide attributes used in simulation


    #@profile
    def query_agent(self):# TODO add documentation
        next(self.Book.second_tick())
        second = self.Book.second
        self.valuation(self.Book.truep, self.val)
        diff = (self.Book.price - self.val) / float(self.Book.price)
        o_side = self._side(diff) #potential buy or sell
        if self.position[0] == 'in': # Remove limit order if valuation changes
            if copysign(1, diff) != copysign(1, self.diff):
                self._remove_order(self.order)
                self.position = ('out', 'NA')
        p_partic = 1 - np.exp(- abs(diff)/ (1./self.phi))
        self.diff = diff # Updates last period's diff to this period
        if np.random.uniform() <  p_partic:
            self.order_price()
            if self.oprice != 'Market':
                self.oprice = "{0:.2f}".format(self.oprice)
                order_price = self.oprice  #TODO CHANGE PRICES TO CENTS TO AVOID THIS
                self.oprice =int(float(order_price) + .02) + \
                    int((float(order_price[-3:]) + .02) * 10) / 10.
            if self.position[0] == 'in':
                self._remove_order(self.order)
            self.order_quantity()
            self.order = [self.oprice, self.oqty,
                          (self.Book.day, self.Book.second),self.agentid]
            self.Book.order(self.agentid, self.oprice, oside, self.oqty,
                            (self.Book.day, self.Book.second)) #place order
            if self.oprice == 'Market':
                self.position = ('out', 'NA')
            else:
                self.position = ('in', o_side)
    #@profile
    def _remove_order(self, order):
        """ Removes an order, need to pop key if last order removed!"""
        try :  #TODO determine order side and remove appropriately
            self.Book.bids[order[0]].remove(order)
            if len(self.Book.bids[order[0]])==0:
                self.Book.bids.pop(order[0])
        except KeyError:
            self.Book.asks[order[0]].remove(order)
            if len(self.Book.asks[order[0]])==0:
                self.Book.asks.pop(order[0])


    #@profile
    def order_price(self):
        """ Sets the order price.  If not an order price, set
        to 'Market' """
        scale= abs(self.rho / self.diff)
        exped_fact= 1. / scale
        exped = np.power(self._exped,exped_fact)
        pdist = exped[:-1]-exped[1:]
        cum_pdist = np.cumsum(pdist)
        cum_pdist = cum_pdist/cum_pdist[-1]
        spots_away = np.argmin(cum_pdist < np.random.uniform())
        if spots_away == 0:
            self.oprice = 'Market'
        elif self.diff > 0: #  Believes stock is overpriced, so will sell.
            self.oprice = max(self.Book.bids.keys()) +  spots_away * .1
        elif self.diff < 0 :
            self.oprice = min(self.Book.asks.keys()) - spots_away * .1

    def order_quantity(self):
        """ Draws the order quantity"""
        self.oqty = np.random.normal(self.mu, self.Sigma) + \
            self.psi*self.Sigma * abs(self.diff)
