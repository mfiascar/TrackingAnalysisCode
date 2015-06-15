from ROOT import TTree, gROOT

def GetLeafNames(T,Require=""):
    Leaves=T.GetListOfLeaves()
    List=[]
    for Leaf in Leaves:
        LName=Leaf.GetName()
        if LName.find(Require) > -1:
            List+=[LName]

    return List


def ProjectFromDraw(self):
    def Project(histname,**args):
#        gROOT.FindObject("blah")

        
