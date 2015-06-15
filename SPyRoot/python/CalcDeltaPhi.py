# ------------------------------------------------------------- #
# package: SPyRoot                                              #
# file: CalcDeltaPhi                                           #
# classes: CalcDeltaPhi                                        #
#                                                               #
# authors: Till Eifert <Till.Eifert@cern.ch> - U. of Geneva     #
#                                                               #
# File and Version Information:                                 #
# $Id: CalcDeltaPhi.py,v 1.5 2009/03/18 16:39:33 mfiascar Exp $
# ------------------------------------------------------------- #


from TTreeAlgorithm import *
from ROOT import *

class CalcDeltaPhi(TTreeAlgorithm):
    def __init__(self,name, o1_x = "T.myJet_px[0]", o2_x = "T.myJet_px[1]",
                 o1_y = "T.myJet_py[0]", o2_y = "T.myJet_py[1]", outName="DeltaPhi_jet1_jet2", Branches=['myJet_px','myJet_py']):

        # remember output var name:
        self.outName = outName

        # construct all 6 input variable strings:
        self.o1_x = o1_x
        self.o1_y = o1_y

        self.o2_x = o2_x
        self.o2_y = o2_y

        # activate the needed branches:
        TTreeAlgorithm.__init__(self,name, Branches)


    def execute(self,T,AllEntriesData,GlobalData,ThisEntryData):
        try:
            phi1 = atan2( eval(self.o1_y), eval(self.o1_x) )
            phi2 = atan2( eval(self.o2_y), eval(self.o2_x) )
        except NameError:
            phi1 = 0.0
            phi2 = 0.0
        except IndexError:
            phi1 = 0.0
            phi2 = 0.0

        delta_phi = fabs( phi1 - phi2 )
        if delta_phi > TMath.Pi():
            delta_phi = 2*TMath.Pi() - delta_phi

        ThisEntryData[self.outName] = delta_phi

        return True

class CalcDeltaPhiLep(TTreeAlgorithm):
    def __init__(self,name, o1_x = "T.myJet_px[0]", o1_y = "T.myJet_py[0]",
                 o2_x = "T.myEl_px[0]", o2_y = "T.myEl_py[0]", o3_x = "T.myMu_px[0]", o3_y = "T.myMu_py[0]",
                 n_el = "T.myEl_N", n_mu = "T.myMu_N",
                 outName="DeltaPhi_jet1_lep",
                 Branches=['myJet_px','myJet_py','myEl_px','myEl_py','myMu_px','myMu_py']):

        # remember output var name:
        self.outName = outName

        # construct all 6 input variable strings:
        self.o1_x = o1_x
        self.o1_y = o1_y

        self.o2_x = o2_x
        self.o2_y = o2_y

        self.o3_x = o3_x
        self.o3_y = o3_y

        self.n_el = n_el
        self.n_mu = n_mu


        # activate the needed branches:
        TTreeAlgorithm.__init__(self,name, Branches)


    def execute(self,T,AllEntriesData,GlobalData,ThisEntryData):

        try:
            if eval(self.n_el) > eval(self.n_mu):
                phi1 = atan2( eval(self.o1_y), eval(self.o1_x) )
                phi2 = atan2( eval(self.o2_y), eval(self.o2_x) )
            else:
                phi1 = atan2( eval(self.o1_y), eval(self.o1_x) )
                phi2 = atan2( eval(self.o3_y), eval(self.o3_x) )
        except IndexError:
            phi1 = 0.0
            phi2 = 0.0
            #print "IndexError!  This shouldn't happen anymore!!!"
        except NameError:
            phi1 = 0.0
            phi2 = 0.0
            #print "NameError!  This shouldn't happen anymore!!!"


        delta_phi = fabs( phi1 - phi2 )
        if delta_phi > TMath.Pi():
            delta_phi = 2*TMath.Pi() - delta_phi

        ThisEntryData[self.outName] = delta_phi

        return True


class CalcGeneralDeltaPhi(TTreeAlgorithm):
    def __init__(self,name, cut="1",phi1 = "T.myEg_phi[0]", phi2 = "T.myEg_phi[1]",
                 outName="DeltaPhi_ele_ele", Branches=['myEg_phi']):

        # remember output var name:
        self.outName = outName

        self.cut =  cut
        self.phi1 = phi1
        self.phi2 = phi2

        # activate the needed branches:
        TTreeAlgorithm.__init__(self,name, Branches)


    def execute(self,T,AllEntriesData,GlobalData,ThisEntryData):

        delta_phi = 0.

        if eval(self.cut):

            delta_phi = fabs( eval(self.phi1) - eval(self.phi2) )
            if delta_phi > TMath.Pi():
                delta_phi = 2*TMath.Pi() - delta_phi

        ThisEntryData[self.outName] = delta_phi

        return True


