import numpy as np
params = {
'num_inst': 20, # Number of institutional traders
'num_chart': 250, # number of chartists
'num_chart2': 100,
'fund_vol': 0, # Volatility of fundamental value
'delta' : lambda lims : np.random.uniform(lims[0], lims[1]), #draw delta
'deltalimsc': (0, 1), # Limits for perception error
'deltalimsi': (0, .0001),
'beta' : lambda betalims : np.random.uniform(betalims[0], betalims[1]),
'betalims' : (.2,.8),
'phi' : lambda lims : np.random.uniform(lims[0], lims[1]), # Agression
'philims' : (20,50),
'rholims' : (.2, .5),
'rho' : lambda lims : np.random.uniform(lims[0], lims[1]),
'muchart' : lambda : np.random.normal(20000, 4000),
'muinst' : lambda : np.random.normal(100000, 10000),
'Sigmachart' : lambda : np.random.uniform(100,500),
'Sigmainst' : lambda : np.random.uniform(10000, 15000),
'psi' : lambda : np.random.uniform(10, 50),
'horizon': lambda : np.random.uniform(10,30)
}
