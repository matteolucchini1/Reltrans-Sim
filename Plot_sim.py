import numpy as np
import random
import matplotlib.pyplot as plt
import matplotlib.pylab as pl
import math
import os
import glob
import matplotlib.ticker as plticker
from xspec import *
from matplotlib import cm
from matplotlib.colors import LogNorm
from mpl_toolkits.axes_grid1 import make_axes_locatable

from matplotlib.patches import Polygon
import matplotlib.ticker as plticker
from matplotlib import rc, rcParams
rc('text',usetex=True)
rc('font',**{'family':'serif','serif':['Computer Modern']})
plt.rcParams.update({'font.size': 18})

#xspec settings since pyxspec seems to bypass the xpsec.rc fileName
Xset.abund = "wilm"
Xset.cosmo = "70 0 0.73"
Xset.xsect = "vern"

colors = ['#ff5a00','#ff9c00','#ffde00','#ffeea4','#e6cd6a','#c5a46a','#7b6220','#18394a','#39627b','#62839c','#acacac']
fsize = 26

#parname = ("spec_pars.dat")
parname = ("lag_pars_xLowF.dat")
filename = ("xLowF")
renorm = ("Parameters/renorm.dat")
renorm = np.genfromtxt(renorm)

#this scripts plots the model + simulated data for the given input file. Note that you have to specify the filenames manually
#and tweak a few things for the plot because I'm feeling lazy
pars_sim = np.genfromtxt("Parameters/"+parname)
pars_model = np.zeros(23)

for i in range(len(pars_model)):
    if (i==18 or i == 22):
        pars_model[18] = 6. #pars_model[18] = ReIm, pars_model[22] = RESP
        pars_model[22] = 1.
    else: 
        pars_model[i] = pars_sim[i]
#remember to tweak this to the same value as the simulation script 
       
#load the flux-energy spectrum:
flux_energy = Spectrum("Products/"+filename+".pha")
flux_energy.ignore("**-0.5")
flux_energy.ignore("10.0-**")

AllModels.lmod("reltrans",dirPath="~/Software/Reltrans")
test_model = Model("rtransDbl",setPars=pars_model.tolist())  
#test_model.rtransDbl.norm = renorm

Plot.device = "/xs"
Plot.xAxis = "keV"
Plot.xLog = True
#Plot("eeufspec")
Plot("ufspec")
xVals = Plot.x()
yVals = Plot.y()
xErrs = Plot.xErr()
yErrs = Plot.yErr()
modVals = Plot.model()

Plot("delchi")
xRatio = Plot.x()
yRatio = Plot.y()
yRatioE = Plot.yErr()

unity = np.zeros(len(yRatio))

fig, ((ax1,ax2)) = plt.subplots(2,1,figsize=(9.,9.), gridspec_kw={'height_ratios': [3, 1]})

ax1.errorbar(xVals,yVals,xerr=xErrs,yerr=yErrs,color=colors[8],zorder=2,ls='none')
ax1.scatter(xVals,yVals,color=colors[8],zorder=2)
ax1.plot(xVals,modVals,color=colors[0],linewidth=2.5,zorder=3)
ax1.plot(xVals,unity,color='black',linestyle='dashed',linewidth=2.5,zorder=1)
ax1.set_xscale("log")
#ax1.set_yscale("log")
#ax1.set_ylabel("kev$^{2}$ (counts s$^{-1}$ cm$^{-2}$ kev$^{-1}$)",fontsize=fsize)
ax1.set_ylabel("Lag (s)",fontsize=fsize)
ax1.xaxis.set_major_formatter(plt.NullFormatter())

ax2.errorbar(xRatio,yRatio,yerr=1.,color=colors[0],zorder=1,ls='none')
ax2.scatter(xRatio,yRatio,color=colors[0],zorder=1)
ax2.plot(xRatio,unity,color='black',linestyle='dashed',linewidth=2.5,zorder=2)
ax2.set_xscale("log")
ax2.set_ylim([-4.,4.])
ax2.set_xlabel("keV",fontsize=fsize)
ax2.set_ylabel("$\\Delta \\chi$",fontsize=fsize)

plt.tight_layout()
fig.subplots_adjust(hspace=0)

plt.savefig("Plots/"+filename+".pdf")
plt.show()
