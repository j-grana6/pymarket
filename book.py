import numpy as np
from collections import defaultdict


class OrderBook(object):
    """
    Order book class
    """
    def __init__(self, bids, asks, vol=0):
        """
        Parameters
        ----------

        bids : defaultdict
            Keys are prices, values are a Deque of lists.  Each element of
            bids are of the form [price, size, time, agentid]

        asks : defaultdict
            Keys are prices, values are a Deque of lists.  Each element of
            asks are of the form [price, size, time, agentid]


        Agents : dict
            Dictionary of all agents that will be in the market.  Keys are
            unique ID numbers, values are trader instances.

        Attributes
        ----------

        second : int
            The second of the day
        day : int
            The day

        Agents : Dict
            Dictionary where keys are agentid and values are agent instance

        truep : float
            The true price of the underlying asset

        price : float
            The price of the last trade

        transactions : dict
            Keys are days.  Entry is a list of transactions

        vol : float
            The volatility of the fundamental value

        """
        self.bids = bids
        self.asks = asks
        self.second = 0
        self.day = 0
        self.Agents = {}
        self.truep = 100
        self.price = 100
        self.transactions = defaultdict(list)
        self.vol = vol
        self._close_price = [self.price] * 100

    def include_agents(self, Agent):
        """
        Adds an agent to the market

        Parameters
        ----------

        Agent : Trader_inst
            a Trader instance
        """
        self.Agents[Agent.agentid] = Agent

    def second_tick(self):
        """ Increase the second by 1"""
        while True:
            self.second += 1
            yield self.second

    def day_tick(self):
        """ Increase the day by 1"""
        while True:
            self.day += 1
            yield self.day

    def move(self):
        """ Moves the fundamental value according to vol"""
        while True:
            if self.vol > 0:
                self.truep += np.random.normal(0, self.vol)
            yield self.truep

    def order(self, agentid, price, side, size, time):
        """ Executes and order

        Parameters
        ----------

        agentid : str
            The id of the agent

        price : str or float
            The limit price or "Market" if the order is a market order

        size : int
            Number of shares

        time : tuple
            The time the order was placed in the form of (day, second)

        side : str
            "B" for buy order, "S" for sell order

            """
        if price == 'Market':
            self._market_order(side, size, time)
            self.transactions[time[0]].append(
                [agentid, self.price, size, time, side])
        else:
            self._limit_order(agentid, price, side, size, time)

    #@profile
    def _limit_order(self, agent_id, order_price, order_side,
                     order_size, time):
        """
        Adds an order to the existing order book.  Meant to be called
        by OrderBook.order.

        Parameters
        ----------

        agentid : str
            Unique agent id

        order_price : float
            The order price

        order_side : str
            "B" or "S"

        order_size : int
            Number of shares

        time : tuple
            (day, second)
        """
        if order_side == 'S':
            self.asks[order_price].append(
                [order_price, order_size, time, agent_id])
        else:
            self.bids[order_price].append(
                [order_price, order_size, time, agent_id])

    #@profile
    def _market_order(self, order_side, order_size, time):
        """ Executes a market order.  Should be called by OrderBook.order

        order_side : str
            "B" or "S"

        order_size : int
            Number of shares

        time : tuple
            (day, second)"""

        if order_side == 'S':
            # If a sell
            while order_size > 0:
                # While there are shares to be traded
                entry = max(self.bids.keys())
                # What is the price
                highest_bid = self.bids[entry][0]
                # The order to be traded with??
                size = min(highest_bid[1], order_size)
                # Size is either order size or lowest ask?
                self.transactions[time[0]].append([highest_bid[3],
                                                  highest_bid[0],
                                                  size, highest_bid[2], 'B'])
                # Record the transaction
                highest_bid[1] = highest_bid[1] - size
                # Trade the shares
                self.price = entry / 100.
                # Set price of last trade in terms of $ and cents
                if highest_bid[1] == 0:
                    # If highest bid is exhausted
                    if highest_bid[3] != 'Me':
                        #If it wasn't part of the initial configuration
                        self.Agents[highest_bid[3]].position = ('out', 'NA')
                        # Change the agents status
                    _ = self.bids[self.price].popleft()
                    # Remove a bid with 0 size
                else:
                    # If the bid is not exhausted
                    if highest_bid[3] != 'Me':
                        # If the order is by an agent
                        self.Agents[highest_bid[3]].order = highest_bid
                        # Change the agent's current order
                if len(self.bids[self.price]) == 0:
                    # If no more bids at that price
                    _ = self.bids.pop(self.price)
                    # Remove price from the dict
                order_size = order_size - size
        else:
            # Buy orders are parallel to sell orders
            while order_size > 0:
                entry = min(self.asks.keys())
                lowest_ask = self.asks[entry][0]
                size = min(lowest_ask[1],  order_size)
                self.transactions[time[0]].append([lowest_ask[3],
                                                  lowest_ask[0],
                                                  size, lowest_ask[2], 'S'])
                lowest_ask[1] = lowest_ask[1] - size
                self.price = lowest_ask[0]
                if lowest_ask[1] == 0:
                    if lowest_ask[3] != 'Me':
                        self.Agents[lowest_ask[3]].position = ('out', 'NA')
                    _ = self.asks[self.price].pop(0)
                else:
                    if lowest_ask[3] != 'Me':
                        self.Agents[lowest_ask[3]].order = lowest_ask
                if len(self.asks[self.price]) == 0:
                    _ = self.asks.pop(self.price)
                order_size = order_size - size
