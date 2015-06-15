# ------------------------------------------------------------- #
# package: SPyRoot                                              #
# file: VarCutAlgorithm                                         #
# classes: SimpleVarCutAlgorithm, VarCutAlgorithm               #
# purpose: analysis algorithms for cuts on TTree variables      #
#                                                               #
# authors: Amir Farbin <Amir.Farbin@cern.ch> - CERN             #
#          Till Eifert <Till.Eifert@cern.ch> - U. of Geneva     #
#          Jamie Boyd  <Jamie.Boyd@cern.ch>  - CERN             #
#          Maria Fiascaris <maria.fiascaris@cern.ch> - U. of Oxford #
#          Rishiraj Pravahan  UTA                               #
# File and Version Information:                                 #
# $Id: VarCutAlgorithm.py,v 1.7 2008/05/19 07:57:05 mfiascar Exp $
# ------------------------------------------------------------- #


from TTreeAlgorithm import *
from ROOT import *

class SimpleVarCutAlgorithm(TTreeAlgorithm):
    def __init__(self,name,Cut,Branches):
        self.Expression=Cut
        TTreeAlgorithm.__init__(self,name,Branches)

    def filter(self,T,AllEntriesData,GlobalData,ThisEntryData):
        return eval(self.Expression)


class SimpleVarTagAlgorithm(TTreeAlgorithm):
    def __init__(self,name,Cut,Branches,TagVar):
        self.Expression=Cut
        self.Tag=TagVar
        TTreeAlgorithm.__init__(self,name,Branches)

    def execute(self,T,AllEntriesData,GlobalData,ThisEntryData):
        try:
            res=eval(self.Expression)
            if res:
                ThisEntryData[self.Tag]=res
            return True
        except IndexError:
            print " Tag " + self.Expression +"Cannot be made due to Indexing Error!"
            ThisEntryData[self.Tag]=-1
            return True


class VarCutAlgorithm(TTreeAlgorithm):
    def __init__(self,name,CutVar,Comparitor,CutValue,Branch="",MakeHist=False,Tag=None):
        if Branch=="":
            Branches=[CutVar]
        else:
            Branches=[Branch]
            
        self.Tag=Tag

        self.CutVar=CutVar
        self.Comparitor=Comparitor
        self.CutValue=CutValue
        self.Expression="(T."+self.CutVar+") "+self.Comparitor+str(self.CutValue)
        self.MakeHist=MakeHist
        TTreeAlgorithm.__init__(self,name,Branches)

    def initialize(self,TheSample, AllEntriesData, GlobalData):
        if self.MakeHist:
            AllEntriesData[self.name]=TH1F(self.name,self.name,100,-float(self.CutValue),float(self.CutValue))
        return True

    def filter(self,T,AllEntriesData,GlobalData,ThisEntryData):
        if self.MakeHist:
            AllEntriesData[self.name].Fill(eval("T."+self.CutVar))
        res=eval(self.Expression)
        if self.Tag:
            ThisEntryData[self.Tag]=res

        return res


class ConditionalVarCutAlgorithm(TTreeAlgorithm):

    def __init__(self,name,Condition,Expression1,Expression2, Branches,Tag=None):
        self.Expression1 = Expression1
        self.Expression2 = Expression2
        self.Condition = Condition
        self.Tag=Tag
        TTreeAlgorithm.__init__(self,name,Branches)
         
    def filter(self,T,AllEntriesData,GlobalData,ThisEntryData):
        if eval(self.Condition):
            res=eval(self.Expression1)
        else:
            res=eval(self.Expression2)

        if self.Tag:
            if res:
                ThisEntryData[self.Tag]=1
            else:
                ThisEntryData[self.Tag]=0
            return True
        return res



class LoopVarCutAlgorithm(TTreeAlgorithm):
    def __init__(self, name,
                 variable_name, comparitor= "=",
                 Cut_value= 0.0,Cut_number_min=0,Cut_number_max=100, Expression="",Branches=[],MakeHist=False, lowBin=0.0, highBin=0.0,
                 UseInternal=True,Tag=None):

        self.name = name
        self.variable_name = variable_name
        self.comparitor = comparitor
        self.Cut_value = Cut_value
        self.Cut_number_min = Cut_number_min
        self.Cut_number_max = Cut_number_max
        self.MakeHist=MakeHist
        self.Expression=Expression
        self.lowBin= lowBin
        self.highBin= highBin
        self.UseInternal= UseInternal

        self.Tag=Tag

        TTreeAlgorithm.__init__(self,name,Branches)

    def initialize(self,T,AllEntriesData,GlobalData):
        if self.MakeHist:
            AllEntriesData[self.variable_name]=TH1F(self.name,self.name,100,self.lowBin,self.highBin)
        return True

    def filter(self,T,AllEntriesData,GlobalData,ThisEntryData):

        my_var_N=0
        if self.UseInternal:
            VarName="ThisEntryData['"+self.variable_name+"']"
        else:
            VarName="T."+self.variable_name
        #print VarName
        for t in range(len( eval(VarName) )):
            if self.Expression=="":
                Expression = "("+ self.variable_name +"[t])"+self.comparitor + str(self.Cut_value)
            else:
                Expression = self.Expression

            passed= eval(Expression)

            if not passed :
                continue

            my_var_N += 1
            
            if self.MakeHist:
                AllEntriesData[str(self.variable_name)].Fill(eval(VarName +"[t]"))

        res=True

        if ((my_var_N < self.Cut_number_min) or (my_var_N > self.Cut_number_max)):
            res=False


        if self.Tag:
            ThisEntryData[self.Tag]=res

        return res