class CalcDeltaPhiInternalVars(TTreeAlgorithm):
    def __init__(self,name, index1, index2,
                 o1_x = "myJet_px", o2_x = "myJet_px",
                 o1_y = "myJet_py", o2_y = "myJet_py", outName="DeltaPhi_jet1_jet2" ):

        # remember output var name:
        self.outName = outName

        self.index1=index1
        self.index2=index2
        
        # construct all 6 input variable strings:
        self.o1_x = o1_x
        self.o1_y = o1_y

        self.o2_x = o2_x
        self.o2_y = o2_y

        # activate the needed branches:
        TTreeAlgorithm.__init__(self,name, [])


    def execute(self,T,AllEntriesData,GlobalData,ThisEntryData):
        try:
            if self.index1>-1:
                o1_y=ThisEntryData[self.o1_y][self.index1] 
                o1_x=ThisEntryData[self.o1_x][self.index1]
            else:
                o1_y=ThisEntryData[self.o1_y]
                o1_x=ThisEntryData[self.o1_x]

            if self.index2>-1:
                o2_y=ThisEntryData[self.o2_y][self.index2]
                o2_x=ThisEntryData[self.o2_x][self.index2]
            else:
                o2_y=ThisEntryData[self.o2_y]
                o2_x=ThisEntryData[self.o2_x]

            phi1 = atan2( o1_y, o1_x )
            phi2 = atan2( o2_y, o2_x )

        except NameError:
            phi1 = 0.0
            phi2 = 0.0
        except IndexError:
            phi1 = 0.0
            phi2 = 0.0

        delta_phi = fabs( phi1 - phi2 )
        if delta_phi > TMath.Pi():
            delta_phi = 2*TMath.Pi() - delta_phi

        ThisEntryData[self.outName] = delta_phi

        return True



class CalcDeltaPhiLepInternalVars(TTreeAlgorithm):
    def __init__(self,name, index1, index2, index3,
                 o1_x = "myJet_px", o1_y = "myJet_py",
                 o2_x = "myEl_px", o2_y = "myEl_py", o3_x = "myMu_px", o3_y = "myMu_py",
                 n_el = "myEl_N", n_mu = "myMu_N",
                 outName="DeltaPhi_jet1_lep"  ):

        # remember output var name:
        self.outName = outName

        self.index1 = index1
        self.index2 = index2
        self.index3 = index3
        
        # construct all 6 input variable strings:
        self.o1_x = o1_x # anything
        self.o1_y = o1_y # anything

        self.o2_x = o2_x # el
        self.o2_y = o2_y # el

        self.o3_x = o3_x # mu
        self.o3_y = o3_y # mu

        self.n_el = n_el
        self.n_mu = n_mu

        # activate the needed branches:
        TTreeAlgorithm.__init__(self,name, [])


    def execute(self,T,AllEntriesData,GlobalData,ThisEntryData):

        try:

            if self.index1>-1:
                o1_y=ThisEntryData[self.o1_y][self.index1]
                o1_x=ThisEntryData[self.o1_x][self.index1]
            else:
                o1_y=ThisEntryData[self.o1_y]
                o1_x=ThisEntryData[self.o1_x]
                pass
            phi1 = atan2( o1_y, o1_x ) # any obj

            if ThisEntryData[self.n_el] > ThisEntryData[self.n_mu]:
                # go for electron
                if self.index2>-1:
                    o2_y=ThisEntryData[self.o2_y][self.index2]
                    o2_x=ThisEntryData[self.o2_x][self.index2]
                else:
                    o2_y=ThisEntryData[self.o2_y]
                    o2_x=ThisEntryData[self.o2_x]
                    pass
                phi2 = atan2( o2_y, o2_x ) # el
            else:
                # try with muon
                if self.index3>-1:
                    o3_y=ThisEntryData[self.o3_y][self.index3]
                    o3_x=ThisEntryData[self.o3_x][self.index3]
                else:
                    o3_y=ThisEntryData[self.o3_y]
                    o3_x=ThisEntryData[self.o3_x]
                    pass
                phi2 = atan2( o3_y, o3_x ) # mu
                pass
                
            pass
        
        except IndexError:
            phi1 = 0.0
            phi2 = 0.0
            #print "IndexError!  This shouldn't happen anymore!!!"
        except NameError:
            phi1 = 0.0
            phi2 = 0.0
            #print "NameError!  This shouldn't happen anymore!!!"


        delta_phi = fabs( phi1 - phi2 )
        if delta_phi > TMath.Pi():
            delta_phi = 2*TMath.Pi() - delta_phi

        ThisEntryData[self.outName] = delta_phi

        return True

