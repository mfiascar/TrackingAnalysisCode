# ------------------------------------------------------------- #
# package: SPyRoot                                              #
# file: VarHistAlgorithm                                        #
# classes: VarHistAlgorithm                                     #
# purpose: analysis algorithms to create a 1D-histogram         #
#                                                               #
# authors: Amir Farbin <Amir.Farbin@cern.ch> - CERN             #
#          Till Eifert <Till.Eifert@cern.ch> - U. of Geneva     #
#          Jamie Boyd  <Jamie.Boyd@cern.ch>  - CERN             #
#                                                               #
# File and Version Information:                                 #
# $Id: VarHistAlgorithm.py,v 1.3 2008/02/26 21:00:03 eifert Exp $
# ------------------------------------------------------------- #


from TTreeAlgorithm import *
from ROOT import *

class VarHistAlgorithm(TTreeAlgorithm):
    def __init__(self, name, HistName, Var, Bins, Min, Max, Branches, Cut='1'):
        self.HistName=HistName
        self.Bins=Bins
        self.Min=Min
        self.Max=Max
        self.Expression=Var
        self.Cut = Cut
        self.CutExp = ''
        TTreeAlgorithm.__init__(self,name,Branches)

    def initialize(self,TheSample,AllEntriesData,GlobalData):
        AllEntriesData[self.HistName]=TH1F(self.HistName, self.HistName,  
                                           self.Bins,self.Min,self.Max)
        if TheSample.eventWeightVar  != '':
            self.CutExp = "(%s) * T.%s" % ( self.Cut, TheSample.eventWeightVar )
        else:
            self.CutExp = "(%s)" % ( self.Cut )
            pass
        
        return True

    def execute(self,T,AllEntriesData,GlobalData,ThisEntryData):
        w= eval(self.CutExp)
        if w != 0. : AllEntriesData[self.HistName].Fill(eval(self.Expression), w )
        return True
