#############################################
#
# Spyroot script to make loss map plot
#
#############################################

try:
    inputDir
except NameError:
    inputDir = "/home/mfiascar/Physics/Accelerator/Simulation/7TeVStandard_commonfiles"

if inputDir[len(inputDir)-1]!="/":
    inputDir = inputDir+"/"

try:
    binning
except NameError:
    binning = 0.1

print "Running plot making for input ", inputDir, " with bin size ", binning

import RootStyles
rs = RootStyles.RootStyles()
rs.setAtlasStyle2()
rs.style.cd()
rs.style.SetPadRightMargin( 0.17 )
rs.style.SetPadTopMargin( 0.07 )
rs.style.SetPaintTextFormat("2.1f")
ROOT.gROOT.ForceStyle()

f = TFile.Open(inputDir+"Layout.root")
hd = f.Get("h_dipole_position")
hq = f.Get("h_quadrupole_position")
hc = f.Get("h_coll_position")

hd.SetLineColorAlpha(38,1.)
hd.SetMarkerColor(10)
hd.SetFillColor(38)
hq.SetLineColor(41)
hq.SetLineColorAlpha(41,1.0)
#hq.SetMarkerColor(5)
hq.SetFillColor(41)
hc.SetLineColorAlpha(12,1.)
hc.SetMarkerColor(12)
hc.SetFillColor(12)

hq.Scale(2.)
hc.Scale(2.)

c = TCanvas("c","c")
c.cd()
pad = TPad("layout","layout",0.05,0.80,0.95,0.95)
pad.Draw()
hq.GetXaxis().SetRangeUser(19700., 21500.)
#hd.GetXaxis().SetAxisColor(10)
#hd.GetXaxis().SetLabelColor(10)
hq.GetXaxis().SetTitle("")
#hd.GetYaxis().SetAxisColor(10)
#hd.GetYaxis().SetLabelColor(10)
hq.GetYaxis().SetTitle("")
hq.Draw("AH9")
hd.Draw("same")
hc.Draw("same")





