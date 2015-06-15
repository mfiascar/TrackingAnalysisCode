# Script to compare cleaning ineff. plots with and without DS collimators (for HL-LHC)

try:
    inputDirectory1 
except NameError:
    inputDirectory1 = "/home/mfiascar/Physics/Accelerator/Simulation/HL-LHC/v1.0/VertB1/plots"

try:
    inputDirectory2
except NameError:
    inputDirectory2 = "/home/mfiascar/Physics/Accelerator/Simulation/HL-LHC/v1.0_withDScoll/VertB1/plots"

if inputDirectory1[len(inputDirectory1)-1]!="/":
    inputDirectory1 = inputDirectory1+"/"
if inputDirectory2[len(inputDirectory2)-1]!="/":
    inputDirectory2 = inputDirectory2+"/"

import RootStyles
rs = RootStyles.RootStyles()
rs.setAtlasStyle2()
rs.style.cd()
rs.style.SetPadRightMargin( 0.17 )
rs.style.SetPadTopMargin( 0.07 )
rs.style.SetPaintTextFormat("2.1f")
rs.setPalette()
ROOT.gROOT.ForceStyle()

file1 = TFile.Open(inputDirectory1 + "Efficiency.root")
h_ampl_1 = file1.Get("efficiency_vs_amplitude_rad")
h_dp_1 = file1.Get("efficiency_vs_dpOverp")

file2 = TFile.Open(inputDirectory2 + "Efficiency.root")
h_ampl_2 = file2.Get("efficiency_vs_amplitude_rad")
h_dp_2 = file2.Get("efficiency_vs_dpOverp")

c = TCanvas("Compare_efficiency_vs_amplitude","Compare_efficiency_vs_amplitude")
c.cd()
h_ampl_1.SetMarkerColor(kRed)
h_ampl_1.SetLineColor(kRed)
h_ampl_2.SetMarkerColor(kBlue)
h_ampl_2.SetLineColor(kBlue)
c.SetLogy()
c.SetGridy()
h_ampl_1.GetXaxis().SetTitle("Radial Aperture, A_{0} [#sigma]")
h_ampl_1.GetXaxis().SetRangeUser(6.,15.)
h_ampl_1.GetYaxis().SetTitle("Cleaning inefficiency, #eta (A_{0})")
h_ampl_1.GetYaxis().SetRangeUser(1e-5,1.)
h_ampl_1.Draw()
h_ampl_2.Draw("same")
rs.myMarkerText(0.6,0.85,kRed,20,"without DS coll",0.04)
rs.myMarkerText(0.6,0.78,kBlue,20,"with DS coll",0.04)
c.Write()
c.Print(inputDirectory1+"Compare_Efficiency_vs_amplitude.pdf")
c.Print(inputDirectory1+"Compare_Efficiency_vs_amplitude.png")

c = TCanvas("Compare_efficiency_vs_dpOverp","Compare_efficiency_vs_dpOverp")
c.cd()
h_dp_1.SetMarkerColor(kRed)
h_dp_1.SetLineColor(kRed)
h_dp_2.SetMarkerColor(kBlue)
h_dp_2.SetLineColor(kBlue)
c.SetLogy()
#c.SetGridy()
h_dp_1.GetXaxis().SetTitle("#Deltap/p (%)")
h_dp_1.GetXaxis().SetRangeUser(0.01,1.)
h_dp_1.GetYaxis().SetTitle("Cleaning inefficiency, #eta (#Deltap/p)")
h_dp_1.GetYaxis().SetRangeUser(1e-7,0.1)
h_dp_1.Draw()
h_dp_2.Draw("same")
rs.myMarkerText(0.6,0.85,kRed,20,"without DS coll",0.04)
rs.myMarkerText(0.6,0.78,kBlue,20,"with DS coll",0.04)
c.Write()
c.Print(inputDirectory1+"Compare_Efficiency_vs_dpOverp.pdf")
c.Print(inputDirectory1+"Compare_Efficiency_vs_dpOverp.png")
