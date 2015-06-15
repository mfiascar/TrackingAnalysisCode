# ------------------------------------------------------------- #
# package: SPyRoot                                              #
# file: TTreeAlgorithm                                          #
# classes: TTreeAlgorithm, TTreeAlgorithmLooper                 #
# purpose: Base class for analysis algorithms, looper class to  #
#          handle a chain of algorithms => a whole analysis     #
#                                                               #
# authors: Amir Farbin <Amir.Farbin@cern.ch> - CERN             #
#          Till Eifert <Till.Eifert@cern.ch> - U. of Geneva     #
#          Jamie Boyd  <Jamie.Boyd@cern.ch>  - CERN             #
#                                                               #
# File and Version Information:                                 #
# $Id: TTreeAlgorithm.py,v 1.11 2008/06/05 08:37:42 eifert Exp $
# ------------------------------------------------------------- #


from ROOT import *
import sys

class TTreeAlgorithm:
    def __init__(self, name, Branches=[]):
        self.timer=TStopwatch()
        self.timer.Reset()

        self.name=name
        self.Branches=Branches
        self.PrintLogs=0
        self.PrintEvt=1000
        self.NewChain=True
        self.fCurrent=-1
        self.Verbose=True
        self.CutFlows=["Default"]

    def SetDebug(self,PrintLogs=0, PrintEvt=1000):
        self.PrintLogs=PrintLogs
        self.PrintEvt=PrintEvt

    def SetCutFlow(self,CutFlows):
        self.CutFlows=CutFlows

    def HasCutFlow(self,CutFlow):
        for myCutFlow in self.CutFlows:
            if myCutFlow==CutFlow:
                return True
        return False

    def CheckChain(self,T):
        cn=T.GetTreeNumber()
        if cn != self.fCurrent:
            self.fCurrent= cn
            self.NewChain=True
            if self.Verbose:
                print self.name+":"
                print "FileName: ",T.GetFile().GetName()
                print "FileNumber: ",T.GetFileNumber()
                print "TreeNumber: ",T.GetTreeNumber()
                pass
            pass


    def Loop(self, TheSample, MaxEntries=-1, GlobalData={}, firstEntry=0, cacheSize = 50000000):
        AllEntriesData={}

        # get TCain
        T = TheSample.Chain

        T.SetCacheSize( cacheSize )
        T.SetBranchStatus("*",0)
        self.SetBranches(T)

        # if TheSample has an eventWeight, activate it and use it
        ew = False
        # switch off error msg from SetBranchStatus
        import ctypes
        e = ctypes.c_uint32(1)
        if TheSample.eventWeightVar != "":
            ew = True
            T.SetBranchStatus(TheSample.eventWeightBranch, 1,e)
            T.AddBranchToCache(TheSample.eventWeightBranch, 1)
            pass

        if not self.initialize(TheSample, AllEntriesData, GlobalData):
            print self.name, " initialize Failed"
            return [0, AllEntriesData]

        if MaxEntries<0:
            MaxEntries=T.GetEntries() - firstEntry

        # examples:
        # firstEntry = 0,   MaxEntries = 50 => want to process evts 0 to 49
        # firstEntry = 50,  MaxEntries = 50 => want to process evts 50 to 99
        # firstEntry = 100, MaxEntries = 50 => want to process evts 100 to 149
        for I in xrange(MaxEntries):
            evtCounter = firstEntry+I
            if self.PrintLogs and evtCounter % self.PrintEvt==0:
                print evtCounter

            size = T.GetEntry(evtCounter)
            if size <= 0 :  break

            ThisEntryData={}
            #ThisEntryData['evt'] = evtCounter

            w = 1.0
            if ew: w = eval("T." + TheSample.eventWeightVar)
            
            TheSample.AddStatsBeforeAlgo( self.name, w, self.CutFlows )
            self.CheckChain(T)
            if self.filter(T,AllEntriesData,GlobalData,ThisEntryData):
                # if filter succeeded, call the execute and also add TheSample's stats:
                self.execute(T,AllEntriesData,GlobalData,ThisEntryData)
                TheSample.AddStatsAfterAlgo( self.name, w, self.CutFlows )
                pass
            pass
        
        if not self.finalize(TheSample, AllEntriesData, GlobalData):
            print self.name, " finalize Failed"

        # done, return all results accumulated by the algorithm's filter & execute
        return [evtCounter, AllEntriesData]

    def SetBranches(self,T):
        # switch off error msg from SetBranchStatus
        import ctypes
        e = ctypes.c_uint32(1)
        for branchname in self.Branches:
            try:
                T.SetBranchStatus(branchname,1,e)
            except TypeError:
                print self.name," bad branch name ", branchname

    def initialize(self, TheSample, AllEntriesData, GlobalData):
        return True

    def finalize(self, TheSample, AllEntriesData, GlobalData):
        return True

    def filter(self, T, AllEntriesData, GlobalData, ThisEntryData):
        return True

    def execute(self,T, AllEntriesData,GlobalData,ThisEntryData):
        return True

