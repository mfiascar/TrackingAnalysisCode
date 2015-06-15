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
# $Id: VarHist2DAlgorithm.py,v 1.3 2008/02/26 21:00:03 eifert Exp $
# ------------------------------------------------------------- #


from TTreeAlgorithm import *
from ROOT import *

class VarHist2DAlgorithm(TTreeAlgorithm):
    def __init__(self,name,HistName,HistTitle,VarX,BinsX,MinX,MaxX,VarY,BinsY,MinY,MaxY,Branches):
        self.HistTitle=HistTitle
        self.HistName=HistName
        self.BinsX=BinsX
        self.MinX=MinX
        self.MaxX=MaxX
        self.ExpressionX=VarX
        self.BinsY=BinsY
        self.MinY=MinY
        self.MaxY=MaxY
        self.ExpressionY=VarY
        TTreeAlgorithm.__init__(self,name,Branches)

    def initialize(self,TheSample,AllEntriesData,GlobalData):
        AllEntriesData[self.name+"_"+self.HistName]=TH2F(self.HistName,self.HistTitle,
                                                         self.BinsX,self.MinX,self.MaxX,
                                                         self.BinsY,self.MinY,self.MaxY)
        return True

    def execute(self,T,AllEntriesData,GlobalData,ThisEntryData):
        AllEntriesData[self.name+"_"+self.HistName].Fill(eval(self.ExpressionX), eval(self.ExpressionY))
        return True
