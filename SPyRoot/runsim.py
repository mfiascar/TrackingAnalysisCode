from simulation import *

try:
    directory
except NameError:
    directory = "/home/mfiascar/Physics/Accelerator/Simulation/HL-LHC/v1.0/HorizB1"


#read input and make all root files with plots
sim = simulation(directory)
sim._print()
sim._print_betafunctions()
sim.nsigmaColl()
sim._makeLayout_()
sim.makeLossPlots()
#sim.efficiency()
sim.dispersion()

#inputDir = directory + "/plots"
#execfile("scripts/makePlot.py")




