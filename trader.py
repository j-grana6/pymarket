import numpy as np
from math import copysign


class Trader(object):

    def __init__(self, Book, phi, rho, mu, psi, Sigma, agentid,
                 delta,  initval=100):
        """
        Parameters
        ----------

        Book : OrderBook instance
            The order book instance that the trader participates in

        delta : float
            The standard deviation for in the mean-zero random error
            of agent's  perception of the fundamental value.


        phi : float
            The agent's aggression parameter.  The higher phi, the more likely
            the agent is to place an order when they perceive a mis-valued
            asset

        rho : float
            The patience parameter.  The higher rho is, the more likely an
            agent is to place a limit order when they perceive a mis-valued
            asset.

        mu : float
            The  trader's size parameter.

        psi : float
            The response of order size to a perceived mis-valuation.

        Sigma : float
            The variance of order size.

        agentid : str
            Identifies the Agent

        initval : float
            The initial valuation of the asset

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
        self._side = lambda x: 'S' if x > 0 else 'B'
        self.order = None
        self.agentid = agentid
        self.diff = 10**-10
        self.val = initval
        self._exped = np.exp(np.arange(-(2 / .1 + 1), 1, 1))[::-1]

    #@profile
    def query_agent(self):
        second = self.Book.second
        # What time is it?
        current_price = self.Book.price
        val = self.valuation(self.Book.truep, self.val)
        # Make valuation
        diff = (current_price - val) / float(current_price)
        # Percent misprice
        o_side = self._side(diff)
        # Buy or Sell?
        if self.position[0] == 'in':
            # Remove limit order if valuation changes
            if copysign(1, diff) != copysign(1, self.diff):
            # If valuation has changed
                self._remove_order(self.order)
                # Remove the order
                self.position = ('out', 'NA')
                # Update position
        p_partic = 1 - np.exp(- abs(diff) / (1. / self.phi))
        # Probability of participating
        self.diff = diff
        # Updates last period's diff to this period
        if np.random.uniform() < p_partic:
            # If the agent participates
            oprice = self.order_price()
            # Get order price in $ and cents
            if self.position[0] == 'in':
                # If the agent has a limit order
                self._remove_order(self.order)
                #remove it
            qty = self.order_quantity()
            # Get the order quantity
            self.order = [oprice, qty, (self.Book.day, self.Book.second),
                          self.agentid]
            # Get the agent's order
            if oprice != 'Market':
                oprice = int(oprice * 100)
                # Change order price to only cents
            self.Book.order(self.agentid, oprice, o_side, qty,
                            (self.Book.day, self.Book.second))
            # place order in terms of cents
            if self.oprice == 'Market':
                # If it was a market order
                self.position = ('out', 'NA')
                # The agent is out of the market
            else:
                # If not
                self.position = ('in', o_side)
                # He has a standing limit order

                #@profile
    def _remove_order(self, order):
        """ Removes an order, need to pop key if last order removed!"""
        try:
            self.Book.bids[order[0]].remove(order)
            if len(self.Book.bids[order[0]]) == 0:
                self.Book.bids.pop(order[0])
        except KeyError:
            self.Book.asks[order[0]].remove(order)
            if len(self.Book.asks[order[0]]) == 0:
                self.Book.asks.pop(order[0])

    #@profile
    def order_price(self):
        """ Sets the order price.  If not an order price, set
        to 'Market' """
        scale = abs(self.rho / self.diff)
        exped_fact = 1. / scale
        exped = np.power(self._exped, exped_fact)
        pdist = exped[:-1]-exped[1:]
        cum_pdist = np.cumsum(pdist)
        cum_pdist = cum_pdist/cum_pdist[-1]
        spots_away = np.argmin(cum_pdist < np.random.uniform())
        if spots_away == 0:
            return 'Market'
        elif self.diff > 0:
            # Believes stock is overpriced, so will sell.
            return max(self.Book.bids.keys())/100. + spots_away * .1
        elif self.diff < 0:
            return min(self.Book.asks.keys())/100. - spots_away * .1

    def order_quantity(self):
        """ Draws the order quantity"""
        return np.random.normal(self.mu, self.Sigma) + \
            self.psi*self.Sigma * abs(self.diff)
