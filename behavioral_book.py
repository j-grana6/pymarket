"""
JG's modification of GP's Order Book.
"""

import numpy as np
from math import copysign, e
import statsmodels.api as sm
from numpy.linalg import pinv

def initbook(abook, numbids=400, numasks=400):
    """ Puts some orders around the starting price of
       an order book.
       """
    price = abook.price
    price = int(price)
    bidsrange = np.arange(price - 5, price, .2)
    askrange = np.arange(price+.2, price + 5, .2)
    sizerange = np.arange(5000,20000, 2000)
    for _ in xrange(numbids):
        bidindex = np.random.random_integers(0, len(bidsrange)-1)
        sizeindex = np.random.random_integers(0, len(sizerange)-1)
        price = bidsrange[bidindex]
        price = "{0:.2f}".format(price)
        price =int(float(price)+.02) + \
            int((float(price[-3:]) + .02) * 10) / 10.
        price = "{0:.2f}".format(price)
        price =int(float(price) + .02) + float(price[-3:])
        size = round(sizerange[sizeindex],2)
        try:
            abook.bids[price].append([price, size,   (0,0), 'Me'])
        except KeyError:
            abook.bids[price]=[[price, size,(0,0), 'Me']]
    for _ in xrange(numasks):
        askindex = np.random.random_integers(0, len(askrange)-1)
        sizeindex = np.random.random_integers(0, len(sizerange)-1)
        price = askrange[askindex]
        price = "{0:.2f}".format(price)
        price =int(float(price)+.02) + float(price[-3:])
        size = round(sizerange[sizeindex],2)
        try:
            abook.asks[price].append([price, size,(0,0), 'Me'])
        except KeyError:
            abook.asks[price]=[[price, size,(0,0), 'Me']]
    return 'Book Filled'







class Results(object):
    def __init__(self, Book):
        self.Book = Book

    def get_tickets(self):
        trans_dict = self.Book.transactions
        trades = []
        end_trade=[]
        for day in trans_dict.keys():
            numtrades = len(trans_dict[day])
            if numtrades !=0:
                end_trade.append(trans_dict[day][-1][1])
                for t in range(numtrades):
                    trades.append(trans_dict[day][t][1])
            else:
                end_trade.append(self.Book.price)
        return trades, end_trade

    def intraday(self, day):
        trans_dict = self.Book.transactions
        trades = []
        numtrades = len(trans_dict[day])
        for t in range(numtrades):
            trades.append(trans_dict[day][t][1])
        return trades


    def inst_chart_vol(self):
        trans_dict = self.Book.transactions
        chartvol = []
        chart2vol= []
        instvol  = []
        for day in trans_dict.keys():
            cvolday=0
            c2volday=0
            ivolday=0
            numtrades = len(trans_dict[day])
            for t in range(numtrades):
                if trans_dict[day][t][0][0] =='I':
                    ivolday += trans_dict[day][t][2]
                elif trans_dict[day][t][0][:3] =='C2-':
                    c2volday += trans_dict[day][t][2]
                else:
                    cvolday +=trans_dict[day][t][2]
            chartvol.append(cvolday)
            instvol.append(ivolday)
            chart2vol.append(c2volday)
        return chartvol, instvol, chart2vol

    def get_x_axis(self):
        trans_dict = self.Book.transactions
        times = []
        for day in trans_dict.keys():
            numtrades = len(trans_dict[day])
            for t in range(numtrades):
                time = (trans_dict[day][t][3][0] - 1)*len(self.Book.Agents.keys()) + \
                    trans_dict[day][t][3][1]
                times.append(time)
        times = np.asarray(times)
        times = times/float(len(self.Book.Agents.keys()))
        return times

    def buy_sell_vol(self):
        trans_dict = self.Book.transactions
        chartvol = []
        chart2vol = []
        instvol  = []
        for day in trans_dict.keys():
            cvolday=0
            ivolday=0
            c2volday=0
            numtrades = len(trans_dict[day])
            for t in range(numtrades):
                if trans_dict[day][t][0][0] =='I':
                    if trans_dict[day][t][4] =='B':
                        ivolday += trans_dict[day][t][2]
                    else:
                        ivolday -= trans_dict[day][t][2]
                elif trans_dict[day][t][0][:3]=='C2-':
                    if trans_dict[day][t][4] =='B':
                        c2volday += trans_dict[day][t][2]
                    else:
                        c2volday -= trans_dict[day][t][2]
                else:
                    if trans_dict[day][t][4] =='B':
                        cvolday += trans_dict[day][t][2]
                    else:
                        cvolday -= trans_dict[day][t][2]

            chartvol.append(cvolday)
            instvol.append(ivolday)
            chart2vol.append(c2volday)
        return chartvol, instvol, chart2vol

    def n_day_returns(self, n):
        prices = np.asarray(self.get_tickets()[1])
        days = np.arange(n, len(prices), 1)
        nret = (prices[n :] - prices[:-n]) / prices[:-n]
        return nret

