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
from rebin_spec import *

from matplotlib.patches import Polygon
import matplotlib.ticker as plticker
from matplotlib import rc, rcParams
rc('text',usetex=True)
rc('font',**{'family':'serif','serif':['Computer Modern']})
plt.rcParams.update({'font.size': 18})

#Initialize convenient things:
parameters_dbl = ['h1','h2','a','inc','rin','rout','zcos','Gamma','logxi','Afe','lognep','kTe','lumratio','nH','boost','Mass',
                  'floHz','fhiHz','gammac','DelA','DelAB','g','Texp','pow','RESP','Tin']

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

#sort out parameters for the simulation of flux energy spectrum:
#we need one array dedicated to reltrans (to calculate its normalisation) and a full one to pass to the actual simulation
model_pars = np.zeros(len(sim_pars)+1)
rtrans_pars = np.zeros(len(sim_pars)-2)

for i in range(len(model_pars)):
    if (i < 16): #up to the BH mass, the input parameters are identical to those of rtransDbl 
        model_pars[i] = sim_pars[i]
    elif i in range(16,18):  #set fmin, fmax to 0
        model_pars[i] = 0. 
    elif i in range(19,22):
        model_pars[i] = 0. #set phiA, phiAB, g to 0
    elif (i==24):
        model_pars[i] = sim_pars[13]  #When adding tbabs*diskbb, make nH identical 
    elif (i==25):
        model_pars[i] = sim_pars[len(sim_pars)-1] #set the disk temperature
    else:
        model_pars[i] = 1. #set everything else to 1, which sets the model to run the flux-energy spectrum
for i in range(len(rtrans_pars)):
    rtrans_pars[i] = model_pars[i]

print("Input coronal flux between 0.5 and 10 keV, in erg/cm^2/s:")
flux_corona = input()

print("Input disk flux between 0.5 and 10 keV, in erg/cm^2/s:")
flux_disk = input()

save_file ="Parameters/model_pars.dat"
save_file = open(save_file, "w") 
for i in range(len(model_pars)):
    save_file.write(str(model_pars[i])+"\n")
save_file.close()

#clear flies in the Products folder:
print("------------------------------------------------------------------------------------------")
print("Type y if you want to remove the previous files - not that this is necessary if you are")
print("going to use the same file names:")
print("------------------------------------------------------------------------------------------")
test = input()
if(test == "y"):
    os.system("rm Products/*")
    os.system("rm Raw/*")


print("------------------------------------------------------------------------------------------")
print("Simulating flux energy spectrum:")
print("Output file prefix:")
spectrum_name = input()
spectrum_file = "Products/" + spectrum_name + ".pha"
oversample_file = "Products/" + spectrum_name + "_sampled.pha"
rebin_file = "Products/" + spectrum_name + "_rebin.pha"
print("------------------------------------------------------------------------------------------")
#xspec settings since pyxspec seems to bypass the xpsec.rc fileName
Xset.abund = "wilm"
Xset.cosmo = "70 0 0.73"
Xset.xsect = "vern"

AllModels.lmod("reltrans",dirPath="~/Software/Reltrans")

corona_model = Model("rtransDbl",setPars=rtrans_pars.tolist())
AllModels.calcFlux("0.5 10.0")
flux_model = AllModels(1).flux
renorm_corona = float(flux_corona)/float(flux_model[0])
print(renorm_corona)
AllModels.clear()

disk_model = Model("diskbb",setPars=[model_pars[25],model_pars[26]])
AllModels.calcFlux("0.5 10.0")
flux_model = AllModels(1).flux
renorm_disk = float(flux_disk)/float(flux_model[0])
print(renorm_disk)
AllModels.clear()

#TBD: add the calibration features from Jingyi's paper? Unsure if necessary
save_file = "Parameters/renorm.dat"
save_file = open(save_file, "w") 
save_file.write(str(renorm_corona)+"\n")
save_file.write(str(renorm_disk)+"\n")
save_file.close()

