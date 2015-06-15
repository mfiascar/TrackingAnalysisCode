########################
# Script to analyze the simulation scans:
# TCP - TCSG
# and see how the ineffiency plots are affected
########################
from array import array
from simulation import *

inputDirectory = "/home/mfiascar/Physics/Accelerator/Simulation/FCC/TOY_V1/HaloDist_scan/"

import RootStyles
rs = RootStyles.RootStyles()
rs.setAtlasStyle2()
rs.style.cd()
rs.style.SetPadRightMargin( 0.17 )
rs.style.SetPadTopMargin( 0.07 )
rs.style.SetPaintTextFormat("2.1f")
rs.setPalette()
ROOT.gROOT.ForceStyle()

dirs = [
    [0.1,"Horiz_dPS_0.1"],
    [0.2,"Horiz_dPS_0.2"],
    [0.5,"Horiz_dPS_0.5"],
    [0.75,"Horiz_dPS_0.75"],
    [1.0,"Horiz_dPS_1.0"],
    [1.5,"Horiz_dPS_1.5"],
    [2.5,"Horiz_dPS_2.5"],
    [5.0,"Horiz_dPS_5"],
    [10.0,"Horiz_dPS_10"],
    ]

#dirs = [
#    [0.2,"Vert_dPS_0.2"],
#    [0.5,"Vert_dPS_0.5"],
#    [1.0,"Vert_dPS_1.0"],
#    [2.5,"Vert_dPS_2.5"],
#    [5.0,"Vert_dPS_5"],
#    [10.0,"Vert_dPS_10"],
#   ]

#A(r) values for 1D plot
radSigma = [ 9., 10.,12.,15.]
dpop = [ 0.02, 0.05, 0.2,0.5,0.8]

styles = [
    [2, 20],
    [4, 21],
    [6, 22],
    [8, 23],
    [1, 29]
]

ref_file = TFile.Open(inputDirectory+dirs[0][1]+"/plots/Efficiency.root")
ref_eff_rad = ref_file.Get("efficiency_vs_amplitude_rad")
ref_eff_dpop = ref_file.Get("efficiency_vs_dpOverp")
suffix = "_Horiz"
if dirs[0][1].find("Vert")>=0:
    suffix = "_Vert"

n_x_rad =  ref_eff_rad.GetNbinsX()
bins_x_rad = []
for n in range(n_x_rad):
    bins_x_rad += [ ref_eff_rad.GetBinCenter(n) ]
#print "bins for Radial A:"
#print bins_x_rad
#my_x_rad_bins = array('d',bins_x_rad)

n_x_dpop = ref_eff_dpop.GetNbinsX()
bins_x_dpop = []
for n in range(n_x_dpop):
    bins_x_dpop += [ ref_eff_dpop.GetBinCenter(n) ]
#print "bins for dpop:"
#print bins_x_dpop
#my_x_dpop_bins = array('d',bins_x_dpop)

my_dsigma = []
for d in dirs:
    my_dsigma += [d[0]]
#print "bins for delta Sigma:"
#print my_dsigma
my_dsigma_bins = array('d',my_dsigma)

g_eff_rad = TGraph2D()
g_eff_rad.SetName("2dgraph_eff_rad")

g_eff_dpop = TGraph2D()
g_eff_dpop.SetName("2dgraph_eff_dpop")


g_eff_rad_1d = []
for r in radSigma:
    g_eff_rad_10sigma = TGraph()
    g_eff_rad_10sigma.SetName("graph_eff_rad_%isigma" %r)
    g_eff_rad_1d += [ g_eff_rad_10sigma ]
g_eff_dpop_1d = []
for p in dpop:
    g_eff_dpop_05 = TGraph()
    g_eff_dpop_05.SetName("graph_eff_dpop_%s" %p)
    g_eff_dpop_1d += [ g_eff_dpop_05 ]

c_overlay_eff_rad = TCanvas("Compare_eff_rad","Compare_eff_rad")
c_overlay_eff_rad.SetLogy()
c_overlay_eff_dpop = TCanvas("Compare_eff_dpop","Compare_eff_dpop")
c_overlay_eff_dpop.SetLogy()

