# Script to compute the efficiency vs. amplitude

from array import array
import os
import argparse
from ROOT import *

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


heff_rad = TH1F("efficiency_vs_amplitude_rad","efficiency_vs_amplitude_rad",40,0.,20.)
heff_x = TH1F("efficiency_vs_amplitude_x","efficiency_vs_amplitude_x",40,0.,20.)
heff_y = TH1F("efficiency_vs_amplitude_y","efficiency_vs_amplitude_y",40,0.,20.)
h_ntot_abs = TH1F("ntot_abs_vs_amplitude","ntot_abs_vs_amplitude",40,0.,20.)


#Read in coll_summary.dat - note: need to loop over all sub-directories
inDirs=[]
for inDir in os.listdir("%s" %inputDir):
    if inDir.find(".root")>=0:
        continue
    if inDir.find("clean_input") >=0 :
        continue
    if not os.path.isfile(inputDir + inDir+ "/efficiency.dat"):
        continue
    inDirs+=[inDir]
    fsummary = open(inputDir + inDir+ "/efficiency.dat",'r')
    #print "Opened file: %s/efficiency.dat" %inDir
    sum_lines = fsummary.readlines()
    fsummary.close()
    #print "Reading coll_summary"
    #print sum_lines[0]
    for l in sum_lines:
        if l.find("rad_sigma") >=0 : #exclude header line
            continue
        #find s position corresponding to collimator
        #print l
        s_parts = l.split()
        if len(s_parts) < 8:
            continue
        print "num rad %1.2f, x %1.2f, y %1.2f, n_abs %1.2f" %(float(s_parts[4]),float(s_parts[5]), float(s_parts[6]),float(s_parts[7]) )
        heff_rad.Fill(float(s_parts[0]),float(s_parts[4]))
        heff_x.Fill(float(s_parts[0]),float(s_parts[5]))
        heff_y.Fill(float(s_parts[0]),float(s_parts[6]))
        h_ntot_abs.Fill(float(s_parts[0]),float(s_parts[7]))
print "Found input directories: ",inDirs

#Now file efficiency efficiency_dpop.dat
#Take binning from the .dat file
bins = []
ffile = open(inputDir + inDirs[0]+ "/efficiency_dpop.dat",'r')
lines = ffile.readlines()
ffile.close()
for l in lines:
    if l.find("n_dpop") >=0 :
        continue
    bins+= [float(l.split()[0])]
if bins[0] < 1e-11:
    bins[0]=1e-11
print "Bins: ", bins
my_bins = array('d',bins)

heff_dpop =  TH1F("efficiency_vs_dpOverp","efficiency_vs_dpOverp",len(bins)-1,my_bins)
h_ntot_abs_dpop = TH1F("ntot_abs_vs_dpOverp","ntot_abs_vs_dpOverp",len(bins)-1,my_bins)

for inDir in inDirs:
    fsummary = open(inputDir + inDir+ "/efficiency_dpop.dat",'r')
    sum_lines = fsummary.readlines()
    fsummary.close()
    for l in sum_lines:
        if l.find("n_dpop") >=0 :
            continue
        s_parts = l.split()
        if len(s_parts) < 4:
            continue
        bin0 = float(s_parts[0])
        if bin0 < 1e-11: 
            bin0=1e-11
        heff_dpop.Fill(bin0,float(s_parts[2]))
        h_ntot_abs_dpop.Fill(bin0,float(s_parts[3]))
        #print "Dir %s Filling line %f content %f" %(inDir,float(s_parts[0]),float(s_parts[3]))


heff_rad_num = heff_rad.Clone("efficiency_vs_amplitude_rad_num")
heff_x_num = heff_x.Clone("efficiency_vs_amplitude_x_num")
heff_y_num = heff_y.Clone("efficiency_vs_amplitude_y_num")
heff_dpop_num = heff_dpop.Clone("efficiency_vs_dpOverp_num")

