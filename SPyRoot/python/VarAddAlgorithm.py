# ------------------------------------------------------------- #
# package: SPyRoot                                              #
# file: VarAddAlgorithm                                         #
#                                                               #
# authors: Till Eifert <Till.Eifert@cern.ch> - U. of Geneva     #
# modified : Rshiraj Pravahan 08/30/2009                        #
#            -- added outputvar to AllEntriesData               # 
# File and Version Information:                                 #
# $Id: VarAddAlgorithm.py,v 1.4 2008/02/21 19:44:57 eifert Exp $#
# ------------------------------------------------------------- #


from TTreeAlgorithm import *
from ROOT import *

class SimpleVarAddAlgorithm(TTreeAlgorithm):
    def __init__(self,name,Expr,Branches,OutputVar,Test="2>1"):
        self.Expression=Expr
        self.OutputVar = OutputVar
        self.Test=Test
        TTreeAlgorithm.__init__(self,name,Branches)

    def execute(self,T,AllEntriesData,GlobalData,ThisEntryData):
        if eval(self.Test):
            ThisEntryData[self.OutputVar] = eval(self.Expression)
            AllEntriesData[self.OutputVar] = eval(self.Expression)
        else:
            ThisEntryData[self.OutputVar]=-1
            AllEntriesData[self.OutputVar]=-1
        return True

class VarAddAlgorithm(TTreeAlgorithm):
    #if Test passes, Condition is evaluated. If condition==1 then Expr1 else Expr2
    def __init__(self,name,Condition,Expr1,Expr2,Branches,OutputVar,Test="2>1"):
        self.Expression1= Expr1
        self.Expression2= Expr2
        self.Condition = Condition
        self.OutputVar = OutputVar
        self.Test=Test
        TTreeAlgorithm.__init__(self,name,Branches)
         
    def execute(self,T,AllEntriesData,GlobalData,ThisEntryData):
        if eval(self.Test):
            if eval(self.Condition):
                ThisEntryData[self.OutputVar] = eval(self.Expression1)
                AllEntriesData[self.OutputVar] = eval(self.Expression1)
            else :
                ThisEntryData[self.OutputVar] = eval(self.Expression2)
                AllEntriesData[self.OutputVar] = eval(self.Expression2)
        else:
            ThisEntryData[self.OutputVar]=-1
            AllEntriesData[self.OutputVar]=-1
        return True
