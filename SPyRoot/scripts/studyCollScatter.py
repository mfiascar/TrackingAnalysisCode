from simulation import *

def ScalePlot(h):
    h.Scale(1./h.Integral())

#inputDir = "/home/mfiascar/Physics/Accelerator/Simulation/FCC/TOY_V1/HaloDist"
inputDir = "/home/mfiascar/Physics/Accelerator/Simulation/HL-LHC/v1.0/HorizB1_onlyIR7_thicktothin_noLossMaps/"

sim = simulation(inputDir)

infile = TFile.Open(sim.Directory + "Coll_Scatter.root")
t = infile.Get("ntuple")

nmax = 1000000  #t.GetEntries()

h_intType = TH1F("h_intType","h_intType",6,0.,6.) 
h_fi_intType_vs_dp = TH2F("h_firstImpact_intType_vs_dp","h_firstImpact_intType_vs_dp",6,0.,6.,100,0.,1.01) #relative dx (x=b)
h_fi_intType_vs_dxp = TH2F("h_firstImpact_intType_vs_dxp","h_firstImpact_intType_vs_dxp",6,0.,6.,200,-2.e-5,2.e-5) #relative dxp (x=b)
h_fi_intType_vs_dyp = TH2F("h_firstImpact_intType_vs_dyp","h_firstImpact_intType_vs_dyp",6,0.,6.,200,-2.e-5,2.e-5) #relative dxp (x=b)

h_abs_icoll = TH1F("h_abs_icoll","h_abs_icoll",20,1,21)
h_nTurn_absorption = TH1F("h_nTurn_fromFirstImpact_to_absorption","h_nTurn_fromFirstImpact_to_absorption",200,0,200)
h_nTurn_absorption_icoll = TH2F("h_nTurn_fromFirstImpact_to_absorption_vs_icoll","h_nTurn_fromFirstImpact_to_absorption_vs_icoll",200,0,200,20,1,21)
h_nPassagesTCP_absorbedTCP = TH1F("h_nPassagesTCP_absorbedTCP","h_nPassagesTCP_absorbedTCP",20,0,20)
h_nPassagesTCP_absorbedOther = TH1F("h_nPassagesTCP_absorbedOther","h_nPassagesTCP_absorbedOther",20,0,20)

turnOld = 0
firstImp = {}

for i in range(nmax):

    t.GetEntry(i)
    if t.iturn < turnOld:
        #print "Reset, entry %i, current turn is %i old one %i" %(i, t.iturn, turnOld)
        firstImp = {}
        turnOld = 0

    h_intType.Fill(t.nabs)
    #look at first impacts on TCP.C (horizontal)
    icoll = int(t.icoll)-1
    if t.np not in firstImp:
        if "TCP.C" in sim.collimator_name[ icoll ]:
            firstImp[t.np] = [ icoll, t.iturn, t.nabs, t.iturn, 1]
            h_fi_intType_vs_dp.Fill(t.nabs,fabs(t.dp))
            h_fi_intType_vs_dxp.Fill(t.nabs,t.dxp)
            h_fi_intType_vs_dyp.Fill(t.nabs,t.dyp)
    else:
        if "TCP.C" in sim.collimator_name[ icoll ] and t.iturn != firstImp[t.np][3]:
            firstImp[t.np][3] = t.iturn
            firstImp[t.np][4] = firstImp[t.np][4]+1
    if t.nabs==1:
        h_abs_icoll.Fill(t.icoll)
        if t.np in firstImp:
            h_nTurn_absorption.Fill(t.iturn - firstImp[t.np][1])
            h_nTurn_absorption_icoll.Fill(t.iturn - firstImp[t.np][1],t.icoll)
            if "TCP.C" in sim.collimator_name[ icoll ]:
                h_nPassagesTCP_absorbedTCP.Fill(firstImp[t.np][4])
            else:
                h_nPassagesTCP_absorbedOther.Fill(firstImp[t.np][4])
    turnOld = t.iturn
            
outfile = TFile(inputDir + "/plots/StudyCollScatter.root","recreate")
outfile.cd()
ScalePlot(h_intType)
h_intType.Write()
h_fi_intType_vs_dp.Write()
h_fi_intType_vs_dxp.Write()
h_fi_intType_vs_dyp.Write()
for i in range(h_fi_intType_vs_dp.GetNbinsX()):
    hdp = h_fi_intType_vs_dp.ProjectionY(h_fi_intType_vs_dp.GetName()+"_bin%s"%(i+1),i+1,i+1)
    hdp.Write()
    hdxp = h_fi_intType_vs_dxp.ProjectionY(h_fi_intType_vs_dxp.GetName()+"_bin%s"%(i+1),i+1,i+1)
    hdxp.Write()
    hdyp = h_fi_intType_vs_dyp.ProjectionY(h_fi_intType_vs_dyp.GetName()+"_bin%s"%(i+1),i+1,i+1)
    hdyp.Write()
ScalePlot(h_nTurn_absorption)
h_nTurn_absorption.Write()
h_nTurn_absorption_icoll.Write()
ScalePlot(h_nPassagesTCP_absorbedTCP)
ScalePlot(h_nPassagesTCP_absorbedOther)
h_nPassagesTCP_absorbedTCP.Write()
h_nPassagesTCP_absorbedOther.Write()
ScalePlot(h_abs_icoll)
h_abs_icoll.Write()
outfile.Close()