heff_rad.Divide(h_ntot_abs)
heff_x.Divide(h_ntot_abs)
heff_y.Divide(h_ntot_abs)
heff_dpop.Divide(h_ntot_abs_dpop)

for i in range(heff_rad.GetNbinsX()):
    if h_ntot_abs.GetBinContent(i) > 0:
        heff_rad.SetBinError(i, sqrt(heff_rad.GetBinContent(i)*(1-heff_rad.GetBinContent(i))/h_ntot_abs.GetBinContent(i) )  )
        heff_x.SetBinError(i, sqrt(heff_x.GetBinContent(i)*(1-heff_x.GetBinContent(i))/h_ntot_abs.GetBinContent(i) )  )
        heff_y.SetBinError(i, sqrt(heff_y.GetBinContent(i)*(1-heff_y.GetBinContent(i))/h_ntot_abs.GetBinContent(i) )  )

for i in range(heff_dpop.GetNbinsX()):
    #print "Bin %i, content %i" %(i,h_ntot_abs_dpop.GetBinContent(i))
    if h_ntot_abs_dpop.GetBinContent(i) > 0:
        if heff_dpop.GetBinContent(i) >= 1.:
            error = 0.
        else:
            error = sqrt(heff_dpop.GetBinContent(i)*(1-heff_dpop.GetBinContent(i))/h_ntot_abs_dpop.GetBinContent(i))
        heff_dpop.SetBinError(i, error)  

import RootStyles
rs = RootStyles.RootStyles()
rs.setAtlasStyle2()
rs.style.cd()
rs.style.SetPadRightMargin( 0.17 )
rs.style.SetPadTopMargin( 0.07 )
rs.style.SetPaintTextFormat("2.1f")
ROOT.gROOT.ForceStyle()

fout = TFile(outputDir + "Efficiency.root" ,"recreate")
fout.cd()

heff_rad.SetMarkerStyle(20)
heff_x.SetMarkerStyle(20)
heff_y.SetMarkerStyle(20)
heff_rad_num.SetMarkerStyle(20)
heff_x_num.SetMarkerStyle(20)
heff_y_num.SetMarkerStyle(20)
h_ntot_abs.SetMarkerStyle(20)
heff_dpop.SetMarkerStyle(20)
h_ntot_abs_dpop.SetMarkerStyle(20)

heff_rad.Write()
heff_x.Write()
heff_y.Write()
heff_rad_num.Write()
heff_x_num.Write()
heff_y_num.Write()
h_ntot_abs.Write()
heff_dpop.Write()
h_ntot_abs_dpop.Write()
heff_dpop_num.Write()

#plot for Ineff vs amplit
c = TCanvas("Ineff_vs_amplit","c")
c.cd()
c.SetLogy()
c.SetGridy()
heff_rad.GetXaxis().SetTitle("Radial Aperture, A_{0} [#sigma]")
heff_rad.GetXaxis().SetRangeUser(6.,15.)
heff_rad.GetYaxis().SetTitle("Cleaning inefficiency, #eta (A_{0})")
heff_rad.GetYaxis().SetRangeUser(1e-5,1.)
heff_rad.Draw()
c.Write()
c.Print(outputDir + "Efficiency_vs_amplitude.pdf")
c.Print(outputDir + "Efficiency_vs_amplitude.png")

#plot for Ineff vs Doverp
c = TCanvas("Ineff_vs_dpOverp","c")
c.cd()
c.SetLogy()
#c.SetGridy()
#c.SetLogx()
heff_dpop.GetXaxis().SetTitle("#Deltap/p")
heff_dpop.GetXaxis().SetRangeUser(1e-4,0.01)
heff_dpop.GetYaxis().SetTitle("Cleaning inefficiency, #eta (#Deltap/p)")
#heff_dpop.GetYaxis().SetRangeUser(5e-6,1.5)
heff_dpop.Draw()
c.Write()
c.Print(outputDir + "Efficiency_vs_dOverp.pdf")
c.Print(outputDir + "Efficiency_vs_dOverp.png")

fout.Close()
