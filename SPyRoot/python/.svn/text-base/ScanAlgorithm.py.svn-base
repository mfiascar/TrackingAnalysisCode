# ------------------------------------------------------------- #
# package: SPyRoot                                              #
# file: ScanAlgorithm                                           #
# classes: ScanAlgorithm                                        #
# purpose: analysis algorithm to fill table with ntuple vars    #
#                                                               #
# authors: Brian Petersen <Brian.Petersen@cern.ch> - CERN       #
#                                                               #
# File and Version Information:                                 #
# $Id: $
# ------------------------------------------------------------- #


from TTreeAlgorithm import *
from ROOT import *

class ScanAlgorithm(TTreeAlgorithm):
    def __init__(self, name,Vars,Format,Cut, Branches, table,VectorVar=None):
        self.Vars=Vars
        self.Format=Format #this is temporary until formatting is implemented in the table itself
        self.Branches=Branches
        self.table=table
        self.Cut = Cut
        self.VectorVar=VectorVar
        TTreeAlgorithm.__init__(self,name,Branches)

    def initialize(self,TheSample,AllEntriesData,GlobalData):     
        return True

    def execute(self,T,AllEntriesData,GlobalData,ThisEntryData):
        if eval(self.Cut):
            if self.VectorVar:
                num=eval('T.'+self.VectorVar)
                if num!=0:
                    for idx in xrange(num):
                        row=self.table.AddRow()
                        for vv,ff in zip(self.Vars,self.Format):
                            if idx==0 or vv.find('[]')!=-1:
                                self.table[row,vv]=ff % eval('T.'+vv.replace('[]','['+str(idx)+']'))
                else:
                    row=self.table.AddRow()
                    for vv,ff in zip(self.Vars,self.Format):
                        if vv.find('[]')!=-1: continue
                        self.table[row,vv]=ff % eval('T.'+vv)
            else:
                row=self.table.AddRow()
                for vv,ff in zip(self.Vars,self.Format):
                    self.table[row,vv]=ff % eval('T.'+vv)
        return True
