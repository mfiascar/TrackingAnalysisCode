import RootStyles
rs = RootStyles.RootStyles()
rs.setAtlasStyle2()
rs.style.cd()
rs.style.SetPadRightMargin( 0.17 )
rs.style.SetPadTopMargin( 0.07 )
rs.style.SetPaintTextFormat("2.1f")
rs.setPalette()
ROOT.gROOT.ForceStyle()


variables = [ ["dx", "h_dispersion_b1_x"],
              ["dy", "h_dispersion_b1_y"],
              ["betax","h_betax"],
              ["betay","h_betay"]
              ]

for vi in variables:

    hname = vi[1]
    v = vi[0]
    print "Looking at variable %s, histo name %s" %(v,hname)
    if v.find("beta")>=0:
        print "Opening root files for beta function"
        f = TFile.Open("/home/mfiascar/Physics/Accelerator/Simulation/HL-LHC/v1.0/HorizB1/plots/BetaFunctions.root")
        fn = TFile.Open("/home/mfiascar/Physics/Accelerator/Simulation/HL-LHC/v1.0/HorizB1_test_thickTothin/plots/BetaFunctions.root")
        fn_withDS = TFile.Open("/home/mfiascar/Physics/Accelerator/Simulation/HL-LHC/v1.0_withDScoll/HorizB1/plots/BetaFunctions.root")
    else:
        print "Opening root files for dispersion"
        f = TFile.Open("/home/mfiascar/Physics/Accelerator/Simulation/HL-LHC/v1.0/HorizB1/plots/Dispersion.root")
        fn = TFile.Open("/home/mfiascar/Physics/Accelerator/Simulation/HL-LHC/v1.0/HorizB1_test_thickTothin/plots/Dispersion.root")
        fn_withDS = TFile.Open("/home/mfiascar/Physics/Accelerator/Simulation/HL-LHC/v1.0_withDScoll/HorizB1/plots/Dispersion.root")

    dx = f.Get("%s" %hname)
    dx_test = fn.Get("%s" %hname)
    dx_withDS = fn_withDS.Get("%s" %hname)

    dx_ratio_thin_vs_thickTothin = dx.Clone("%s_ratio_thin_vs_thickTothin" %v)
    dx_ratio_thin_vs_thickTothin.Divide(dx_test)
    for ib in range(dx_ratio_thin_vs_thickTothin.GetNbinsX()):
        if dx.GetBinContent(ib)==dx_test.GetBinContent(ib) and dx.GetBinContent(ib)==0:
            dx_ratio_thin_vs_thickTothin.SetBinContent(ib,1.)
    c_dx_ratio_thin_vs_thickTothin = TCanvas("%s_ratio_thin_vs_thickTothin" %v)
    c_dx_ratio_thin_vs_thickTothin.cd()
    dx_ratio_thin_vs_thickTothin.Draw()
    if v.find("beta")>=0:
        dx_ratio_thin_vs_thickTothin.GetYaxis().SetRangeUser(0.,1.5)
    else:
        dx_ratio_thin_vs_thickTothin.GetYaxis().SetRangeUser(-5.,5.)
    dx_ratio_thin_vs_thickTothin.GetYaxis().SetTitle("Ratio %s" %v)
    c_dx_ratio_thin_vs_thickTothin.Print("%s_ratio_thin_vs_thickTothin.png" %v)

    dx_diff_thin_vs_thickTothin = dx.Clone("%s_diff_thin_vs_thickTothin" %v)
    dx_diff_thin_vs_thickTothin.Add(dx_test,-1.)
    c_dx_diff_thin_vs_thickTothin = TCanvas("%s_diff_thin_vs_thickTothin" %v)
    c_dx_diff_thin_vs_thickTothin.cd()
    dx_diff_thin_vs_thickTothin.Draw()
    #if v.find("beta")>=0:
    #    dx_diff_thin_vs_thickTothin.GetYaxis().SetRangeUser(0.,1.5)
    #else:
    #    dx_diff_thin_vs_thickTothin.GetYaxis().SetRangeUser(-5.,5.)
    dx_diff_thin_vs_thickTothin.GetYaxis().SetTitle("Diff %s" %v)
    c_dx_diff_thin_vs_thickTothin.Print("%s_diff_thin_vs_thickTothin.png" %v)

#-----------------------------

    dx_ratio_with_vs_withoutDS = dx.Clone("%s_ratio_with_vs_withoutDS" %v)
    dx_ratio_with_vs_withoutDS.Divide(dx_withDS)
    for ib in range(dx.GetNbinsX()):
        if dx.GetBinContent(ib)==dx_withDS.GetBinContent(ib) and dx.GetBinContent(ib)==0:
            dx_ratio_with_vs_withoutDS.SetBinContent(ib,1.)
    c_dx_ratio_with_vs_withoutDS = TCanvas("%s_ratio_with_vs_withoutDS" %v)
    c_dx_ratio_with_vs_withoutDS.cd()
    dx_ratio_with_vs_withoutDS.Draw()
    if v.find("beta")>=0:
        dx_ratio_with_vs_withoutDS.GetYaxis().SetRangeUser(0.,1.5)
    else:
        dx_ratio_with_vs_withoutDS.GetYaxis().SetRangeUser(-5.,5.)
    dx_ratio_with_vs_withoutDS.GetYaxis().SetTitle("Ratio %s" %v)
    c_dx_ratio_with_vs_withoutDS.Print("%s_ratio_with_vs_withoutDS.png" %v)

    dx_diff_with_vs_withoutDS = dx.Clone("%s_diff_with_vs_withoutDS" %v)
    dx_diff_with_vs_withoutDS.Add(dx_withDS,-1.)
    c_dx_diff_with_vs_withoutDS = TCanvas("%s_diff_with_vs_withoutDS" %v)
    c_dx_diff_with_vs_withoutDS.cd()
    dx_diff_with_vs_withoutDS.Draw()
    #if v.find("beta")>=0:
    #    dx_diff_with_vs_withoutDS.GetYaxis().SetRangeUser(0.,1.5)
    #else:
    #    dx_diff_with_vs_withoutDS.GetYaxis().SetRangeUser(-5.,5.)
    dx_diff_with_vs_withoutDS.GetYaxis().SetTitle("Diff %s" %v)
    c_dx_diff_with_vs_withoutDS.Print("%s_diff_with_vs_withoutDS.png" %v)

