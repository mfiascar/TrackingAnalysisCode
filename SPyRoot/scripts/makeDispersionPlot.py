########################################################
#
# Make plot for dispersion x,y as a func. of s
#
# input files: amplitude.dat
########################################################

try:
    inputDir
except NameError:
    inputDir = "/home/mfiascar/Physics/Accelerator/Simulation/7TeVStandard_commonfiles"

if inputDir[len(inputDir)-1]!="/":
    inputDir = inputDir+"/"

try:
    beam
except NameError:
    beam=1

import RootStyles
rs = RootStyles.RootStyles()
rs.setAtlasStyle2()
rs.style.cd()
rs.style.SetPadRightMargin( 0.17 )
rs.style.SetPadTopMargin( 0.07 )
rs.style.SetPaintTextFormat("2.1f")
ROOT.gROOT.ForceStyle()

LHCring = 26659.
deltaS = 0.1

h_disp_x = TH1F("h_dispersion_b%i_x" %beam,"h_dispersion_b%i_x"%beam,int(LHCring/deltaS),0.,LHCring)
h_disp_y = TH1F("h_dispersion_b%i_y" %beam,"h_dispersion_b%i_y"%beam,int(LHCring/deltaS),0.,LHCring)

# From CollPositions files get location of collimators
inputfile = inputDir + "amplitude.b%i.dat" %beam
f = open(inputfile)
lines = f.readlines()
f.close()
for l in lines:
    if l.find("ielem")>=0:
        continue
    parts = l.split()
    if len(parts) < 15:
        continue
    if float(parts[2])==0.0:
        continue
    
    #print "Checking element %s at position %2.1f" %(parts[1],float(parts[2]))
    ibin = h_disp_x.FindBin(float(parts[2]))
    h_disp_x.SetBinContent(ibin,float(parts[13]))
    h_disp_y.SetBinContent(ibin,float(parts[14]))


h_disp_x.SetLineColor(kRed)
h_disp_x.SetMarkerColor(kRed)
h_disp_x.SetLineStyle(1)
h_disp_x.SetMarkerStyle(20)
h_disp_y.SetLineColor(kBlue)
h_disp_y.SetMarkerColor(kBlue)
h_disp_y.SetLineStyle(1)
h_disp_y.SetMarkerStyle(20)

outfile = TFile.Open(inputDir + "Dispersion.root","recreate")
outfile.cd()
h_disp_x.Write()
h_disp_y.Write()
outfile.Close()

c = TCanvas("Dispersion_B%i"%beam, "Dispersion_B%i"%beam)
c.cd()
h_disp_x.GetXaxis().SetTitle("s(m)")
h_disp_x.GetYaxis().SetTitle("Dispersion")
h_disp_x.Draw("AL")
h_disp_y.Draw("sameL")



