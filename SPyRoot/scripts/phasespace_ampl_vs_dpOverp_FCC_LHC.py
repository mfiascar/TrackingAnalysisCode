###############################################################################
# Make a plot of the phase-space defined by TCP in betatron cleaning AND TCTs
# for the FCC and the LHC
###############################################################################

try:
    doFCC
except NameError:
    doFCC = True


##### HL-LHC values
#
#IR7:tcp.c6l7.b1
#s=0.1979118E+05   
#betax = 0.1501481636E+03
#half-gap: 0.1648329434E-02 
#sigmax = 0.27472E-03
#dispx = 0.5041865E+00
#sigma = 6
#
#TCT: tcth.4l1.b1
#s = 0.2652536320003E+05
#betax = 0.4847006193E+04
#half-gap:0.1295530466E-01
#dispx = 0.3789810E+00
#sigma = 8.3

##### FCC Values:
#
# IR2: tcp.c6l2.b1
#s=0.4803313E+05
#betax = 0.7459028536E+03
#sigma = 0.75700E+01
#half-gap: 0.1328401903E-02
#sigmax =  0.17548E-03
#dispx = 0.5691877E-01
#
#
#TCT: tcth.4l3.b1
#s = 0.7432960E+05
#betax = 0.1187194276E+05
#half-gap: 0.7329933828E-02
#sigmax = 0.70009E-03
#dispx = 0.4955323E-01
#sigma = 0.10470E+02

emittance = 0.413E-10
betax_tct = 0.1187194276E+05
dispx_tct=0.4955323E-01
coll_tct=10.47
betax_ir7 =0.7459028536E+03
dispx_ir7 =0.5691877E-01
coll_ir7=7.57
xrange = 2.e-1

if not doFCC:
    emittance = 0.503E-09 
    betax_tct = 0.4847006193E+04
    dispx_tct= 0.3789810E+00
    coll_tct= 8.3
    betax_ir7 =  0.1501481636E+03
    dispx_ir7 =  0.5041865E+00
    coll_ir7= 6
    xrange = 0.05

plus_tct = TF1("fn_TCT_plus","[0]-x*[1]/sqrt([2]*[3])",-1*xrange,xrange)
plus_tct.SetParameters(coll_tct,dispx_tct,emittance,betax_tct)
minus_tct = TF1("fn_TCT_minus","[0]-x*[1]/sqrt([2]*[3])",-1*xrange,xrange)
minus_tct.SetParameters(-1.*coll_tct,dispx_tct,emittance,betax_tct)
plus_tct_i = TF1("fn_TCT_plus_i","[0]+x*[1]/sqrt([2]*[3])",-1*xrange,xrange)
plus_tct_i.SetParameters(coll_tct,dispx_tct,emittance,betax_tct)
minus_tct_i = TF1("fn_TCT_minus_i","[0]+x*[1]/sqrt([2]*[3])",-1*xrange,xrange)
minus_tct_i.SetParameters(-1.*coll_tct,dispx_tct,emittance,betax_tct)

plus_ir7 = TF1("fn_IR7_plus","[0]-x*[1]/sqrt([2]*[3])",-1*xrange,xrange)
plus_ir7.SetParameters(coll_ir7,dispx_ir7,emittance,betax_ir7)
minus_ir7 = TF1("fn_IR7_minus","[0]-x*[1]/sqrt([2]*[3])",-1*xrange,xrange)
minus_ir7.SetParameters(-1.*coll_ir7,dispx_ir7,emittance,betax_ir7)
plus_ir7_i = TF1("fn_IR7_plus","[0]+x*[1]/sqrt([2]*[3])",-1*xrange,xrange)
plus_ir7_i.SetParameters(coll_ir7,dispx_ir7,emittance,betax_ir7)
minus_ir7_i = TF1("fn_IR7_minus","[0]+x*[1]/sqrt([2]*[3])",-1*xrange,xrange)
minus_ir7_i.SetParameters(-1.*coll_ir7,dispx_ir7,emittance,betax_ir7)

import RootStyles
rs = RootStyles.RootStyles()
rs.setAtlasStyle2()
rs.style.cd()
rs.style.SetPadRightMargin( 0.17 )
rs.style.SetPadTopMargin( 0.07 )
rs.style.SetPaintTextFormat("2.1f")
ROOT.gROOT.ForceStyle()

if doFCC:
    mytitle = "Ampl_vs_dpOverp_FCC"
    yrange = 15.
    tct_name = "TCT"
    ir7_name = "TCP"
else:
    mytitle = "Ampl_vs_dpOverp_HLLHC"
    yrange = 12.
    tct_name = "TCT"
    ir7_name = "TCP"
c = TCanvas(mytitle,mytitle)
c.cd()
plus_tct.GetYaxis().SetRangeUser(-1*yrange,yrange)
plus_tct.Draw()
plus_tct.SetLineColor(kRed)
minus_tct.Draw("same")
minus_tct.SetLineColor(kRed)
plus_tct.GetXaxis().SetTitle("#Deltap/p")
plus_tct.GetYaxis().SetTitle("betatron cut [#sigma]")
minus_tct_i.SetLineColor(kRed)
minus_tct_i.Draw("same")
plus_tct_i.SetLineColor(kRed)
plus_tct_i.Draw("same")
plus_ir7.SetLineColor(kBlue)
plus_ir7_i.SetLineColor(kBlue)
minus_ir7.SetLineColor(kBlue)
minus_ir7_i.SetLineColor(kBlue)
plus_ir7.Draw("same")
plus_ir7_i.Draw("same")
minus_ir7.Draw("same")
minus_ir7_i.Draw("same")

line = TLine(0,-1*yrange,0,yrange)
line.SetLineStyle(2)
line.SetLineColor(1)
line.SetLineWidth(1)
line.Draw("same")
lineplus = TLine(-1*xrange,coll_tct,xrange,coll_tct)
lineplus.SetLineStyle(2)
lineplus.SetLineColor(1)
lineplus.SetLineWidth(1)
lineplus.Draw("same")
lineminus = TLine(-1*xrange,-1.*coll_tct,xrange,-1.*coll_tct)
lineminus.SetLineStyle(2)
lineminus.SetLineColor(1)
lineminus.SetLineWidth(1)
lineminus.Draw("same")
rs.myText(0.85,0.9,kBlue,ir7_name)
rs.myText(0.85,0.85,kRed,tct_name)
c.Print(mytitle+".png")

