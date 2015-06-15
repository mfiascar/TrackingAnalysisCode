# ------------------------------------------------------------- #
# package: SPyRoot                                              #
# file: AddEvtCounter                                         #
# classes:
# purpose:
#                                                               #
# authors: Till Eifert <Till.Eifert@cern.ch> - U. of Geneva     #
# File and Version Information:                                 #
# $Id: AddEvtCounter.py,v 1.2 2008/01/17 08:58:25 eifert Exp $
# ------------------------------------------------------------- #


from TTreeAlgorithm import *
from ROOT import *

class AddEvtCounter(TTreeAlgorithm):
    def __init__(self, name, counterName="evt_number"):
        self.counterName=counterName
        self.counter = 0
        TTreeAlgorithm.__init__(self,name,[])

    def execute(self,T,AllEntriesData,GlobalData,ThisEntryData):
        ThisEntryData[self.counterName] = self.counter
        self.counter += 1
        return True
