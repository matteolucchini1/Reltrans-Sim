import numpy as np
import random
import matplotlib.pyplot as plt
import matplotlib.pylab as pl
import math
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

#Initialize convenient things:
parameters_dbl = ['h1','h2','a','inc','rin','rout','zcos','Gamma','logxi','Afe','lognep','kTe','lumratio','nH','boost','Mass',
                  'floHz','fhiHz','ReIm','DelA','DelAB','g','RESP','norm']
parameters_dcp = ['h1','a','inc','rin','rout','zcos','Gamma','logxi','Afe','lognep','kTe','nH','boost','Mass','floHz','fhiHz',
                  'ReIm','DelA','DelAB','g','RESP','norm']
parameters_dist = ['h1','a','inc','rin','rout','zcos','Gamma','dist','Afe','lognep','kTe','nH','qboost','Mass','honr','b1','b2',
                   'ReIm','floHz','fhiHz','DelA','DelAB','g','RESP','norm']
#note: texp and pow are done later when calling fakeit

sim_mode = ""
sim_flavour = ""                 
                   
#for now only do _dbl

#step one: ask if user wants a range or fixed values
print("This utility simulates a set of time-independent spectra from the reltransDbl model")
print("Do you want to specify parameter values or parameter ranges for the simulation?")
print("Type either range or value:")
print("-----------------------------------------------------------------------------------")
while (len(sim_mode) == 0):
    sim_mode = input()
    if(sim_mode != "range" and sim_mode != "value"):
        print("There's a typo in your input, specify either range or value!")
        sim_mode = ""
#ask for input
if(sim_mode == "value"):
    print("Input simulation parameters:")
    sim_pars = np.zeros(len(parameters_dbl))
    for i in range(len(parameters_dbl)):
        if (i<16 or i>19):  #this excludes the frequency ranges and ReIm, which are specificed later, and DelA 
            print("Input parameter ",i+1,", ",parameters_dbl[i])
            sim_pars[i] = input()
    sim_pars[16] = 0.
    sim_pars[17] = 0.
    sim_pars[18] = 1
    sim_pars[19] = 0.
    #print(sim_pars)
else:
    print("Input simulation parameter range:")
    sim_pars_min = np.zeros(len(parameters_dbl))
    sim_pars_max = np.zeros(len(parameters_dbl))
    sim_pars = np.zeros(len(parameters_dbl))    
    for i in range(len(parameters_dbl)):
        if (i<16 or i>19):  #this excludes the frequency ranges and ReIm, which are specificed later, and DelA 
            print("Input parameter ",i+1,", ",parameters_dbl[i], " min and max values")
            sim_pars_min[i] = input()
            sim_pars_max[i] = input()
            sim_pars[i] = random.uniform(sim_pars_min[i],sim_pars_max[i])
    sim_pars[16] = 0.
    sim_pars[17] = 0.
    sim_pars[18] = 1
    sim_pars[19] = 0.
    #print(sim_pars)
save_file ="Parameters/sim_pars.dat"
save_file = open(save_file, "w") 
for i in range(len(sim_pars)):
    save_file.write(str(sim_pars[i])+"\n")
save_file.close()
#Input flux and exposure time, set up the model spectrum, and run the simulation for the time averaged spectrum
print("Simulating spectra:")
print("Input source flux between 0.5 and 10 keV, in erg/cm^2/s:")
flux_source = input()
print("Input exposure:")
Texp = input()
AllModels.lmod("reltrans",dirPath="~/Software/Reltrans")
sim_model = Model("rtransDbl",setPars=sim_pars.tolist())
AllModels.calcFlux("0.5 10.0")
flux_model = AllModels(1).flux
renorm = float(flux_source)/float(flux_model[0])
sim_model.rtransDbl.norm = renorm
AllModels.calcFlux("0.5 10.0")
sim_settings = FakeitSettings(response='~/Data/Response/nicer-rmf6s-teamonly-array50.rmf',arf='~/Data/Response/nicer-consim135p-teamonly-array50.arf',
                              exposure=Texp,fileName='Products/TimeAveraged_sim.pha')
AllData.fakeit(1,sim_settings,applyStats=True,filePrefix="")
                 

#later: 1)figure out how to do lags - probably from xspec interface?
#2) figure out different model flavours?