#Now fill in tgraphs
dcount = 0 
for d in dirs:
    print "looking at ",d[1]
    f = TFile.Open(inputDirectory+d[1]+"/plots/Efficiency.root")
    eff_rad = f.Get("efficiency_vs_amplitude_rad")
    eff_dpop = f.Get("efficiency_vs_dpOverp")
    if dcount <= len(styles)-1:
        eff_rad.SetLineColor(styles[dcount][0])
        eff_rad.SetMarkerColor(styles[dcount][0])
        eff_rad.SetMarkerStyle(styles[dcount][1])
        eff_dpop.SetLineColor(styles[dcount][0])
        eff_dpop.SetMarkerColor(styles[dcount][0])
        eff_dpop.SetMarkerStyle(styles[dcount][1])
        c_overlay_eff_rad.cd()
        if dcount==0:
            eff_rad.GetXaxis().SetRangeUser(8.,15.)
            eff_rad.GetYaxis().SetRangeUser(1e-4,1.)
            eff_rad.Draw()
        else:
            eff_rad.Draw("same")
        rs.myMarkerText(0.65,0.7+dcount*0.05,styles[dcount][0], styles[dcount][1], "#Delta #sigma=%s" %d[0], 0.04, 1.5)
        c_overlay_eff_dpop.cd()
        if dcount==0:
            eff_dpop.GetXaxis().SetRangeUser(0.01,1.)
            eff_dpop.GetYaxis().SetRangeUser(1e-5,5e-3)
            eff_dpop.Draw()
        else:
            eff_dpop.Draw("same")
        rs.myMarkerText(0.65,0.7+dcount*0.05,styles[dcount][0], styles[dcount][1], "#Delta #sigma=%s" %d[0], 0.04, 1.5)
    dcount +=1 

    for n in range(eff_rad.GetNbinsX()):
        if eff_rad.GetBinCenter(n) < 7.5:
            continue
        g_eff_rad.SetPoint(g_eff_rad.GetN(),eff_rad.GetBinCenter(n),d[0],eff_rad.GetBinContent(n))
        print "Setting 2d_eff_rad: x= %2.1f, y=%f, eff=%f" %(d[0], eff_rad.GetBinCenter(n),eff_rad.GetBinContent(n))
    for n in range(eff_dpop.GetNbinsX()):
        if eff_dpop.GetBinCenter(n) < 0.:
            continue
        g_eff_dpop.SetPoint(g_eff_dpop.GetN(),eff_dpop.GetBinCenter(n),d[0],eff_dpop.GetBinContent(n))
        print "Setting 2d_eff_dpop: x= %2.1f, y=%f, eff=%f" %(d[0], eff_dpop.GetBinCenter(n),eff_dpop.GetBinContent(n))
    rcount=0
    for r in radSigma:
        if 7.6+d[0] > 14:
            rcount +=1
            continue
        bin_10sigma = eff_rad.FindBin(r)
        g_eff_rad_1d[rcount].SetPoint(g_eff_rad_1d[rcount].GetN(),7.6+d[0],eff_rad.GetBinContent(bin_10sigma))
        print "Filling histo ", g_eff_rad_1d[rcount].GetName(), " for bin: ",bin_10sigma
        rcount +=1
    pcount = 0
    for p in dpop:
        bin_05 = eff_dpop.FindBin(p)
        g_eff_dpop_1d[pcount].SetPoint(g_eff_dpop_1d[pcount].GetN(),d[0],eff_dpop.GetBinContent(bin_05))
        print "Filling histo ",g_eff_dpop_1d[pcount].GetName(), " for bin", bin_05
        pcount += 1

#Now write out the graphs
Graph2DProperties( g_eff_rad, "Radial Aperture, A_{0} [#sigma]", "#Delta(TCP-TCSG)", "#eta (A_{0})",kRed, 1, kRed, 20)
g_eff_rad.GetXaxis().SetRangeUser(8.,19.)
g_eff_rad.SetDrawOption("surf1P")
g_eff_dpop.GetXaxis().SetRangeUser(0.01,1.)
g_eff_dpop.SetDrawOption("surf1P")
Graph2DProperties( g_eff_dpop,"#Deltap/p (%)", "#Delta(TCP-TCSG)",  "#eta (#Deltap/p)",kRed, 1, kRed, 20)
fout = TFile("/home/mfiascar/Physics/Accelerator/Simulation/FCC/TOY_V1/HaloDist_scan/plots"+suffix+"/Efficiencies.root","recreate")
fout.cd()
g_eff_rad.Write()
g_eff_dpop.Write()
c_overlay_eff_rad.Write()
c_overlay_eff_dpop.Write()
rcount=0
for r in radSigma:
    GraphProperties( g_eff_rad_1d[rcount], "TCSG [#sigma]", "#eta (A_{0})", styles[rcount][0], 1, styles[rcount][0], styles[rcount][1])
    g_eff_rad_1d[rcount].Write()
    rcount += 1
