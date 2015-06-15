from simulation import *

def ScalePlot(h):
    h.Scale(1./h.Integral())

#inputDir = "/home/mfiascar/Physics/Accelerator/Simulation/FCC/TOY_V1/HaloDist"
inputDir = "/home/mfiascar/Physics/Accelerator/Simulation/HL-LHC/v1.0/HorizB1_onlyIR7_thicktothin"
sim = simulation(inputDir)

infile = TFile.Open(sim.Directory + "FirstImpacts.root")
t = infile.Get("ntuple")

h_fi_int_type = TH1F("h_firstImpact_inter_type","h_firstImpact_inter_type",6,0.,6.)
h_fi_nturn = TH1F("h_firstImpact_nturn","h_firstImpact_nturn",200,0.,200.)
#h_fi_dp = TH1F("h_firstImpact_dp","h_firstImpact_dp",200,0.,200.)
h_fi_dx = TH1F("h_firstImpact_dx","h_firstImpact_dx",200,-1.e-5,1.e-5) #absolute dx 
h_fi_dxp = TH1F("h_firstImpact_dxp","h_firstImpact_dxp",200,-2.e-5,2.e-5) #relative dxp (x=b)
h_fi_dy = TH1F("h_firstImpact_dy","h_firstImpact_dy",200,-1.e-5,1.e-5) #absolute dy
h_fi_dyp = TH1F("h_firstImpact_dyp","h_firstImpact_dyp",200,-2.e-5,2.e-5) #relative dyp (x=b)
h_fi_ds = TH1F("h_firstImpact_ds","h_firstImpact_ds",100,0.,1.) #absolute lenght transversed

h_fi_intType_vs_dx = TH2F("h_firstImpact_intType_vs_dx","h_firstImpact_intType_vs_dx",6,0.,6.,200,-1.e-5,1.e-5) #relative dx (x=b)
h_fi_intType_vs_dxp = TH2F("h_firstImpact_intType_vs_dxp","h_firstImpact_intType_vs_dxp",6,0.,6.,200,-2.e-5,2.e-5) #relative dxp (x=b)
h_fi_intType_vs_dy = TH2F("h_firstImpact_intType_vs_dy","h_firstImpact_intType_vs_dy",6,0.,6.,200,-1.e-5,1.e-5) #relative dx (x=b)
h_fi_intType_vs_dyp = TH2F("h_firstImpact_intType_vs_dyp","h_firstImpact_intType_vs_dyp",6,0.,6.,200,-2.e-5,2.e-5) #relative dxp (x=b)
h_fi_intType_vs_ds = TH2F("h_firstImpact_intType_vs_ds","h_firstImpact_intType_vs_ds",6,0.,6.,100,0.,1.) #absolute lenght transversed

h_fi_ds_vs_xin = TH2F("h_firstImpact_ds_vs_xin","h_fi_ds_vs_xin",200,0.,2.e-6,100,0.,1.)
h_fi_ds_vs_dx = TH2F("h_firstImpact_ds_vs_dx","h_fi_ds_vs_dx",200,-1.e-5,1.e-5,100,0.,1.)

nmax = 1000000  #t.GetEntries()

for i in range(nmax):
    t.GetEntry(i)
    icoll = int(t.icoll)-1
    
    if not "TCP" in sim.collimator_name[ icoll ] :
        print "First interaction is not with a primary!"
        continue

    h_fi_int_type.Fill(t.nabs)
    h_fi_nturn.Fill(t.iturn)

    if "TCP.C" in sim.collimator_name[ icoll ] :
        h_fi_dx.Fill((t.x_out - t.x_in))
        h_fi_dy.Fill((t.y_out - t.y_in))
        h_fi_dxp.Fill((t.xp_out - t.xp_in))
        h_fi_dyp.Fill((t.yp_out - t.yp_in))
        h_fi_ds.Fill(t.s_out - t.s_imp)
        h_fi_intType_vs_ds.Fill(t.nabs,t.s_out - t.s_imp)
        h_fi_intType_vs_dx.Fill(t.nabs,t.x_out - t.x_in)
        h_fi_intType_vs_dxp.Fill(t.nabs,t.xp_out - t.xp_in)
        h_fi_intType_vs_dy.Fill(t.nabs,t.y_out - t.y_in)
        h_fi_intType_vs_dyp.Fill(t.nabs,t.yp_out - t.yp_in)
        h_fi_ds_vs_xin.Fill(t.x_in, t.s_out - t.s_imp)
        h_fi_ds_vs_dx.Fill(t.x_out - t.x_in, t.s_out - t.s_imp)

#Normalize plots
#h_fi_int_type.Scale(1./h_fi_int_type.Integral())
#h_fi_nturn.Scale(1./h_fi_nturn.Integral())
ScalePlot(h_fi_int_type)
ScalePlot(h_fi_nturn)
ScalePlot(h_fi_dx)
ScalePlot(h_fi_dxp)
ScalePlot(h_fi_dy)
ScalePlot(h_fi_dyp)
ScalePlot(h_fi_ds)

outfile = TFile(inputDir + "/plots/StudyFirstImpacts.root","recreate")
outfile.cd()
h_fi_int_type.Write()
h_fi_nturn.Write()
h_fi_dx.Write()
h_fi_dxp.Write()
h_fi_dy.Write()
h_fi_dyp.Write()
h_fi_ds.Write()
h_fi_intType_vs_ds.Write()
for i in range(h_fi_intType_vs_ds.GetNbinsX()):
    hs = h_fi_intType_vs_ds.ProjectionY(h_fi_intType_vs_ds.GetName()+"_bin%s"%(i+1),i+1,i+1)
    hs.Write()
    hdx = h_fi_intType_vs_dx.ProjectionY(h_fi_intType_vs_dx.GetName()+"_bin%s"%(i+1),i+1,i+1)
    hdx.Write()
    hx = h_fi_intType_vs_dxp.ProjectionY(h_fi_intType_vs_dxp.GetName()+"_bin%s"%(i+1),i+1,i+1)
    hx.Write()
    hdy = h_fi_intType_vs_dy.ProjectionY(h_fi_intType_vs_dy.GetName()+"_bin%s"%(i+1),i+1,i+1)
    hdy.Write()
    hy = h_fi_intType_vs_dyp.ProjectionY(h_fi_intType_vs_dyp.GetName()+"_bin%s"%(i+1),i+1,i+1)
    hy.Write()
h_fi_ds_vs_xin.Write()    
h_fi_ds_vs_dx.Write()
outfile.Close()

    
