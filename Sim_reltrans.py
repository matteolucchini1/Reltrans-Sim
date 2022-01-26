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

#Initialize convenient things:
parameters_dbl = ['h1','h2','a','inc','rin','rout','zcos','Gamma','logxi','Afe','lognep','kTe','lumratio','nH','boost','Mass',
                  'floHz','fhiHz','gammac','DelA','DelAB','g','Texp','pow','RESP']

lagonly_dbl = [16,17,18,19,20,21,23]
                  
sim_mode = ""
sim_flavour = ""       
#for now only do _dbl

#step one: ask if user wants a range or fixed values
print("-----------------------------------------------------------------------------------")
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
    print("Input simulation parameters for every spectrum:")
    sim_pars = np.zeros(len(parameters_dbl))
    for i in range(len(parameters_dbl)):
        if (i not in lagonly_dbl):
            print("Input parameter ",i+1,", ",parameters_dbl[i])
            sim_pars[i] = input()
else:
    print("Input simulation parameter range for every spectrum:")  
    sim_pars_min = np.zeros(len(parameters_dbl))
    sim_pars_max = np.zeros(len(parameters_dbl))
    sim_pars = np.zeros(len(parameters_dbl))    
    for i in range(len(parameters_dbl)):
        if (i not in lagonly_dbl):
            print("Input parameter ",i+1,", ",parameters_dbl[i], " min and max values")
            sim_pars_min[i] = input()
            sim_pars_max[i] = input()
            sim_pars[i] = random.uniform(sim_pars_min[i],sim_pars_max[i])

save_file ="Parameters/spec_pars.dat"
save_file = open(save_file, "w") 
for i in range(len(sim_pars)):
    save_file.write(str(sim_pars[i])+"\n")
save_file.close()

#sort out parameters for the simulation of flux energy spectrum:
spec_pars = np.zeros(len(sim_pars)-2)
for i in range(len(spec_pars)):
    if (i < 16):
        spec_pars[i] = sim_pars[i]
    elif (i == 19 or i == 22 or i == 23):
        spec_pars[i] = 1.
    else:
        spec_pars[i] == sim_pars[len(sim_pars)-1]
    
print("Input source flux between 0.5 and 10 keV, in erg/cm^2/s:")
flux_source = input()

print("------------------------------------------------------------------------------------------")
print("Simulating flux energy spectrum:")
print("------------------------------------------------------------------------------------------")
AllModels.lmod("reltrans",dirPath="~/Software/Reltrans")
AllModels.setEnergies("0.5 10.0 250 log")
sim_model = Model("rtransDbl",setPars=spec_pars.tolist())
AllModels.calcFlux("0.5 10.0")
flux_model = AllModels(1).flux
renorm = float(flux_source)/float(flux_model[0])
sim_model.rtransDbl.norm = renorm
AllModels.calcFlux("0.5 10.0")
sim_settings = FakeitSettings(response='~/Data/Response/nicer-rmf6s-teamonly-array50.rmf',arf='~/Data/Response/nicer-consim135p-teamonly-array50.arf',
                              exposure=sim_pars[len(sim_pars)-3],fileName='Products/TimeAveraged_sim.pha')
AllData.fakeit(1,sim_settings,applyStats=True,filePrefix="")
AllData.clear()

print("------------------------------------------------------------------------------------------")
print("Flux energy spectrum done; lag energy spectra left")
print("Type how many lag-energy spectra you want to simulate")
print("------------------------------------------------------------------------------------------")
lagen_number = input()
for j in range(int(lagen_number)):
    if(sim_mode == "value"):
        print("Input simulation parameters for lag energy spectrum:",j+1) 
        lag_pars = np.zeros(len(parameters_dbl))
        for i in range(len(parameters_dbl)):
            if (i in lagonly_dbl):
                print("Input parameter ",i+1,", ",parameters_dbl[i])
                lag_pars[i] = input()
            else:
                lag_pars[i] = sim_pars[i] 
    else:
        print("Input simulation parameter range for every spectrum:")  
        lag_pars_min = np.zeros(len(parameters_dbl))
        lag_pars_max = np.zeros(len(parameters_dbl))
        lag_pars = np.zeros(len(parameters_dbl))    
        for i in range(len(parameters_dbl)):
            if (i in lagonly_dbl):
                print("Input parameter ",i+1,", ",parameters_dbl[i], " min and max values")
                lag_pars_min[i] = input()
                lag_pars_max[i] = input()
                lag_pars[i] = random.uniform(lag_pars_min[i],lag_pars_max[i]) 
            else:
                lag_pars[i] = sim_pars[i] 
    #tbd: save lag parameters 
    print("------------------------------------------------------------------------------------------")
    print("Simulating lag energy spectra:")
    print("------------------------------------------------------------------------------------------")
    print("Note: because Xspec is weird the simulation will be run first with default paramters, then")
    print("with the correct input parameters. Input the same output file name twice to fix this!")
    print("------------------------------------------------------------------------------------------")
    AllModels.setEnergies("0.5 10.0 50 log")
    sim_model = Model("simrtdbl",setPars=lag_pars.tolist())  
    files = str(glob.glob('x*.dat'))
    files = files.replace("'","")
    files = files.replace("[","")
    files = files.replace("]","")
    files_name = files.replace(".dat","")
    save_file ="Parameters/lag_pars_"+files
    save_file = open(save_file, "w") 
    for i in range(len(sim_pars)):
        save_file.write(str(sim_pars[i])+"\n")
    save_file.close()
    flx_call = "flx2xsp " + files + " " + files_name + ".pha " + files_name + ".rsp"
    os.system(flx_call)
    os.system("mv *.dat Raw/")
    os.system("mv *.pha Products/")
    os.system("mv *.rsp Products/")
    AllData.clear()
    
#TBD: figure out different model flavours
