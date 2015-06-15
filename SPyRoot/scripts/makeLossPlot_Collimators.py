############################################################
#
# Deprecated: now implemented in python/simulation.py
#
############################################################

#!/usr/bin/env python

from array import array
import os
import argparse
from ROOT import *

LHCring = 26659.
deltaS = 0.1
binadjust = 1./deltaS
print "Using ", int(LHCring/deltaS), "bins of size ",deltaS, "binadjust = ", binadjust

#array containing the edges of the warm areas
warm = [[0.0, 22.5365], [54.853, 152.489], [172.1655, 192.39999999999998], [199.48469999999998, 224.3], [3095.454284, 3155.628584], [3167.740084, 3188.4330840000002], [3211.4445840000003, 3263.867584], [3309.9000840000003, 3354.9740840000004], [3401.005584, 3453.4285840000002], [3476.440084, 3494.065584], [3505.885284, 3568.318584], [6405.4088, 6457.9138], [6468.7785, 6859.513800000001], [6870.3785, 6923.5338], [9735.907016000001, 9824.730516000001], [9830.832016, 9861.730516], [9878.732016, 9939.985516], [9950.548016, 10043.462016], [10054.024516, 10115.278016], [10132.279516, 10163.970516], [10170.072016, 10257.603016], [13104.989233, 13129.804533], [13136.889233, 13157.123733], [13176.800233, 13271.647233], [13306.752733, 13351.825733], [13386.931233000001, 13481.778233000001], [13501.454732999999, 13522.784533], [13529.869233, 13554.684533], [16394.637816, 16450.871316], [16456.972816, 16487.271316000002], [16493.372816, 16830.871316], [16836.972815999998, 16867.271316], [16873.372816, 16928.294816], [19734.8504, 19760.6997], [19771.5644, 20217.9087], [20228.773400000002, 20252.9744], [23089.979683999998, 23138.576984], [23150.396684, 23171.375484], [23194.386984, 23246.809984], [23292.842484, 23337.915484], [23383.947984, 23436.370984], [23459.382483999998, 23480.082484], [23492.193984, 23553.115984], [26433.4879, 26458.3032], [26465.387899999998, 26486.7177], [26506.3942, 26601.2412], [26636.346700000002, 26658.883199999997]]


parser = argparse.ArgumentParser(description=
'Make ntuples from .dat files for one job',
formatter_class=argparse.RawTextHelpFormatter)

parser.add_argument('--inputDir', action='store', type=str,
                    help= 'Specify the input directory \n\
EX: --inputDirectory \'./\' ')

parser.add_argument('--outputDir', action='store', type=str,
                    help= 'Specify the output directory \n\
EX: --outputDirectory \'./\' ')

args=parser.parse_args()

if args.inputDir:
    inputDir = args.inputDir
else:
    inputDir = '/home/mfiascar/Physics/Accelerator/Simulation/Outputs/'

if inputDir[len(inputDir)-1]!="/":
    inputDir = inputDir+"/"

if args.outputDir:
    outputDir = args.outputDir
else:
    outputDir = inputDir
    
if outputDir[len(outputDir)-1]!="/":
    outputDir = outputDir+"/"

beam=1
if (inputDir.find("B2")>=0 or inputDir.find("b2")>=0):
    beam=2

setup="horiz"
if (inputDir.find("Vert")>=0 or inputDir.find("vert")>=0):
    setup="vert"

print "in Ntuple making"
print "inputDir: %s, outputDir: %s, beam %i" %(inputDir, outputDir, beam)

# From CollPositions files get location of collimators
inputCollPosition = inputDir + "clean_input/CollPositions.b%i.dat" %beam
f = open(inputCollPosition)
lines = f.readlines()
f.close()
collPos = {}
icollPos = {}
for l in lines:
    parts = l.split()
    if len(parts) >2:
        if parts[0].find("Ind") >=0:
            continue
        collPos[parts[1]] = [int(parts[0]),float(parts[2])]
        icollPos[parts[0]] = float(parts[2])
print "Size of collPos vector: %i, %i" %( len(collPos), len(icollPos))

