# ------------------------------------------------------------- #
# package: SPyRoot                                              #
# file: VirtualCuts.py                                          #
# classes: VirtualCuts                                          #
# purpose: 
#                                                               #
# authors: Till Eifert <Till.Eifert@cern.ch> - CERN             #
#                                                               #
# ------------------------------------------------------------- #


from TTreeAlgorithm import *
from ROOT import *

def listify( item ):
    if type(item) is list: return item
    else : return [ item ]

class VirtualCuts( TTreeAlgorithm ):
    #
    # example usage:
    # 
    def __init__(self, name, listOfCuts, Cut='1', storeStats=True,
                 ReqTreeAttribute=None, ReqTransAttribute=None, Branches=[]):
        # any cut expression, will be evaluated (thus time consuming!)
        self.storeStats=storeStats
        self.Cut = Cut
        self.CutExp = ''
        self.simpleName=name
        self.prefix=name+'_'
        # a simple TTree variable (which is required to be non zero)
        self.ReqTreeAttribute = ReqTreeAttribute
        self.ReqTransAttribute = ReqTransAttribute
        # list of virtual cuts
        self.CutAlgorithms = []
        import VarCutAlgorithm
        for simpleCut in listOfCuts:
            cutAlgo = VarCutAlgorithm.SimpleVarCutAlgorithm(**simpleCut)
            self.CutAlgorithms.append( cutAlgo )
            pass
        # base class constructor
        TTreeAlgorithm.__init__(self,name+'_VC',Branches)

    def initialize(self,TheSample,AllEntriesData,GlobalData):
        
        if TheSample.eventWeightVar  != '':
            self.CutExp = "(%s) * T.%s" % ( self.Cut, TheSample.eventWeightVar )
        else:
            self.CutExp = "%s" % ( self.Cut )
            pass

        # figure whether we'll have to run the T.__getattr__(self.ReqTreeAttribute)
        if self.ReqTreeAttribute :
            self.doReqTreeAttribute = True
            print self.name,"will apply the cut: T.__getattr__('%s') " % (self.ReqTreeAttribute)
        else:
            self.doReqTreeAttribute = False
            pass
        if self.ReqTransAttribute :
            self.doReqTransAttribute = True
            print self.name,"will apply the cut: ThisEntryData['%s'] " % (self.ReqTransAttribute)
        else:
            self.doReqTransAttribute = False
            pass
        # figure whether we'll have to run the eval(self.CutExp)
        self.doCut = True
        if self.CutExp == '1' or self.CutExp == '' :
            self.doCut = False
            #print "VirtualCuts::%s will not apply the eval(cut) -- no cut & no eventWeight given" % (self.name)
        else:
            print self.name,"will apply the cut: eval('%s')" % (self.CutExp)
            pass

        self.CutExpObj = compile( self.CutExp, "<cutString>", "eval")
                
        # initialize all sub-algorithms
        for cutAlgo in self.CutAlgorithms:
            if not TheSample.RegisterStatsAlgo( self.prefix+cutAlgo.name ):
                return False
            cutAlgo.initialize( TheSample, AllEntriesData, GlobalData)
            pass

        TheSample.RegisterStatsAlgo( self.simpleName+'Cut' )
        # keep ref for TheSample
        self.TheSample = TheSample

        return True

    def execute(self,T,AllEntriesData,GlobalData,ThisEntryData):

        passCuts=True

        if self.doReqTreeAttribute and not T.__getattr__(self.ReqTreeAttribute): passCuts=False
        if self.doReqTransAttribute and not ThisEntryData[ self.ReqTransAttribute ]: passCuts=False
        
        w = 1
        if self.doCut: w = eval(self.CutExpObj)
        if w == 0. : passCuts=False

        # be pessimistic, assume algorithm will not make it
        ThisEntryData[self.simpleName+'Cut']=0
        for Alg in self.CutAlgorithms:
            ThisEntryData[self.prefix+Alg.name]=0
       
        if passCuts:
            self.TheSample.AddStatsBeforeAlgo( self.simpleName+'Cut', w )
            for Alg in self.CutAlgorithms:
                # store stats
                if self.storeStats and not self.TheSample.AddStatsBeforeAlgo( self.prefix+Alg.name, w ):
                    print self.name,"ERROR, AddStatsBeforeAlgo failed ?!?"
                    break
                passCuts=passCuts and Alg.filter(T, AllEntriesData, GlobalData, ThisEntryData)
                if passCuts :
                    ThisEntryData[self.prefix+Alg.name]=1
                if passCuts and not self.TheSample.AddStatsAfterAlgo( self.prefix+Alg.name, w ):
                    print self.name,"ERROR, AddStatsAfterAlgo failed ?!?"
                    break
                pass
            pass
        
        if passCuts:
            ThisEntryData[self.simpleName+'Cut']=1
            self.TheSample.AddStatsAfterAlgo( self.simpleName+'Cut', w )
            pass
        
        return True


    def finalize(self, TheSample, AllEntriesData, GlobalData):

        # finalize all sub-algorithms
        for cutAlgo in self.CutAlgorithms:
            if not TheSample.UnsubscribeStatsAlgo( self.prefix+cutAlgo.name ):
                return False
            cutAlgo.finalize( TheSample, AllEntriesData, GlobalData)
            pass
        TheSample.UnsubscribeStatsAlgo( self.simpleName+'Cut' )
        return True

    def getAllOutputVarNames(self):

        listOfOutputVars = []
        for cutAlgo in self.CutAlgorithms:       
            listOfOutputVars.append ( self.prefix+cutAlgo.name )
            pass


        return listOfOutputVars
    
