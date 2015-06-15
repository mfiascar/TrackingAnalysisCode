#############################################
#
# Spyroot script to make loss map plot
#
#############################################

try:
    inputDir
except NameError:
    inputDir = "/home/mfiascar/Physics/Accelerator/Simulation/Outputs"

if inputDir[len(inputDir)-1]!="/":
    inputDir = inputDir+"/"

try:
    inputDirLayout
except NameError:
    inputDirLayout = inputDir

if inputDirLayout[len(inputDirLayout)-1]!="/":
    inputDirLayout = inputDirLayout+"/"

try:
    binning
except NameError:
    binning = 0.1

    
beam=1
if (inputDir.find("B2")>=0 or inputDir.find("b2")>=0):
    beam=2

setup="horiz"
if (inputDir.find("Vert")>=0 or inputDir.find("vert")>=0):
    setup="vert"

print "Running plot making for input ", inputDir, " with bin size ", binning

import RootStyles
rs = RootStyles.RootStyles()
rs.setAtlasStyle2()
rs.style.cd()
rs.style.SetPadRightMargin( 0.17 )
rs.style.SetPadTopMargin( 0.07 )
rs.style.SetPaintTextFormat("2.1f")
ROOT.gROOT.ForceStyle()

#Get histograms and normalize them
f = TFile.Open(inputDir + "StandardSetup_losses_bin%1.1f.root" %binning)

hcollim = f.Get("h_collimator_losses")
hcollim.SetTitle("Loss Map - %s B%i" %(setup,beam) )
hcold = f.Get("h_cold_losses")
hwarm = f.Get("h_warm_losses")

hcollim_norm = f.Get("h_collimator_losses_norm")
h_allLHC_losses_norm = f.Get("h_allLHC_losses_norm")

nabs = hcollim_norm.Integral() + h_allLHC_losses_norm.Integral()
print "N particles absorbed: ", hcollim_norm.Integral(), " + ", h_allLHC_losses_norm.Integral(), " = ", nabs
hcollim.Scale(1./nabs)
hcold.Scale(1./nabs)
hwarm.Scale(1./nabs)

fL = TFile.Open(inputDirLayout+"Layout.root")
hd = fL.Get("h_dipole_position")
hq = fL.Get("h_quadrupole_position")
hc = fL.Get("h_coll_position")

outfile = TFile(inputDir+"Plots_Losses_bin%1.1f.root" %binning,"recreate")

#plot for the whole ring
c = TCanvas("losses","losses")
c.cd()
c.SetLogy()
c.SetGridy()
hcollim.SetLineColor(kBlack)
hcollim.SetLineWidth(1)
hcollim.GetXaxis().SetTitle("s(m)")
hcollim.GetXaxis().CenterTitle()
hcollim.GetYaxis().SetTitle("Losses (particles/m)")
hcollim.GetXaxis().SetRangeUser(hcollim.GetBinLowEdge(1),hcollim.GetBinLowEdge(hcollim.GetNbinsX())+hcollim.GetBinWidth(hcollim.GetNbinsX()))
hcollim.GetYaxis().SetRangeUser(1e-7,5)
hcollim.GetYaxis().CenterTitle()
hcollim.Draw()
hcold.SetLineColor(kBlue)
hcold.SetLineWidth(1)
hcold.Draw("same")
hwarm.SetLineColor(kRed)
hwarm.SetLineWidth(1)
hwarm.Draw("same")
hcollim.Draw("same")
rs.myMarkerLine(0.3,0.82,"collimators",0.05,1,0.04)
rs.myMarkerLine(0.3,0.77,"cold losses",0.05,kBlue,0.04)
rs.myMarkerLine(0.3,0.72,"warm losses",0.05,kRed,0.04)
outfile.cd()
c.Print(inputDir+"losses.png")
c.Print(inputDir+"losses.pdf")
c.Write()

#plot for IR7
cIR7 = TCanvas("lossesIR7","c")
cIR7.cd()
cIR7.SetLogy()
cIR7.SetGridy()
hcollim.SetLineColor(kBlack)
hcollim.GetXaxis().SetTitle("s(m)")
if beam==1:
    hcollim.GetXaxis().SetRangeUser(19700., 20700.)
if beam==2:
    hcollim.GetXaxis().SetRangeUser(6400., 7500.)
hcollim.GetYaxis().SetTitle("Losses (particles/m)")
hcollim.GetYaxis().SetRangeUser(1e-7,10)
hcollim.Draw()
hcold.SetLineColor(kBlue)
hcold.Draw("same")
hwarm.SetLineColor(kRed)
hwarm.Draw("same")
#hcollim.Draw("same")
rs.myMarkerLine(0.56,0.82,"collimator losses",0.05,1,0.04)
rs.myMarkerLine(0.56,0.77,"cold losses",0.05,kBlue,0.04)
rs.myMarkerLine(0.56,0.72,"warm losses",0.05,kRed,0.04)


hd.SetLineColorAlpha(38,1.)
hd.SetLineWidth(1)
hd.SetMarkerColor(10)
hd.SetFillColor(38)
hq.SetLineColor(41)
hq.SetLineWidth(1)
hq.SetLineColorAlpha(41,1.0)
#hq.SetMarkerColor(5)
hq.SetFillColor(41)
hc.SetLineColorAlpha(12,1.)
hc.SetLineWidth(1)
hc.SetMarkerColor(12)
hc.SetFillColor(12)
hq.Scale(2.)
hc.Scale(2.)


pad = TPad("layout","layout",0.0,0.90,1.,1.,-1,0)
pad.SetBottomMargin(0)
pad.Draw()
pad.cd()
rs.style.SetDrawBorder(0)
myaxis = TGaxis()
myaxis.SetMaxDigits(4)
if beam==1:
    hq.GetXaxis().SetRangeUser(19700.,20700.)
if beam==2:
    hq.GetXaxis().SetRangeUser(6400., 7500.)
#hd.GetXaxis().SetAxisColor(10)
#hd.GetXaxis().SetLabelColor(10)
hq.GetXaxis().SetTitle("")
#hd.GetYaxis().SetAxisColor(10)
#hd.GetYaxis().SetLabelColor(10)
hq.GetYaxis().SetTitle("")
hq.GetXaxis().SetTickLength(0)
hq.GetYaxis().SetTickLength(0)
hq.GetXaxis().SetLabelOffset(999)
hq.GetYaxis().SetLabelOffset(999)
hq.GetXaxis().SetAxisColor(kWhite)
hq.GetYaxis().SetAxisColor(kWhite)
a = hd.GetXaxis()
line = TLine(a.GetXmin(),0.,a.GetXmax(),0.)
line.SetLineColor(kWhite)
line.SetLineWidth(2)
hq.Draw("H9")
hd.Draw("same")
hc.Draw("same")
line.Draw("same")

rs.myMarkerLine(x=0.88,y=0.70,text="collimator",lineH=0.02,lineColor=12,fsize=0.3,dist=0.03)
rs.myMarkerLine(x=0.88,y=0.40,text="dipole",lineH=0.02,lineColor=38,fsize=0.3,dist=0.03)
rs.myMarkerLine(x=0.88,y=0.10,text="quadrupole",lineH=0.02,lineColor=41,fsize=0.3,dist=0.03)

outfile.cd()
cIR7.Print(inputDir+"lossesIR7.png")
cIR7.Print(inputDir+"lossesIR7.pdf")
cIR7.Write()
outfile.Close()
