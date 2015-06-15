# ------------------------------------------------------------- #
# package: SPyRoot                                              #
# file: CalcInvMass                                           #
# classes: CalcInvMass                                        #
#                                                               #
# ------------------------------------------------------------- #


from TTreeAlgorithm import *
from ROOT import *
from ROOT import TLorentzVector, TVector3

class CalcInvMass_pxyz(TTreeAlgorithm):
    def __init__(self,name, px1, py1, pz1, m1, px2, py2, pz2, m2, outputVarName, Branches):

        self.px1 = px1
        self.py1 = py1
        self.pz1 = pz1
        self.m1 = m1
        self.px2 = px2
        self.py2 = py2
        self.pz2 = pz2
        self.m2 = m2
        self.outputVarName = outputVarName
        TTreeAlgorithm.__init__(self,name,Branches)


    def execute(self,T,AllEntriesData,GlobalData,ThisEntryData):

        try:
            momentum1 = TVector3( eval(self.px1), eval(self.py1), eval(self.pz1) )
            momentum2 = TVector3( eval(self.px2), eval(self.py2), eval(self.pz2) )
        except NameError:
            ThisEntryData[self.outputVarName] = -1
            return
        except IndexError:
            ThisEntryData[self.outputVarName] = -1
            return
        
        energy1   = TMath.Sqrt( momentum1.Dot( momentum1 ) + self.m1*self.m1 )
        fourVec1  = TLorentzVector( momentum1, energy1 )
        energy2   = TMath.Sqrt( momentum2.Dot( momentum2 ) + self.m2*self.m2 )
        fourVec2  = TLorentzVector( momentum2, energy2 )

        sumVec = fourVec1 + fourVec2

        ThisEntryData[self.outputVarName] = sumVec.M()

        return True

class CalcInvMass_ptEtaPhi(TTreeAlgorithm):
    def __init__(self,name, pt1, eta1, phi1, m1, pt2, eta2, phi2, m2, outputVarName, Branches):

        self.pt1 = pt1
        self.eta1 = eta1
        self.phi1 = phi1
        self.m1 = m1
        self.pt2 = pt2
        self.eta2 = eta2
        self.phi2 = phi2
        self.m2 = m2
        self.outputVarName = outputVarName
        TTreeAlgorithm.__init__(self,name,Branches)


    def execute(self,T,AllEntriesData,GlobalData,ThisEntryData):

        momentum1 = TVector3( 1, 1, 1)
        momentum2 = TVector3( 1, 1, 1)
        try:
            momentum1.SetPtEtaPhi( eval(self.pt1), eval(self.eta1), eval(self.phi1) )
            momentum2.SetPtEtaPhi( eval(self.pt2), eval(self.eta2), eval(self.phi2) )
        except NameError:
            ThisEntryData[self.outputVarName] = -1
            return
        except IndexError:
            ThisEntryData[self.outputVarName] = -1
            return
        
        energy1   = TMath.Sqrt( momentum1.Dot( momentum1 ) + self.m1*self.m1 )
        fourVec1  = TLorentzVector( momentum1, energy1 )

        energy2   = TMath.Sqrt( momentum2.Dot( momentum2 ) + self.m2*self.m2 )
        fourVec2  = TLorentzVector( momentum2, energy2 )

        sumVec = fourVec1 + fourVec2
        
        ThisEntryData[self.outputVarName] = sumVec.M()

        return True



class CalcInvMassInternalVars_pxyz(TTreeAlgorithm):
    def __init__(self,name, index1, index2,
                 px1, py1, pz1, m1, px2, py2, pz2, m2, outputVarName ):

        self.index1=index1
        self.index2=index2

        self.px1 = px1
        self.py1 = py1
        self.pz1 = pz1

        self.px2 = px2
        self.py2 = py2
        self.pz2 = pz2

        self.m1=m1
        self.m2=m2

        self.outputVarName = outputVarName

        TTreeAlgorithm.__init__(self,name,[])


    def execute(self,T,AllEntriesData,GlobalData,ThisEntryData):

        try:
            momentum1 = TVector3( ThisEntryData[self.px1][self.index1], ThisEntryData[self.py1][self.index1], ThisEntryData[self.pz1][self.index1] )
            momentum2 = TVector3( ThisEntryData[self.px2][self.index2], ThisEntryData[self.py2][self.index2], ThisEntryData[self.pz2][self.index2] )
        except NameError:
            ThisEntryData[self.outputVarName] = -1
            return
        except IndexError:
            ThisEntryData[self.outputVarName] = -1
            return
        
        energy1   = TMath.Sqrt( momentum1.Dot( momentum1 ) + self.m1*self.m1 )
        fourVec1  = TLorentzVector( momentum1, energy1 )
        energy2   = TMath.Sqrt( momentum2.Dot( momentum2 ) + self.m2*self.m2 )
        fourVec2  = TLorentzVector( momentum2, energy2 )

        sumVec = fourVec1 + fourVec2

        ThisEntryData[self.outputVarName] = sumVec.M()

        return True

class CalcInvMassInternalVars_ptEtaPhi(TTreeAlgorithm):
    def __init__(self,name, index1,index2,
                 pt1, eta1, phi1, m1, 
                 pt2, eta2, phi2, m2, 
                 outputVarName):

        self.index1=index1
        self.index2=index2

        self.pt1 = pt1
        self.eta1 = eta1
        self.phi1 = phi1
        self.pt2 = pt2
        self.eta2 = eta2
        self.phi2 = phi2
                

        self.m1=m1
        self.m2=m2

        self.outputVarName = outputVarName

        TTreeAlgorithm.__init__(self,name,[])


    def execute(self,T,AllEntriesData,GlobalData,ThisEntryData):

        #self.setupBranches(T,ThisEntryData)

        momentum1 = TVector3( 1, 1, 1)
        momentum2 = TVector3( 1, 1, 1)
        try:
            momentum1.SetPtEtaPhi( ThisEntryData[self.pt1][self.index1], ThisEntryData[self.eta1][self.index1], ThisEntryData[self.phi1][self.index1] )
            momentum2.SetPtEtaPhi( ThisEntryData[self.pt2][self.index2], ThisEntryData[self.eta2][self.index2], ThisEntryData[self.phi1][self.index2] )

        except NameError:
            ThisEntryData[self.outputVarName] = -1
            return True
        except IndexError:
            ThisEntryData[self.outputVarName] = -1
            return True
        
        energy1   = TMath.Sqrt( momentum1.Dot( momentum1 ) + self.m1*self.m1 )
        fourVec1  = TLorentzVector( momentum1, energy1 )

        energy2   = TMath.Sqrt( momentum2.Dot( momentum2 ) + self.m2*self.m2 )
        fourVec2  = TLorentzVector( momentum2, energy2 )

        sumVec = fourVec1 + fourVec2
        
        ThisEntryData[self.outputVarName] = sumVec.M()

        return True
