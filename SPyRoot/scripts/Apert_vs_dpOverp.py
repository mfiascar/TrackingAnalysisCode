#####
#IR3:TCP.6L3.B1
#s = 0.6487671E+04   
#betax = 0.1315240E+03   
#dispx = 0.2174887E+01   
#sigma = 15
#
#IR7:tcp.c6l7.b1
#s=0.1979118E+05   
#betax = 0.1505287E+03   
#dispx = 0.5497021E+00   
#sigma = 6

emittance = 4.69E-10

betax_ir3 = 0.1315240E+03   
dispx_ir3=0.2174887E+01 
coll_ir3=15

betax_ir7 = 0.1505287E+03 
dispx_ir7 = 0.5497021E+00   
coll_ir7=6

plus_ir3 = TF1("fn_IR3_plus","[0]-x*[1]/sqrt([2]*[3])",-4.e-3,4.e-3)
plus_ir3.SetParameters(coll_ir3,dispx_ir3,emittance,betax_ir3)
minus_ir3 = TF1("fn_IR3_minus","[0]-x*[1]/sqrt([2]*[3])",-4.e-3,4.e-3)
minus_ir3.SetParameters(-1.*coll_ir3,dispx_ir3,emittance,betax_ir3)

plus_ir7 = TF1("fn_IR7_plus","[0]-x*[1]/sqrt([2]*[3])",-4.e-3,4.e-3)
plus_ir7.SetParameters(coll_ir7,dispx_ir7,emittance,betax_ir7)
minus_ir7 = TF1("fn_IR7_minus","[0]-x*[1]/sqrt([2]*[3])",-4.e-3,4.e-3)
minus_ir7.SetParameters(-1.*coll_ir7,dispx_ir7,emittance,betax_ir7)


import RootStyles
rs = RootStyles.RootStyles()
rs.setAtlasStyle2()
rs.style.cd()
rs.style.SetPadRightMargin( 0.17 )
rs.style.SetPadTopMargin( 0.07 )
rs.style.SetPaintTextFormat("2.1f")
ROOT.gROOT.ForceStyle()

c = TCanvas("Ampl_vs_dpOverp_ip3","Ampl_vs_dpOverp_ip3")
c.cd()
plus_ir3.GetYaxis().SetRangeUser(-55.,55.)
plus_ir3.Draw()
minus_ir3.Draw("same")
plus_ir3.GetXaxis().SetTitle("#Deltap/p")
plus_ir3.GetYaxis().SetTitle("betatron cut [#sigma]")
line = TLine(0,-55,0.,55.)
line.SetLineStyle(2)
line.SetLineColor(1)
line.SetLineWidth(1)
line.Draw("same")
lineplus = TLine(-4.e-3,coll_ir3,4.e-3,coll_ir3)
lineplus.SetLineStyle(2)
lineplus.SetLineColor(1)
lineplus.SetLineWidth(1)
lineplus.Draw("same")
lineminus = TLine(-4.e-3,-1.*coll_ir3,4.e-3,-1.*coll_ir3)
lineminus.SetLineStyle(2)
lineminus.SetLineColor(1)
lineminus.SetLineWidth(1)
lineminus.Draw("same")
rs.myText(0.48,0.95,1,"IR3")
c.Print("Ampl_vs_dpOverp_ip3.png")

c7 = TCanvas("Ampl_vs_dpOverp_ip7","Ampl_vs_dpOverp_ip7")
c7.cd()
plus_ir7.GetYaxis().SetRangeUser(-20.,20.)
plus_ir7.Draw()
minus_ir7.Draw("same")
plus_ir7.GetXaxis().SetTitle("#Deltap/p")
plus_ir7.GetYaxis().SetTitle("betatron cut [#sigma]")
line = TLine(0,-20,0.,20.)
line.SetLineStyle(2)
line.SetLineColor(1)
line.SetLineWidth(1)
line.Draw("same")
lineplus = TLine(-4.e-3,coll_ir7,4.e-3,coll_ir7)
lineplus.SetLineStyle(2)
lineplus.SetLineColor(1)
lineplus.SetLineWidth(1)
lineplus.Draw("same")
lineminus = TLine(-4.e-3,-1.*coll_ir7,4.e-3,-1.*coll_ir7)
lineminus.SetLineStyle(2)
lineminus.SetLineColor(1)
lineminus.SetLineWidth(1)
lineminus.Draw("same")
rs.myText(0.48,0.95,1,"IR7")
c7.Print("Ampl_vs_dpOverp_ip7.png")