class TTreeAlgorithmLooper(TTreeAlgorithm):
    def __init__(self, name, Branches=[],virtualCuts=False):
        self.Algorithms=[]
        TTreeAlgorithm.__init__(self,name,Branches)
        self.activeBranches = []
        self.virtualCuts=virtualCuts

    def Print(self):
        for alg in self.Algorithms:
            print alg.name

    def AddAlgorithm(self,Alg):
        """
        Add one algorithm to the chain of algorithms to execute.
        """
        self.Algorithms += [ Alg ]

    def SetBranches(self,T):
        """
        Call each algorithm's SetBranches method.
        """
        for Alg in self.Algorithms:
            Alg.SetBranches(T)

    def initialize(self, TheSample, AllEntriesData, GlobalData):
        """
        Call each algorithm's initialize method.
        """
        if self.virtualCuts:
            #hack - assumes last algo is the writer algo
            lastAlgo=self.Algorithms[-1]
            if hasattr(lastAlgo,'AddVar'):
                for Alg in self.Algorithms[:-1]:
                    lastAlgo.AddVar.append([Alg.name,'i'])
        for Alg in self.Algorithms:
            if not TheSample.RegisterStatsAlgo( Alg.name ):
                return False
            if not Alg.initialize(TheSample, AllEntriesData, GlobalData):
                print Alg.name," initialize Failed."
                return False
        return True

    def finalize(self, TheSample, AllEntriesData, GlobalData):
        """
        Call each algorithm's finalize method.
        """

        for Alg in self.Algorithms:
            if not TheSample.UnsubscribeStatsAlgo( Alg.name ):
                return False
            if not Alg.finalize(TheSample, AllEntriesData, GlobalData):
                print Alg.name," finalize Failed."
                return False
        for Alg in self.Algorithms:
            print Alg.name+':',
            Alg.timer.Print()
        return True


    def Loop(self, TheSample, MaxEntries=-1, GlobalData={}, firstEntry=0, cacheSize = 50000000):
        """
        This will 'run' all algorithms belonging to this analysis (algorithm sequence).
        What happens:
        1) call all algorithm's initialize
        2) loop over all events of TheSample and for each event
           2.1) loop over all algorithms and
                call their execute
           2.2) In case an algorithm's execute returns False, go to next evt
        3) call all algorithm's finalize
        4) return AllEntriesData
        """
        evtCounter=0
        AllEntriesData={}

        TheSample.initChain()
        T = TheSample.Chain

        # stop here, in case T is not of type TChain ...
        if not isinstance(T, TTree):
            return [0,{}]
        
        T.SetCacheSize( cacheSize )
        print self.name, " setting the Branches"
        T.SetBranchStatus("*",0)
        self.SetBranches(T)

        # if TheSample has an eventWeight, activate it and use it
        ew = False
        # switch off error msg from SetBranchStatus
        import ctypes
        e = ctypes.c_uint32(1)
        if TheSample.eventWeightVar != "":
            T.SetBranchStatus(TheSample.eventWeightBranch, 1,e)
            T.AddBranchToCache(TheSample.eventWeightBranch, 1)
            ew = True
            pass

        print self.name, " calling all algorithms' initialize"
        if not self.initialize(TheSample, AllEntriesData, GlobalData):
            print self.name, " initialize Failed"
            return [0, AllEntriesData]

        if MaxEntries < 0:
            MaxEntries = T.GetEntries() - firstEntry


        # examples:
        # firstEntry = 0,   MaxEntries = 50 => want to process evts 0 to 49
        # firstEntry = 50,  MaxEntries = 50 => want to process evts 50 to 99
        # firstEntry = 100, MaxEntries = 50 => want to process evts 100 to 149

        # speed-ups
        printLogs = self.PrintLogs
        printEvt  = self.PrintEvt
        loadTree  = T.LoadTree
        getEntry  = T.GetEntry
        virtualcuts = self.virtualCuts
        algs = self.Algorithms
        # Big loop over all events
        for I in xrange(MaxEntries):
            evtCounter=firstEntry+I
            # log prints
            if printLogs and evtCounter%printEvt==0:
                print evtCounter
                pass
            ientry = loadTree(evtCounter)
            if ientry < 0 : break
            size = getEntry(evtCounter)
            if size <= 0 :  break
            
            ThisEntryData={}
            ThisEntryData['evt'] = evtCounter

            w = 1.0
            if ew: w = eval("T." + TheSample.eventWeightVar) # can improve speed here (!) ... but only for mc@nlo samples

            # execute one algo after another, for each call
            # 1) execute
            cutCounter=0
            passCuts=True
            if virtualcuts :
                ThisEntryData[virtualcuts]=cutCounter
            for Alg in algs:
                cutCounter+=1
                if virtualcuts:
                    ThisEntryData[Alg.name]=0
                Alg.timer.Start(false)
                # store stats
                if not TheSample.AddStatsBeforeAlgo( Alg.name, w ):
                    Alg.timer.Stop()
                    print "TTreeAlgorithmLooper: ERROR, AddStatsBeforeAlgo failed ?!?"
                    break
                passCuts=passCuts and Alg.filter(T, AllEntriesData, GlobalData, ThisEntryData)
                if passCuts and virtualcuts:
                    ThisEntryData[virtualcuts]=cutCounter
                    ThisEntryData[Alg.name]=1
                if not passCuts and not virtualcuts :
                    # break the algorithm loop, ie stop execution of any further algo for this event
                    # and go on with the next event
                    Alg.timer.Stop()
                    break
                # if filter succeeded, call the execute and also add stats:
                Alg.execute(T, AllEntriesData, GlobalData, ThisEntryData) 
                if passCuts and not TheSample.AddStatsAfterAlgo( Alg.name, w ):
                    Alg.timer.Stop()
                    break
                Alg.timer.Stop()

        # done with event loop, do finalization
        print "--- Finalize ---"
        if not self.finalize(TheSample, AllEntriesData, GlobalData):
            print self.name, " finalize Failed"
            return [evtCounter, AllEntriesData]


        # store analysis name
        TheSample.analyses += [ self.name ]

        print "done with TTreeAlgorithmLooper"
        return [evtCounter, AllEntriesData]