#-----------------------------

    dx_ratio_test_with_vs_withoutDS = dx_test.Clone("%s_test_ratio_with_vs_withoutDS" %v)
    dx_ratio_test_with_vs_withoutDS.Divide(dx_withDS)
    for ib in range(dx_test.GetNbinsX()):
        if dx_test.GetBinContent(ib)==dx_withDS.GetBinContent(ib) and dx_test.GetBinContent(ib)==0:
            dx_ratio_test_with_vs_withoutDS.SetBinContent(ib,1.)
    c_dx_ratio_test_with_vs_withoutDS = TCanvas("%s_test_ratio_with_vs_withoutDS" %v)
    c_dx_ratio_test_with_vs_withoutDS.cd()
    dx_ratio_test_with_vs_withoutDS.Draw()
    if v.find("beta")>=0:
        dx_ratio_test_with_vs_withoutDS.GetYaxis().SetRangeUser(0.,1.5)
    else:
        dx_ratio_test_with_vs_withoutDS.GetYaxis().SetRangeUser(-5.,5.)
    dx_ratio_test_with_vs_withoutDS.GetYaxis().SetTitle("Ratio %s" %v)
    c_dx_ratio_test_with_vs_withoutDS.Print("%s_test_ratio_with_vs_withoutDS.png" %v)

    dx_diff_test_with_vs_withoutDS = dx_test.Clone("%s_test_diff_with_vs_withoutDS" %v)
    dx_diff_test_with_vs_withoutDS.Add(dx_withDS,-1.)
    c_dx_diff_test_with_vs_withoutDS = TCanvas("%s_test_diff_with_vs_withoutDS" %v)
    c_dx_diff_test_with_vs_withoutDS.cd()
    dx_diff_test_with_vs_withoutDS.Draw()
    #if v.find("beta")>=0:
    #    dx_diff_test_with_vs_withoutDS.GetYaxis().SetRangeUser(0.,1.5)
    #else:
    #    dx_diff_test_with_vs_withoutDS.GetYaxis().SetRangeUser(-5.,5.)
    dx_diff_test_with_vs_withoutDS.GetYaxis().SetTitle("Diff %s" %v)
    c_dx_diff_test_with_vs_withoutDS.Print("%s_test_diff_with_vs_withoutDS.png" %v)



#############################

f = TFile.Open("/home/mfiascar/Physics/Accelerator/Simulation/HL-LHC/v1.0/HorizB1/plots/BetaFunctions.root")
fn = TFile.Open("/home/mfiascar/Physics/Accelerator/Simulation/HL-LHC/v1.0/HorizB1_test_thickTothin/plots/BetaFunctions.root")
fn_withDS = TFile.Open("/home/mfiascar/Physics/Accelerator/Simulation/HL-LHC/v1.0_withDScoll/HorizB1/plots/BetaFunctions.root")

betax = f.Get("Betax")
betax_test = fn.Get("Betax")
betax_withDS = fn_withDS.Get("Betax")

ratio_thin = betax_test.Clone("Ratio_betax_thin_with_over_without_DScoll")
if betax_test.GetN()== betax_withDS.GetN():
    for n in range(ratio_thin.GetN()):
        x = Double(0.)
        y = Double(0.)
        xp = Double(0.)
        yp = Double(0.)
        betax_test.GetPoint(n,x,y)
        betax_withDS.GetPoint(n,xp,yp)
        ratio_thin.SetPoint(n,x/xp,y,yp)
    cr = TCanvas("Ratio")
    cr.cd()
    ratio_thin.Draw("AL")
    cr.Print("Ratio_betax_thin_with_over_without_DScoll.png")
else:
    print "Error: two TGraphs have different number of inputs!!!"
    print betax_test.GetN()
    print betax_withDS.GetN()

c = TCanvas("Compare betax")
c.cd()
betax.SetMarkerColor(kRed)
betax.SetLineColor(kRed)
betax_test.SetMarkerColor(kBlue)
betax_test.SetLineColor(kBlue)
betax.Draw("AL")
betax_test.Draw("L")
betax.Draw("L")
c.Print("Compare_betax_thin_vs_thickTothin.png")

cc = TCanvas("Compare betax coll")
cc.cd()
betax_withDS.SetMarkerColor(kGreen)
betax_withDS.SetLineColor(kGreen)
betax.Draw("AL")
betax_withDS.Draw("L")
betax.Draw("L")
cc.Print("Compare_betax_with_vs_without_DS.png")
