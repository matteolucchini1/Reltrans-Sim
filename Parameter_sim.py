import numpy as np
import matplotlib.pyplot as plt
import matplotlib.pylab as pl
import math
import matplotlib.ticker as plticker
import xspec
from matplotlib import cm
from matplotlib.colors import LogNorm
from mpl_toolkits.axes_grid1 import make_axes_locatable

from matplotlib.patches import Polygon
import matplotlib.ticker as plticker
from matplotlib import rc, rcParams
rc('text',usetex=True)
rc('font',**{'family':'serif','serif':['Computer Modern']})
plt.rcParams.update({'font.size': 18})

#step one: ask if user wants a range or fixed values
print("This utility simulates a set of time-independent spectra from the reltransDbl model")
print("-----------------------------------------------------------------------------------")

#if they want fixed values, ask for input

#if they want a range, ask for min and max

#save parameters to file

#run fakeit for spectra

#later: 1)figure out how to do lags - probably from xspec interface?
#2) figure out different model flavours?
