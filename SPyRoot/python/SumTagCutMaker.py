# ------------------------------------------------#
# Rishiraj Pravahan                               #
# Date 19/06/2009                                 #
#                                                 #
# ------------------------------------------------#

from TTreeAlgorithm import *
from ROOT import *

class SumTagCutMaker(TTreeAlgorithm):
    def __init__(self,name, tagVar="",thetype="p",Tag=None):
        self.tagVar=tagVar
        self.thetype=thetype
        self.Tag=Tag
        TTreeAlgorithm.__init__(self,name)

    def filter(self,T,AllEntriesData,GlobalData,ThisEntryData):
        count=0
        tag=ThisEntryData[self.tagVar]
        for i in xrange(len(tag)):
            if tag[i]==1 and self.thetype=="n":
                count +=1
            elif tag[i]==0 and self.thetype=="p":
                count +=1
            else:
                continue
        if count >0 :
            if self.Tag:
                ThisEntryData[self.Tag]=False
            return False

        if self.Tag :
            ThisEntryData[self.Tag]=True

        return True

