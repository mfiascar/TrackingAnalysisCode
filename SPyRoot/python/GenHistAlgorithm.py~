# ------------------------------------------------------------- #
# package: SPyRoot                                              #
# file: GenHistAlgorithm                                        #
# classes: GenHistAlgorithm                                     #
# purpose: analysis algorithms to create any Root-histogram     #
#                                                               #
# authors: Till Eifert <Till.Eifert@cern.ch> - CERN             #
#                                                               #
# File and Version Information:                                 #
# $Id: VarHistAlgorithm.py,v 1.3 2008/02/26 21:00:03 eifert Exp $
# ------------------------------------------------------------- #


from TTreeAlgorithm import *
from ROOT import *
from array import array

def listify( item ):
    if type(item) is list: return item
    else : return [ item ]

class GenHistAlgorithm(TTreeAlgorithm):
    #
    # example usage:
    # GenHistAlgorithm(name="testHist", HistExp="TH1F('testHist','',100,0,1000)", VarX='T.myMET_et/1000.', Branches=['myMET_et'])
    # HistExp, VarX, VarY, VarZ can be lists (of same length)
    # Lumi: -1 = no normalization, 0 = unit area, >0: normalize to lumi (in pb-1)
    
    def __init__(self, name, HistExp, VarX, VarY=None, VarZ=None , Cut='1',
                 ReqTreeAttribute = None, ReqTransAttribute=None, Branches=[], Lumi=-1):
        self.HistExp = listify( HistExp )
        self.VarX    = listify( VarX )
        self.VarY    = listify( VarY )
        self.VarZ    = listify( VarZ )
        # any cut expression, will be evaluated (thus time consuming!)
        self.Cut = Cut
        self.CutExp = ''
        # a simple TTree variable (which is required to be non zero)
        self.ReqTreeAttribute = ReqTreeAttribute
        self.ReqTransAttribute = ReqTransAttribute

        self.Lumi = Lumi
        
        # base class constructor
        TTreeAlgorithm.__init__(self,name,Branches)

    def initialize(self,TheSample,AllEntriesData,GlobalData):

        #check if data or MC
        if "data" in TheSample.tags or "newdata" in TheSample.tags:
            print "Data run assumed"
            self.isData = True
        else:
            print "CMC run assumed"
            self.isData = False
            pass


        # sanity checks
        if len(self.HistExp) != len(self.VarX) :
            print self.name,"error length of HistExp",len(self.HistExp), "different from VarX",len(self.VarX)
            return False
        if len(self.HistExp) != len(self.VarY):
            if not self.VarY==[None]:
                print self.name,"error length of HistExp",len(self.HistExp), "different from VarY",len(self.VarY)
                return False
            else:
                self.VarY = [ None for i in xrange(len(self.HistExp)) ]
                pass
            pass
        if len(self.HistExp) != len(self.VarZ):
            if not self.VarZ == [None]:
                print self.name,"error length of HistExp",len(self.HistExp), "different from VarZ",len(self.VarZ)
                return False
            else:
                self.VarZ = [ None for i in xrange(len(self.HistExp)) ]
                pass
            pass
        
        # create histogram (from expression)
        print self.name,"creating histogram from expression(s):",self.HistExp
        self.histNames = []
        for histExp in self.HistExp:
            histName = histExp[ histExp.find('(')+2: histExp.find(',')-1 ]
            self.histNames.append( histName )
            print '   -- histName:',histName, 'exp:',histExp
            AllEntriesData[ histName ] = eval( histExp )
            AllEntriesData[ histName ].Sumw2()
            pass
        
        if TheSample.eventWeightVar  != '':
            self.CutExp = "(%s) * T.%s" % ( self.Cut, TheSample.eventWeightVar )
        else:
            self.CutExp = "%s" % ( self.Cut )
            pass

        # figure whether we'll have to run the T.__getattr__(self.ReqTreeAttribute)
        if self.ReqTreeAttribute :
            self.doReqTreeAttribute = True
            print "GenHistAlgorithm::%s will apply the cut: T.__getattr__('%s') " % (self.name, self.ReqTreeAttribute)
        else:
            self.doReqTreeAttribute = False
            pass
        if self.ReqTransAttribute :
            self.doReqTransAttribute = True
            print "GenHistAlgorithm::%s will apply the cut: ThisEntryData['%s'] " % (self.name, self.ReqTransAttribute)
        else:
            self.doReqTransAttribute = False
            pass
        # figure whether we'll have to run the eval(self.CutExp)
        self.doCut = True
        if self.CutExp == '1' or self.CutExp == '' :
            self.doCut = False
            #print "GenHistAlgorithm::%s will not apply the eval(cut) -- no cut & no eventWeight given" % (self.name)
        else:
            print "GenHistAlgorithm::%s will apply the cut: eval('%s')" % (self.name, self.CutExp)
            pass
        
        
        self.CutExpObj = compile( self.CutExp, "<cutString>", "eval")
        self.VarXObj = [ compile( varX,"<varXString>", "eval") for varX in self.VarX ]
        #self.VarXObj  = compile( self.VarX,   "<varXString>", "eval"
        self.VarYObj = []
        for varY in self.VarY:
            if varY:
                self.VarYObj.append( compile( varY,   "<varYString>", "eval") )
            else:
                self.VarYObj.append( None )
                pass
            pass
        self.VarZObj = []
        for varZ in self.VarZ:
            if varZ:
                self.VarZObj.append( compile( varZ,   "<varZString>", "eval") )
            else:
                self.VarZObj.append( None )
                pass
            pass
        #if self.VarY: self.VarYObj = compile( self.VarY,   "<varXString>", "eval")
        #if self.VarZ: self.VarZObj = compile( self.VarZ,   "<varXString>", "eval")

        return True

    def execute(self,T,AllEntriesData,GlobalData,ThisEntryData):

        if self.doReqTreeAttribute and not T.__getattr__(self.ReqTreeAttribute): return True
        if self.doReqTransAttribute and not ThisEntryData[ self.ReqTransAttribute ]: return True
        
        w = 1
        if self.doCut: w = eval(self.CutExpObj)
        if w == 0. : return True # selection failed (!)

        for ind in xrange(len(self.HistExp)):
            hn = self.histNames[ind]
            try:
                x = eval(self.VarXObj[ind])
            except IndexError:
                print 'Failed to index correctly in:',self.VarX[ind]
                print '  evt: ',ThisEntryData['evt']
                return True
        
            if self.VarY[ind] is None:
                AllEntriesData[ hn ].Fill(x, w)
                continue # go to next histogram

            y = eval(self.VarYObj[ind])
            if self.VarZ[ind] is None:
                AllEntriesData[ hn ].Fill(x, y, w)
                continue # go to next histogram

            z = eval(self.VarZObj[ind])
            AllEntriesData[ hn ].Fill(x, y, z, w)
            pass
        
        return True

    def finalize(self, TheSample, AllEntriesData, GlobalData):

        #if this is data, do not normalize to any lumi!!!
        if self.isData and self.Lumi >0:
            return True
        
        for ind in xrange(len(self.HistExp)):
            hn = self.histNames[ind]
            TheSample.NormalizeHist(AllEntriesData[ hn ],self.Lumi,UseSampleWeight=True)
                        
        return True
