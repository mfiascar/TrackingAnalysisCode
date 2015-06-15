# This script makes phase space plots at different s point using the file
# /home/mfiascar/Physics/Accelerator/Simulation/FCC/TOY_V1/GaussDist/Tracks2_part102.root
# The file contains:
# - the tracking of one particle over 200 turns
# - one TGraph and one TGraph2D for each turn, storing the x-y trajectories at each s position 

from ROOT import *
import RootStyles
rs = RootStyles.RootStyles()

fileName = "/home/mfiascar/Physics/Accelerator/Simulation/FCC/TOY_V1/GaussDist/plots/Tracks2_part101.root"
f = TFile.Open(fileName)
href= f.Get("x_xp_trajectory_turn1")

#number of turns to analyze
nturns = 200

#how many points to sample
my_npoints = 20
npoints = href.GetN()
delta_npoint = npoints/my_npoints
sval =[]
h_x_xp = []
for i in range(my_npoints):
    sval += [ href.GetX()[i*delta_npoint] ]
    myh = TH2F("x_xp_phase_space_s_%2.1f" %sval[i], "x_xp_phase_space_s_%2.1f" %sval[i], 200, -1.,1.,200, -0.01,0.01)
    h_x_xp += [ myh.Clone()]

for n in range(nturns):
    h = f.Get("x_xp_trajectory_turn%i" %(n+1))
    for i in range(my_npoints):
        h_x_xp[i].Fill(h.GetY()[i*delta_npoint], h.GetZ()[i*delta_npoint])
    

#f.Close()
fout = TFile("/home/mfiascar/Physics/Accelerator/Simulation/FCC/TOY_V1/GaussDist/plots/Tracks2_part101_phasespace.root","recreate")
fout.cd()
for h in range(my_npoints):
    h_x_xp[h].SetMarkerStyle(20)
    h_x_xp[h].Write()
    hproj = h_x_xp[h].ProjectionX()
    rms = hproj.GetRMS()
    hproj.Write()
    c = TCanvas("c_%i"%h,"X Projection")
    c.cd()
    hproj.Draw()
    #rs.myText(0.6,0.9,1,"s=%2.1f" %sval[i])
    #rs.myText(0.6,0.8,1,"RMS=2.2f" %rms)
    c.Write()
fout.Close()