class SmartTTreeAlgorithmLooper(TTreeAlgorithm):
    def __init__(self, name, Branches=[],virtualCuts=False):
        self.Algorithms=[]
        TTreeAlgorithm.__init__(self,name,Branches)
        self.activeBranches = []
        self.NewChain=True
        self.fCurrent=-1
        self.CutFlows=["Default"]
        self.virtualCuts=virtualCuts

    def Print(self):
        print "Algorithm: CutFlows"
        for alg in self.Algorithms:
            print alg.name+":", alg.CutFlows

    def SetLastAlgCutFlows(self,CutFlows):

        nalg=len(self.Algorithms)
        
        if nalg>0:
            self.Algorithms[nalg-1].SetCutFlow(CutFlows)
            for CutFlow in CutFlows:
                haveit=False
                for myCutFlow in self.CutFlows:
                    if myCutFlow==CutFlow:
                        haveit=True
                        break
                if not haveit:
                    self.CutFlows+=[CutFlow]
        else:
            print "TTreeAlgorithmLooper SetLastAlgCutFlows Warning: No Algorithms"


    def SetAlgCutFlows(self,name,CutFlows):
        foundalg=False
        for alg in self.Algorithms:
            if alg.name==name:
                foundalg=True
                alg.SetCutFlow(CutFlows)
                for CutFlow in CutFlows:
                    haveit=False
                    for myCutFlow in self.CutFlows:
                        if myCutFlow==CutFlow:
                            haveit=True
                            break
                    if not haveit:
                        self.CutFlows+=[CutFlow]
        if not foundalg:
            print "TTreeAlgorithmLooper SetAlgCutFlows Warning: No Algorithm Named",name

    def GetAlgorithm(self,name):
        for alg in self.Algorithms:
            if alg.name==name:
                return alg
        return None


    def SetAllAlgCutFlows(self,CutFlows):
        nalg=len(self.Algorithms)
        
        if nalg>0:
            for alg in self.Algorithms:
                alg.SetCutFlow(CutFlows)
            for CutFlow in CutFlows:
                haveit=False
                for myCutFlow in self.CutFlows:
                    if myCutFlow==CutFlow:
                        haveit=True
                        break
                if not haveit:
                    self.CutFlows+=[CutFlow]
        else:
            print "TTreeAlgorithmLooper SetLastAlgCutFlows Warning: No Algorithms"
        


    def AddAlgorithm(self,Alg):
        """
        Add one algorithm to the chain of algorithms to execute.
        """
        self.Algorithms += [ Alg ]

    def SetBranches(self,T):
        """
        Call each algorithm's SetBranches method.
        """
        for Alg in self.Algorithms:
            Alg.SetBranches(T)

    def initialize(self, TheSample, AllEntriesData, GlobalData):
        """
        Call each algorithm's initialize method.
        """
        if self.virtualCuts:
            #hack - assumes last algo is the writer algo
            lastAlgo=self.Algorithms[-1]
            if hasattr(lastAlgo,'AddVar'):
                for Alg in self.Algorithms[:-1]:
                    lastAlgo.AddVar.append([Alg.name,'i'])
        for Alg in self.Algorithms:
            if not TheSample.RegisterStatsAlgo( Alg.name, Alg.CutFlows ):
                return False
            if not Alg.initialize(TheSample, AllEntriesData, GlobalData):
                print Alg.name," initialize Failed."
                return False
        return True

    def finalize(self, TheSample, AllEntriesData, GlobalData):
        """
        Call each algorithm's finalize method.
        """

        for Alg in self.Algorithms:
            if not TheSample.UnsubscribeStatsAlgo( Alg.name ):
                return False
            if not Alg.finalize(TheSample, AllEntriesData, GlobalData):
                print Alg.name," finalize Failed."
                return False
        for Alg in self.Algorithms:
            print Alg.name+':',
            Alg.timer.Print()
        return True


    def CheckChain(self,T):
        cn=T.GetTreeNumber()
        if cn != self.fCurrent:
            if self.Verbose:
                print "FileName: ",T.GetFile().GetName()
                print "FileNumber: ",T.GetFileNumber()
                print "TreeNumber: ",T.GetTreeNumber()
            self.fCurrent= cn
            return True
        return False

    def Loop(self, TheSample, MaxEntries=-1, GlobalData={}, firstEntry=0, cacheSize = 50000000):
        """
        This will 'run' all algorithms belonging to this analysis (algorithm sequence).
        What happens:
        1) call all algorithm's initialize
        2) loop over all events of TheSample and for each event
           2.1) loop over all algorithms and
                call their filter
                call their execute
           2.2) In case an algorithm's filter returns False, go to next evt
        3) call all algorithm's finalize
        4) return AllEntriesData
        """
        evtCounter=0
        AllEntriesData={}

        TheSample.initChain()
        T = TheSample.Chain

        # stop here, in case T is not of type TChain ...
        if not isinstance(T, TTree):
            return [0, {}]

        T.SetCacheSize( cacheSize )
        print self.name, " setting the Branches"
        T.SetBranchStatus("*",0)
        self.SetBranches(T)

        # if TheSample has an eventWeight, activate it and use it
        ew = False
        # switch off error msg from SetBranchStatus
        import ctypes
        e = ctypes.c_uint32(1)
        if TheSample.eventWeightVar != "":
            T.SetBranchStatus(TheSample.eventWeightBranch, 1, e)
            T.AddBranchToCache(TheSample.eventWeightBranch, 1)
            ew = True
            pass

        print self.name, " calling all algorithms' initialize"
        if not self.initialize(TheSample, AllEntriesData, GlobalData):
            print self.name, " initialize Failed"
            return [0, AllEntriesData]

        if MaxEntries < 0:
            MaxEntries = T.GetEntries() - firstEntry


        # examples:
        # firstEntry = 0,   MaxEntries = 50 => want to process evts 0 to 49
        # firstEntry = 50,  MaxEntries = 50 => want to process evts 50 to 99
        # firstEntry = 100, MaxEntries = 50 => want to process evts 100 to 149


        CutFlowStats={}

        for CutFlow in self.CutFlows:
            CutFlowStats[CutFlow]=[0,0,1] # Called, Passed, Status

        # Big loop over all events
        for I in xrange(MaxEntries):
            evtCounter=firstEntry+I
            # log prints
            if self.PrintLogs and evtCounter%self.PrintEvt==0:
                print evtCounter
                #sys.stdout.flush()
                pass
