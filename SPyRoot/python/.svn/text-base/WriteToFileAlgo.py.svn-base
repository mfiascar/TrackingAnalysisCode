# ------------------------------------------------------------- #
# package: SPyRoot                                              #
# file: WriteToFileAlgo                                         #
# classes:
# purpose:
#                                                               #
# authors: Till Eifert <Till.Eifert@cern.ch> - U. of Geneva     #
# File and Version Information:                                 #
# $Id: WriteToFileAlgo.py,v 1.1 2008/01/10 13:59:36 eifert Exp $
# ------------------------------------------------------------- #


from TTreeAlgorithm import *
from ROOT import *

class WriteToFileAlgo(TTreeAlgorithm):
    def __init__(self, name, fileName, preStr, expression):
        self.file = open(fileName,"w")
        self.preStr = preStr
        self.expression = expression
        TTreeAlgorithm.__init__(self,name)


    def execute(self,T,AllEntriesData,GlobalData,ThisEntryData):
        printStr = str(eval( self.expression ))
        self.file.write(str(self.preStr) + printStr+"\n")
        return True

    def finalize(self,T,AllEntriesData,GlobalData):
        self.file.close
        return True