def go(i):
    from collections import defaultdict
    the_book = OrderBook({}, {}, vol=params['fund_vol'])
    initbook(the_book)
    for chart in xrange(params['num_chart']):
        Chartist(the_book, params['phi'](params['philims']),
                 params['rho'](params['rholims']), params['muchart'](),
                 params['psi'](), params['Sigmachart'](), 'C'+str(chart),
                 params['delta']((params['deltalimsc'][0], params['deltalimsc'][1])),
                 params['beta']((params['betalims'][0],params['betalims'][1])),
                 initval = np.random.uniform(99, 101))
    for inst in xrange(params['num_inst']):
        Institution(the_book, phi = params['phi'](params['philims']),
                    rho=params['rho'](params['rholims']),
                    mu=params['muinst'](),
                 psi=params['psi'](), Sigma=params['Sigmainst'](), agentid='I'+str(inst),
                 delta=params['delta'](params['deltalimsi']), initval=100)
    for chart in xrange(params['num_chart2']):
        Chartist2(the_book, params['phi'](params['philims']),
                 params['rho'](params['rholims']), params['muchart'](),
                 params['psi'](), params['Sigmachart'](), 'C2-'+str(chart),
                 params['delta']((1, 2)),
                 params['beta']((params['betalims'][0],params['betalims'][1])),
                 initval = np.random.uniform(99, 101), horizon = int(params['horizon']()))

    the_book.truep=100
    trueps = [the_book.truep]
    for day in range(600):

        next(the_book.move())
        # if int(day)/40 * 40==day:
        #     the_book.truep +=4
        # if int(day)/80 * 80 == day:
        #     the_book.truep -=8
        trueps.append(the_book.truep)
        if day == 200:
           the_book.truep += 3
        # #print 'Price', the_book.price
        #if day ==300:
        #   the_book.truep  += 1
        #if day == 400:
        #    the_book.truep += 1
        # if day == 1000:
        #     the_book.truep= 102
        the_book.second=0
        next(the_book.day_tick())
        print 'The day:', day
        print 'Observed Price', the_book.price
        print 'True Price', the_book.truep
        the_book.transactions[the_book.day] = []
        agent_order = np.random.choice(the_book.Agents.values(),
                size = len(the_book.Agents), replace=False)
        for agnt in agent_order:
            agnt.query_agent()
        the_book._close_price.append(the_book.price)
    res = Results(the_book)
    daily_prices = res.get_tickets()[1]
    dates = res.get_x_axis()
    chart_vol_directed = res.buy_sell_vol()[0]
    inst_vol_directed = res.buy_sell_vol()[1]
    chart2_vol_directed = res.buy_sell_vol()[2]
    chart_vol_und=res.inst_chart_vol()[0]
    inst_vol_und = res.inst_chart_vol()[1]
    chart2_vol_und=res.inst_chart_vol()[2]
    print str(i)*10
    return daily_prices, chart_vol_directed, inst_vol_directed, chart2_vol_directed, chart_vol_und, inst_vol_und, chart2_vol_und, trueps[1:]


#daily_prices, chart_vol_directed, inst_vol_directed, chart2_vol_directed, chart_vol_und, inst_vol_und, chart2_vol_und = go()

from matplotlib import pyplot as plt
def make_plots(meandata):
    fig, ((ax1, ax2, ax3), (ax5, ax6, ax7)) = plt.subplots(2,3)
    cross = np.argmax(np.asarray(meandata[0]) >103)
    # ax1.set_title('Observed Price')
    ax1.plot(np.asarray(meandata[2]))
    ax1.set_title('Net Volume of Institutions')
    ax5.plot(meandata[5])
    ax5.set_title('Total institutional volume')
    ax2.plot(meandata[1])
    ax2.set_title('Net Volume of Anchor Traders')
    ax6.plot(meandata[4])
    ax6.set_title('Total Volume of Anchor Traders')
    ax3.plot(meandata[3])
    ax3.set_title('Net volume of Extrapolate Trader ')
    ax7.plot(meandata[6])
    ax7.set_title('Total Volume of Extrapolate Trader')
    plt.figure(111)
    plt.plot(np.arange(len(meandata[0])), meandata[0])
    plt.title('Observed Price')
    plt.hlines(103, 0, 400)
    plt.vlines(cross, 100, 103)
    allax = [ax1, ax2, ax3, ax5, ax6, ax7]
    for ax in allax:
        ax.vlines(cross, ax.get_ylim()[0], ax.get_ylim()[1])


newres = []
for i in range(20):
    newres.append(go(i))