#            ientry = T.LoadTree(evtCounter)
#            if ientry < 0 : break
            size = T.GetEntry(evtCounter)
            if size <= 0 :  break
            
            ThisEntryData={}
            ThisEntryData['evt'] = evtCounter

            w = 1.0
            if ew:
                try:
                    w = eval("T." + TheSample.eventWeightVar)
                except AttributeError:
                    w=1.0
                    ew=False
                    print "Warning... eventweight variable,", TheSample.eventWeightVar,"not found."
                except IndexError:
                    w=1.0
                    ew=False
                    print "Warning... eventweight variable,", TheSample.eventWeightVar,"not found."

            # execute one algo after another, for each call
            # 1) filter and if that was successfull
            # 2) execute
                

            # Check if the TChain has switched to a file...
            # If so, notify all algorithms, so they can reset their branches
            # Note that algorithms must reset the NewChain flag to False
            # (this makes sure that they are no affected by skimming)

            NewChain= self.CheckChain(T)
            if NewChain:
                for Alg in self.Algorithms:
                    Alg.NewChain=NewChain

            for CutFlow in self.CutFlows:
                CutFlowStats[CutFlow][0]+=1 
                CutFlowStats[CutFlow][2]=1 # Status

            cutCounter=0
            passCuts=True
            if self.virtualCuts:
                ThisEntryData[self.virtualCuts]=cutCounter

            for Alg in self.Algorithms:
                # Add the CutFlow name to ThisEntryData for writing out
                for CutFlowStat in CutFlowStats:
                    ThisEntryData[CutFlowStat] = CutFlowStats[CutFlowStat][2]

                RunAlg=False
                
                CutFlowsToUpdate=[]
                for AlgCutFlow in Alg.CutFlows:
                    if CutFlowStats[AlgCutFlow][2]==1:
                        RunAlg=True
                        CutFlowsToUpdate+=[AlgCutFlow]

                if not RunAlg: # No need run alg... 
                    continue

                cutCounter+=1
                if self.virtualCuts:
                    ThisEntryData[Alg.name]=0
                
                Alg.timer.Start(false)
                if not TheSample.AddStatsBeforeAlgo( Alg.name, w, CutFlowsToUpdate ):
                    print "Warning... Bad Stats! Breaking Algorithm Loop.",Alg.name
                    Alg.timer.Stop()
                    break
                
                passfilter=Alg.filter(T, AllEntriesData, GlobalData, ThisEntryData)
                passCuts = passCuts and passfilter

                if passCuts and self.virtualCuts:
                    ThisEntryData[self.virtualCuts]=cutCounter
                    ThisEntryData[Alg.name]=1

                if not passfilter: # and (not passCuts and not self.virtualCuts):
                    for AlgCutFlow in Alg.CutFlows:
                        CutFlowStats[AlgCutFlow][2]=0
                    Alg.timer.Stop()
                else:
                    Alg.execute(T, AllEntriesData, GlobalData, ThisEntryData)
                    Alg.timer.Stop()
                    
                    if not TheSample.AddStatsAfterAlgo( Alg.name, w, CutFlowsToUpdate ):
                        break
                
            for CutFlow in self.CutFlows:
                if CutFlowStats[CutFlow][2]==1:
                    CutFlowStats[CutFlow][1]+=1 


        # done with event loop, do finalization
        AllEntriesData["CutFlowStats"]=CutFlowStats

        if not self.finalize(TheSample, AllEntriesData, GlobalData):
            print self.name, " finalize Failed"
            return AllEntriesData


        # store analysis name
        TheSample.analyses += [ self.name ]

        print "done with TTreeAlgorithmLooper"
        return [evtCounter, AllEntriesData]