pcount = 0
for p in dpop:
    GraphProperties( g_eff_dpop_1d[pcount], "#Delta(TCP-TCSG)", "#eta (#Delta p/p)", styles[pcount][0], 1, styles[pcount][0], styles[pcount][1])
    g_eff_dpop_1d[pcount].Write()
    pcount += 1
fout.Close()

c_eff_rad = TCanvas("2d_eff_rad","2d_eff_rad")
c_eff_rad.cd()
c_eff_rad.SetLogz()
g_eff_rad.GetXaxis().SetTitle("Radial Aperture, A_{0} [#sigma]")
g_eff_rad.GetYaxis().SetTitle("TCSG [#sigma]")
g_eff_rad.GetZaxis().SetTitle("#eta (A_{0})")
g_eff_rad.Draw("surf1")
c_eff_rad.Print("/home/mfiascar/Physics/Accelerator/Simulation/FCC/TOY_V1/HaloDist_scan/plots"+suffix+"/2d_eff_rad.png")
c_eff_dpop = TCanvas("2d_eff_dpop","2d_eff_dpop")
c_eff_dpop.cd()
c_eff_dpop.SetLogz()
g_eff_dpop.GetXaxis().SetTitle("#Deltap/p (%)")
g_eff_dpop.GetYaxis().SetTitle("#Delta(TCP-TCSG)")
g_eff_dpop.GetZaxis().SetTitle("#eta (#Deltap/p)")
g_eff_dpop.Draw("surf1")
c_eff_dpop.Print("/home/mfiascar/Physics/Accelerator/Simulation/FCC/TOY_V1/HaloDist_scan/plots"+suffix+"/2d_eff_dpop.png")

c_eff_rad_10sigma = TCanvas("1d_eff_rad","1d_eff_rad")
c_eff_rad_10sigma.cd()
c_eff_rad_10sigma.SetLogy()
g_eff_rad_1d[rcount-1].GetYaxis().SetRangeUser(1e-4,0.1)
#g_eff_rad_1d[rcount-1].GetXaxis().SetRangeUser(7.6,14)
g_eff_rad_1d[rcount-1].Draw("ALP")
rcount=0
for r in radSigma:
    #if rcount==0:
    #    print "rcount==0"
    #    g_eff_rad_1d[rcount].GetYaxis().SetRangeUser(1e-4,0.5)
    #    g_eff_rad_1d[rcount].GetXaxis().SetRangeUser(7.,14.)
    #    g_eff_rad_1d[rcount].Draw("ALP")
    #else:
    g_eff_rad_1d[rcount].Draw("LP")
    rs.myMarkerText(0.65,0.22+rcount*0.05,styles[rcount][0], styles[rcount][1], "A_{0} = %i #sigma" %r, 0.04, 1.5)
    rcount +=1
c_eff_rad_10sigma.Print("/home/mfiascar/Physics/Accelerator/Simulation/FCC/TOY_V1/HaloDist_scan/plots"+suffix+"/1d_eff_rad.png")


c_eff_dpop_05 = TCanvas("1d_eff_dpop_05","1d_eff_dpop_05")
c_eff_dpop_05.cd()
c_eff_dpop_05.SetLogy()
pcount = 0
for p in dpop:
    if pcount==0:
        g_eff_dpop_1d[pcount].Draw("ALP")
        g_eff_dpop_1d[pcount].GetYaxis().SetRangeUser(1e-5,0.04)
        #g_eff_dpop_1d[pcount].GetXaxis().SetRangeUser(0.,4.)
    else:
        g_eff_dpop_1d[pcount].Draw("LP")
    rs.myMarkerText(0.65,0.22+pcount*0.05,styles[pcount][0], styles[pcount][1], "#Deltap/p = %s" %p, 0.04, 1.5)
    pcount +=1
c_eff_dpop_05.Print("/home/mfiascar/Physics/Accelerator/Simulation/FCC/TOY_V1/HaloDist_scan/plots"+suffix+"/1d_eff_dpop.png")



