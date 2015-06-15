###################################################
#
# Compute the mean losses for CL1 and 2 in the DS
#
###################################################

Cl = { 'Cl1': [20260. , 20340.] , 
       'Cl2': [20360., 20460. ] ,
       'Cl3': [20500., 20560.] }

#inputFilebin1 = TFile.Open("/home/mfiascar/Physics/Accelerator/Simulation/Outputs/StandardSetup_losses_bin0.1.root")
#inputFilebin1 = TFile.Open("/home/mfiascar/Physics/Accelerator/Simulation/HL-LHC/v1.0/HorizB1_onlyIR7_thicktothin/plots/StandardSetup_losses_bin0.1.root")
#inputFilebin1 = TFile.Open("/home/mfiascar/Physics/Accelerator/Simulation/HL-LHC/v1.0_with_IR7_plus_oneDScoll/HorizB1/plots/StandardSetup_losses_bin0.1.root")
inputFilebin1 = TFile.Open("/home/mfiascar/Physics/Accelerator/Simulation/HL-LHC/v1.0_with_IR7_plus_twoDScoll/HorizB1/plots/StandardSetup_losses_bin0.1.root")
#inputFilebin2 = TFile.Open("/home/mfiascar/Physics/Accelerator/Simulation/Outputs/StandardSetup_losses_bin1.0.root")

h1 = inputFilebin1.Get("h_cold_losses")
hcollim_norm = inputFilebin1.Get("h_collimator_losses_norm")
h_allLHC_losses_norm = inputFilebin1.Get("h_allLHC_losses_norm")
nabs = hcollim_norm.Integral() + h_allLHC_losses_norm.Integral()
print "File1 normalization: ", nabs
#h1.Scale(1./nabs)

#h2 = inputFilebin2.Get("h_cold_losses")
#hcollim_norm2 = inputFilebin2.Get("h_collimator_losses_norm")
#h_allLHC_losses_norm2 = inputFilebin2.Get("h_allLHC_losses_norm")
#nabs2 = hcollim_norm2.Integral() + h_allLHC_losses_norm2.Integral()
#print "File2 normalization: ", nabs2
#h2.Scale(1./nabs2)


#Start with first file, loop over bins in range and find average plus integral:
for clus in Cl:
    myCl = Cl[clus]

    print "*************************"
    print ""
    print "Looking at cluster %s" %clus
    print ""
    print "*************************"

    start = h1.FindBin(myCl[0])
    stop = h1.FindBin(myCl[1])
    bmin = -1
    bmax = -1
    print "----------------------"
    print "FILE 1"
    print "Going to loop from bin %i to bin %i" %(start, stop)
    #Find bin to start with for average
    for i in range(start, stop):
        c = h1.GetBinContent(i)
        if c == 0:
            continue
        if (i > bmin):
            bmin = i
            break
    #Find bin to stop with for average
    for i in range(stop, start, -1):
        c = h1.GetBinContent(i)
        if c == 0:
            continue
        if (i > bmax):
            bmax = i
            break
    print "Going to average from bin %i to bin %i" %(bmin, bmax)
    ntot = 0.
    av = 0.
    integral = 0.
    for i in range(bmin,bmax):
        av += h1.GetBinContent(i)
        ntot +=1
    integral = av
    if ntot != 0.:
        av= av/ntot
    print "Average for cluster %s from %i entries: %f" %(clus, ntot, av)
    print "Integral: %f" %(integral)
    print ""

    #start = h2.FindBin(myCl[0])
    #stop = h2.FindBin(myCl[1])
    #bmin = -1
    #bmax = -1
    #print "----------------------"
    #print "FILE 2"
    #print "Going to loop from bin %i to bin %i" %(start, stop)
    ##Find bin to start with for average
    #for i in range(start, stop):
    #    c = h2.GetBinContent(i)
    #    if c == 0:
    #        continue
    #    if (i > bmin):
    #        bmin = i
    #        break
    ##Find bin to stop with for average
    #for i in range(stop, start, -1):
    #    c = h2.GetBinContent(i)
    #    if c == 0:
    #        continue
    #    if (i > bmax):
    #        bmax = i
    #        break
    #print "Going to average from bin %i to bin %i" %(bmin, bmax)
    #ntot2 = 0.
    #av2 = 0.
    #for i in range(bmin,bmax):
    #    av2 += h2.GetBinContent(i)
    #    ntot2 +=1
    #av2= av2/ntot2
    #print "Average for cluster %s from %i entries: %f" %(clus, ntot2, av2)
    #print ""

    