class SmartTTreeAlgorithm(TTreeAlgorithm):
    def __init__(self, name, VariableMap, UseInternalVariables=False):
        self.VariableMap=VariableMap
        self.UseInternalVariables=UseInternalVariables
        Branches=[]

        if not UseInternalVariables:
            for var in self.VariableMap:
                Branches+=[self.VariableMap[var]]


        self.SimpleTypeBranchNames=[]
        self.BuildSimpleTypeList=True

        TTreeAlgorithm.__init__(self,name,Branches)

    def setupBranches(self,T,ThisEntryData):

        if self.UseInternalVariables:
            for var in self.VariableMap.iteritems():
                self.__dict__[var[0]]=ThisEntryData[var[1]]
        else:
            # Simple Types need to be set per event... build a list of them
            if self.BuildSimpleTypeList:
                for var in self.VariableMap.iteritems():
                    if type(T.__getattr__(var[1])) in [long,int,float] or 'typecode' in dir(T.__getattr__(var[1])) :
                        self.SimpleTypeBranchNames.append(var)
                        self.BuildSimpleTypeList=False
#                print self.name,"Simple Types",self.SimpleTypeBranchNames

            # Set Simple Types every event
            for var in self.SimpleTypeBranchNames:
                    self.__dict__[var[0]]=T.__getattr__(var[1])

            # Other types need to be set when there is a new file
            if self.NewChain:
                for var in self.VariableMap.iteritems():
                    self.__dict__[var[0]]=T.__getattr__(var[1])
                    self.NewChain=False