sim_model = Model("rtransDbl+TBabs*diskbb",setPars=model_pars.tolist())  
sim_model.rtransDbl.norm = renorm_corona
sim_model.diskbb.norm = renorm_disk 
AllModels.calcFlux("0.5 10.0")
AllModels.show()
sim_settings = FakeitSettings(response='~/Data/Response/nicer-rmf6s-teamonly-array50.rmf',arf='~/Data/Response/nicer-consim135p-teamonly-array50.arf',
                              exposure=sim_pars[22],fileName=spectrum_file)
AllData.fakeit(1,sim_settings,applyStats=True,filePrefix="")
AllData.clear()
AllModels.clear()
print("------------------------------------------------------------------------------------------")
print("Calling grppha to over-sample the instrument resolution;")
print("Type the following in the grppha command line: ")
print("reset quality & bad 0-29 1200-1500 &  systematics 0-299 0.02 & group nicer_channels_to_group.txt & exit")
print("------------------------------------------------------------------------------------------")
resolution_oversample_string = "grppha " + spectrum_file + " " + oversample_file
print(resolution_oversample_string)
os.system(resolution_oversample_string)
jsgroup(oversample_file,20.,rebin_file)
print("Final product: " + rebin_file)

print("------------------------------------------------------------------------------------------")
print("Flux energy spectrum done; lag energy spectra left")
print("Type how many lag-energy spectra you want to simulate")
print("------------------------------------------------------------------------------------------")
lagen_number = input()
for j in range(int(lagen_number)):
    if(sim_mode == "value"):
        print("Input simulation parameters for lag energy spectrum:",j+1) 
        lag_pars = np.zeros(len(parameters_dbl))
        for i in range(len(parameters_dbl)-1):
            if (i in lagonly_dbl):
                print("Input parameter ",i+1,", ",parameters_dbl[i])
                lag_pars[i] = input()
                if(i==16 or i ==17):
                    print("At this frequency, phase wrapping is:",1./(2.*lag_pars[i])," s")
            else:
                lag_pars[i] = sim_pars[i] 
    else:
        print("Input simulation parameter range for lag energy spectrum:")  
        lag_pars_min = np.zeros(len(parameters_dbl)-1)
        lag_pars_max = np.zeros(len(parameters_dbl)-1)
        lag_pars = np.zeros(len(parameters_dbl)-1)    
        for i in range(len(parameters_dbl)):
            if (i in lagonly_dbl):
                print("Input parameter ",i+1,", ",parameters_dbl[i], " min and max values")
                lag_pars_min[i] = input()
                lag_pars_max[i] = input()
                lag_pars[i] = random.uniform(lag_pars_min[i],lag_pars_max[i]) 
            else:
                lag_pars[i] = sim_pars[i] 
    lag_pars[len(lag_pars)-1] = 1.
    print("------------------------------------------------------------------------------------------")
    print("Simulating lag energy spectra:")
    print("------------------------------------------------------------------------------------------")
    print("Note: because Xspec is weird the simulation will be run first with default paramters, then")
    print("with the correct input parameters. Input the same output file name twice to fix this!")
    print("------------------------------------------------------------------------------------------")
    AllModels.setEnergies("0.5 10.0 25 log")
    sim_model = Model("simrtdbl",setPars=lag_pars.tolist())  
    files = str(glob.glob('x*.dat'))
    files = files.replace("'","")
    files = files.replace("[","")
    files = files.replace("]","")
    files_name = files.replace(".dat","")
    save_file ="Parameters/lag_pars_"+files
    save_file = open(save_file, "w") 
    for i in range(len(lag_pars)):
        save_file.write(str(lag_pars[i])+"\n")
    save_file.close()
    flx_call = "flx2xsp " + files + " " + files_name + ".pha " + files_name + ".rsp"
    os.system(flx_call)
    AllData.clear()
    AllModels.clear()
    os.system("mv *.dat Raw/")
    os.system("mv *.pha Products/")
    os.system("mv *.rsp Products/")
#for some reason I don't understand sometimes this needs to be called twice....   
#os.system("mv *.dat Raw/")
#TBD: figure out different model flavours

print("Simulation completed, full output in Products/")
