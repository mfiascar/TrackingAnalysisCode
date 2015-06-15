################################################################################3
#
# Script to make a plot of the # of absorbed particles in TCPs / TCSs 
# as a function of the TCP-TCSGs retraction
###########################################################################

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

suffix = "_Horiz"
if dirs[0][1].find("Vert")>=0:
    suffix = "_Vert"

g_nabs_tcp = TGraph()
g_nabs_tcp.SetName("npart_abs_tcp")
GraphProperties(g_nabs_tcp , "TCSG [#sigma]", "nabs_{TCP} / nabs_{TOT}", kRed, 1, kRed, 20)
g_nabs_tcsg = TGraph()
g_nabs_tcsg.SetName("npart_abs_tcp")
GraphProperties(g_nabs_tcsg , "TCSG [#sigma]", "nabs_{TCSG} / nabs_{TOT}", kBlue, 1, kBlue, 21)

for d in dirs:
    print "looking at ",d[1]
    if d[0]+7.6 > 14: 
        continue
    f = TFile.Open(inputDirectory+d[1]+"/plots/NpartColl.root")
    h_nabs = f.Get("nabs_collimators")
    ntot = h_nabs.Integral()
    x = h_nabs.GetXaxis()
    ntcp = 0.
    ntcsg = 0.
    for i in range(h_nabs.GetNbinsX()):
        if x.GetBinLabel(i).find("TCP")>=0 and x.GetBinLabel(i).find("2.B1")>=0:
            ntcp += h_nabs.GetBinContent(i)
        if x.GetBinLabel(i).find("TCSG")>=0 and x.GetBinLabel(i).find("2.B1")>=0:
            ntcsg += h_nabs.GetBinContent(i)
    g_nabs_tcp.SetPoint(g_nabs_tcp.GetN(),d[0]+7.6,ntcp/ntot)
    g_nabs_tcsg.SetPoint(g_nabs_tcsg.GetN(),d[0]+7.6,ntcsg/ntot)
     
g_nabs_tcp.GetXaxis().SetTitle("TCSG [#sigma]")
g_nabs_tcp.GetYaxis().SetTitle("nabs_{TCP} / nabs_{TOT}")
g_nabs_tcsg.GetXaxis().SetTitle("TCSG [#sigma]")
g_nabs_tcsg.GetYaxis().SetTitle("nabs_{TCSG} / nabs_{TOT}")

c_tcp = TCanvas("nabs_tcp","nabs_tcp")
c_tcp.cd()
g_nabs_tcp.Draw("ALP")
g_nabs_tcp.GetYaxis().SetRangeUser(0.7,0.98)
c_tcp.Print("/home/mfiascar/Physics/Accelerator/Simulation/FCC/TOY_V1/HaloDist_scan/plots"+suffix+"/nabs_tcp.png")

c_tcsg = TCanvas("nabs_tcsg","nabs_tcsg")
c_tcsg.cd()
g_nabs_tcsg.GetYaxis().SetRangeUser(0.,0.3)
g_nabs_tcsg.Draw("ALP")
c_tcsg.Print("/home/mfiascar/Physics/Accelerator/Simulation/FCC/TOY_V1/HaloDist_scan/plots"+suffix+"/nabs_tcsg.png")

c_tcp_tcsg = TCanvas("nabs_tcp_tcsg","nabs_tcp_tcsg")
c_tcp_tcsg.cd()
g_nabs_tcp.GetYaxis().SetRangeUser(0.,1.)
g_nabs_tcp.Draw("ALP")
g_nabs_tcsg.Draw("LP")
rs.myMarkerText(0.65,0.77,kRed, 20, "TCPs")
rs.myMarkerText(0.65,0.7,kBlue, 21, "TCSGs")
c_tcp_tcsg.Print("/home/mfiascar/Physics/Accelerator/Simulation/FCC/TOY_V1/HaloDist_scan/plots"+suffix+"/nabs_tcp_tcsg.png")
