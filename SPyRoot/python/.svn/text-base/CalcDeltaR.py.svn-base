# ------------------------------------------------------------- #
# package: SPyRoot                                              #
# file: CalcTransMass                                           #
# classes: CalcTransMass                                        #
#                                                               #
# authors: Amir Farbin <Amir.Farbin@cern.ch> - CERN             #
#          Till Eifert <Till.Eifert@cern.ch> - U. of Geneva     #
#          Jamie Boyd  <Jamie.Boyd@cern.ch>  - CERN             #
#                                                               #
# File and Version Information:                                 #
# $Id: CalcDeltaR.py,v 1.1 2007/12/11 11:07:25 eifert Exp $
# ------------------------------------------------------------- #


from TTreeAlgorithm import *
from ROOT import *

class CalcTransMass(TTreeAlgorithm):
    def __init__(self,name, TransMassName="TransMass", DeltaR_Jet_met="Delta_R_Jet_MET"):

        self.TransMassName = TransMassName
        self.DeltaR_Jet_met = DeltaR_Jet_met

        Branches=["myEl_N", "myEl_p_T", "myEl_phi","myMu_N", "myMu_p_T", "myMu_phi", "MET_RefFinal_et", "MET_RefFinal_ex", "MET_RefFinal_ey", "myJet_phi"]
        TTreeAlgorithm.__init__(self,name,Branches)


    def execute(self,T,AllEntriesData,GlobalData,ThisEntryData):

        # 1st find the hardest lepton
        elN = T.myEl_N
        muN = T.myMu_N
        # sanity check
        if elN == 0 and muN == 0:
            # nothing we can do w/o a lepton ...
            ThisEntryData[self.TransMassName] = 0.0
            return True

        if elN == 0 and muN > 0:
            isel = False
        if elN > 0 and muN == 0:
            isel = True
        if elN > 0 and muN > 0:
            isel = True
            if T.myEl_p_T[0] < T.myMu_p_T[0]:
                isel = False

        if isel:
            lepPt  = T.myEl_p_T[0]
            lepPhi = T.myEl_phi[0]
        else:
            lepPt  = T.myMu_p_T[0]
            lepPhi = T.myMu_phi[0]

        # NOTE: use atan2 !!!!!!
        mt = sqrt(2.0*lepPt*T.MET_RefFinal_et*(1.0 - cos( lepPhi - atan2(T.MET_RefFinal_ey,T.MET_RefFinal_ex))))

        delta_r = fabs( T.myJet_phi[0] - atan2(T.MET_RefFinal_ey,T.MET_RefFinal_ex))
        if delta_r > TMath.Pi():
            delta_r = 2*TMath.Pi() - delta_r

        ThisEntryData[self.TransMassName] = mt
        ThisEntryData[self.DeltaR_Jet_met] = delta_r

        return True
