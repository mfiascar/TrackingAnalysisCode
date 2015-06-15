################################3
#
#  First need root file for inputs - note that the .dat file is in the HaloDist/plots directory: 
# tree = TTree("tree","tree")
# tree.ReadFile("twiss_fcc_b1_study_disp.dat","KEYWORD/C:NAME:S/F:L:X:Y:BETX:BETY:ALFX:ALFY:MUX:MUY:DX:DY:DPX:DPY:PX:PY")
# tree.Draw("DX:S")
# g = Graph.Clone("graph_dispx")
# fout = TFile("single_pass_dispersion.root","recreate")
# fout.cd()
# g.Write()
# fout.Close()
################################3
inputDir = "/home/mfiascar/Physics/Accelerator/Simulation/FCC/TOY_V1/HaloDist/plots/"
f = TFile.Open(inputDir+"single_pass_dispersion.root")
g_dx = f.Get("graph_dispx")
g_betx = f.Get("graph_betx")
f.Close()

# the graphs above have s=0 at TCP.D6L2.B1
# to make the plots consistent, shift everything again 
# v1_TOY: TCP.D6L2.B1 s = 48023.132350, ring = 101898.219200
# v10: TCP.D6L2.B1 s = 23303.75057, ring = 
s_TCP = 23303.75057
ring = 97314.56227

g_dx_new = TGraph()
g_dx_new.SetName("graph_dispx_rights")
g_betx_new = TGraph()
g_betx_new.SetName("graph_betx_rights")
s = Double()
dx = Double()
bx = Double()
#first find starting point
start_n = -1
for n in range(g_dx.GetN()):
    g_dx.GetPoint(n,s,dx)
    s_new = s + s_TCP
    if s_new >= ring:
        start_n = n
        break
print start_n

for n in range(g_dx.GetN()):
    g_dx.GetPoint(n,s,dx)
    s_new = s + s_TCP
    if s_new > ring:
        s_new = s_new - ring
    n_new = n + (g_dx.GetN() - start_n) 
    if n >= start_n:
        n_new = n - start_n
    g_dx_new.SetPoint(n_new,s_new,dx)
    g_betx.GetPoint(n,s,bx)
    g_betx_new.SetPoint(n_new,s_new,bx)

fout = TFile(inputDir+"single_pass_dispersion.root","update")
fout.cd()
g_dx_new.Write()
g_betx_new.Write()
fout.Close()

#####################################################################

f = TFile.Open(inputDir+"single_pass_dispersion.root")
g_dx = f.Get("graph_dispx_rights")
f.Close()
fb = TFile.Open(inputDir+"BetaFunctions.root")
g_beta = fb.Get("Betax")
g_c_beta = fb.Get("Coll_betax")
fb.Close()
smin = 23000. #47000.
smax = 26500. #52000.
c = TCanvas("c","c")
g_beta.GetXaxis().SetRangeUser(smin,smax)
g_beta.GetYaxis().SetRangeUser(0.,2000.)
g_beta.GetXaxis().CenterTitle()
g_beta.GetXaxis().SetTitle("s[m]")
g_beta.GetXaxis().SetTitleOffset(1.2)
g_beta.GetYaxis().CenterTitle()
g_beta.GetYaxis().SetTitle("Beta Function[m]")
g_beta.GetYaxis().SetTitleOffset(1.3)
g_beta.Draw("AL")
g_c_beta.Draw("P")

#for HL-LHC
#rightmax = 3 
#rightmin = -0.5
rightmax = 3.5  
rightmin = -0.5
s = Double()
dx = Double()
#for n in range(g_dx.GetN()):
#    g_dx.GetPoint(n,s,dx)
#    if s < smin or s> smax:
#        continue
#    if dx > rightmax:
#        rightmax = dx
#print "Found max dispersion: ", rightmax

scale = gPad.GetUymax()/(rightmax-rightmin)

g_dx_scale = g_dx.Clone("g_dx_scale")
for n in range(g_dx.GetN()):
    g_dx.GetPoint(n,s,dx)
    if s < smin or s> smax:
        continue
    g_dx_scale.SetPoint(n,s,(dx-rightmin)*scale)
g_dx_scale.SetLineColor(kRed)
g_dx_scale.Draw("L")

axis = TGaxis(gPad.GetUxmax(),gPad.GetUymin(),gPad.GetUxmax(),gPad.GetUymax(),rightmin,rightmax,510,"+L")
xmin = gPad.GetUxmin()
xmax = gPad.GetUxmax()
axis.SetLineColor(kRed)
axis.SetLabelColor(kRed)
axis.SetTitle("disp x [m]")
axis.CenterTitle()
axis.SetTitleColor(kRed)
axis.Draw()

fL = TFile.Open(inputDir+"Layout.root")
hd = fL.Get("h_dipole_position")
hq = fL.Get("h_quadrupole_position")
hc = fL.Get("h_coll_position")
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
hq.GetXaxis().SetRangeUser(xmin,xmax)
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

import RootStyles
rs = RootStyles.RootStyles()

rs.myMarkerLine(x=0.8,y=0.70,text="collimator",lineH=0.02,lineColor=12,fsize=0.3,dist=0.03)
rs.myMarkerLine(x=0.8,y=0.40,text="dipole",lineH=0.02,lineColor=38,fsize=0.3,dist=0.03)
rs.myMarkerLine(x=0.8,y=0.10,text="quadrupole",lineH=0.02,lineColor=41,fsize=0.3,dist=0.03)




            