#find lengh of collimator
for inDir in os.listdir("%s" %inputDir):
    if inDir.find(".root")>=0:
        continue
    if inDir.find("clean_input") >=0 :
        continue
    #print "Found file for coll lengh"
    fsummary = open(inputDir + inDir+ "/coll_summary.dat",'r')
    sum_lines = fsummary.readlines()
    fsummary.close()
    for l in sum_lines:
        if l.find("icoll") >=0 : #exclude header line
            continue
        s_parts = l.split()
        if len(s_parts) < 4:
            continue
        s_lenght = float(s_parts[6])
        collPos[s_parts[1]] += [ s_lenght]
    break




#create histogram for nabs:
h_coll_norm = TH1F("h_collimator_losses_norm","h_collimator_losses_norm", int(LHCring/deltaS), 0., LHCring) #only used for normalization
h_coll = TH1F("h_collimator_losses","h_collimator_losses", int(LHCring/deltaS), 0., LHCring)
h_coll_fromFluka = TH1F("h_collimator_lossesFromFluka","h_collimator_lossesFromFluka", int(LHCring/deltaS), 0., LHCring)
h_allLHC_losses_norm = TH1F("h_allLHC_losses_norm","h_allLHC_losses_norm", int(LHCring/deltaS), 0., LHCring) #only used for normalization
h_coldlosses = TH1F("h_cold_losses","h_cold_losses", int(LHCring/deltaS), 0., LHCring)
h_warmlosses = TH1F("h_warm_losses","h_warm_losses", int(LHCring/deltaS), 0., LHCring)


#Read in coll_summary.dat - note: need to loop over all sub-directories
inDirs=[]
for inDir in os.listdir("%s" %inputDir):
    if inDir.find(".root")>=0:
        continue
    if inDir.find("clean_input") >=0 :
        continue
    fsummary = open(inputDir + inDir+ "/coll_summary.dat",'r')
    #print "Opened file: %s/coll_summary.dat" %inDir
    sum_lines = fsummary.readlines()
    fsummary.close()
    #print "Reading coll_summary"
    #print sum_lines[0]
    for l in sum_lines:
        if l.find("icoll") >=0 : #exclude header line
            continue
        #find s position corresponding to collimator
        #print l
        s_parts = l.split()
        if len(s_parts) < 4:
            continue
        s_ind = collPos[s_parts[1]][0]
        if not s_ind == int(s_parts[0]):
            print "ERROR: collname ",s_parts[1]," has index ", s_ind ," in CollPositions and ", int(s_parts[0])," in Coll_Summary "
            continue
        s_pos = collPos[s_parts[1]][1]
        lenght = collPos[s_parts[1]][2]
        # now we can fill the histogram:
        #print "Filling coll %s, icoll %i position %f lenght %f with weight %f" %(s_parts[1], int(s_parts[0]), s_pos, lenght, float(s_parts[3]))
        h_coll.Fill(s_pos, float(s_parts[3])/lenght)
        h_coll_norm.Fill(s_pos, float(s_parts[3]))

    inDirs+=[inDir]

print "Found input directories: ",inDirs


#Read in impacts_real.root
fluka = TFile.Open(inputDir + "impacts_all_real.root")
tf = fluka.Get("ntuple")
for entry in range(tf.GetEntries()):
    tf.GetEntry(entry)
    if tf.nabs != 1:
        continue
    s_pos = icollPos["%s" %int(tf.icoll)]
    h_coll_fromFluka.Fill(s_pos)


#Read in LPI_BLP_out.s: info about particles lost in cold losses
flpi = TFile.Open(inputDir + "LPI_BLP_out.s.root")
t = flpi.Get("ntuple")
for entry in range(t.GetEntries()):
    t.GetEntry(entry)
    #print "particle %i lost at s %f" %(t.np,t.s)
    h_allLHC_losses_norm.Fill(t.s)
    
    #check if it is a cold or warm aperture:
    isWarm = False
    for w in range(len(warm)):
        if ( (t.s >= warm[w][0]) and (t.s < warm[w][1]) ):
            isWarm = True
            break
    if isWarm: 
        h_warmlosses.Fill(t.s, binadjust)
    else:
        h_coldlosses.Fill(t.s, binadjust)

    
fout = TFile(outputDir + "StandardSetup_losses_bin%1.1f.root" %deltaS,"recreate")
fout.cd()
h_coll.Write()
h_coll_norm.Write()
h_coldlosses.Write()
h_warmlosses.Write()
h_coll_fromFluka.Write()
h_allLHC_losses_norm.Write()
fout.Close()
