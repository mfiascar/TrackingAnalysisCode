# ------------------------------------------------------------- #
# package: SPyRoot                                              #
# file: WriterAlgorithm                                         #
# classes: WriterAlgorithm                                      #
#                                                               #
# authors: Till Eifert    <Till.Eifert@cern.ch> - U. of Geneva  #
#                                                               #
# Short description:                                            #
#   WriterAlgorithm will write out a root file which holds a    #
#   TTree. This TTree contains all the Branches that are used   #
#   (by other algs, WriterAlg). So, having a WriterAlgorithm    #
#   with Branches set to ["*"] will copy _all_ branches.        #
#   When running over several Samples, this Algorithm will try  #
#   to create 1 root ntuple for each Sample (this requires a    #
#   Sample entry in the globalData dict).                       #
#                                                               #
# File and Version Information:                                 #
# $Id: WriterAlgorithm.py,v 1.18 2008/06/05 08:37:42 eifert Exp $
# ------------------------------------------------------------- #

from TTreeAlgorithm import *
from ROOT import *
from array import array
import os


class WriterAlgorithm(TTreeAlgorithm):
    def __init__(self,name, outFileName="./outFile.root", Branches=["*"], addVar = [], CloneInputTree=True, OutputTreeName="",
                 CopyAdditionalTreeNames = [], XRDPath=None, MaxTries=5):

        self.outFileName=outFileName
        self.file = 0
        self.Branches = Branches
        self.AddVar = addVar
        self.NewBranches = {}
        self.tree = 0
        self.CloneInputTree = CloneInputTree
        self.OutputTreeName = OutputTreeName
        self.counter = 0
        self.XRDPath=XRDPath
        self.MaxTries=MaxTries
        TTreeAlgorithm.__init__(self,name,Branches)


    def initialize(self,TheSample, AllEntriesData, GlobalData):

        # try to use Sample name for output root file:

        if self.XRDPath:
            if GlobalData.has_key("SampleUniqueName"):
                pathEntries = self.outFileName.rsplit("/",1)
                if len(pathEntries) > 0:
                    dir = pathEntries[0]+"/"
                    file = pathEntries[1]
                else:
                    dir = ""
                    file = pathEntries[0]
                    pass
                fileName=self.XRDPath+dir+GlobalData["SampleUniqueName"]+"_"+file
            else:
                fileName = self.XRDPath+self.outFileName
                pass    
        else:
            # try to use Sample name for output root file:
            if GlobalData.has_key("SampleUniqueName"):
                # get the output directory
                pathEntries = self.outFileName.rsplit("/",1)
                if len(pathEntries) > 0:
                    new_dir = pathEntries[0]
                    if not os.path.isdir(new_dir): os.mkdir(new_dir)
                    new_file = pathEntries[1]
                else:
                    new_dir = "."
                    new_file = pathEntries[0]
                    pass
                fileName = new_dir+"/"+GlobalData["SampleUniqueName"]+"."+new_file
                pass
            else:
                fileName = self.outFileName
                pass
            pass
        
        SuccessOpen=False
        ntries=0

        while( not SuccessOpen and ntries<self.MaxTries):
            if self.XRDPath:
                self.file=TXNetFile(fileName,"recreate")
            else:
                fileName = fileName.replace('//','/')
                self.file = TFile(fileName,"recreate")
                pass
            if self.file.GetBytesRead()>0:
                print self.name, "Problem opening: ",filename
                print self.name, "Retry ",ntries
                SuccessOpen=True
                pass
            ntries+=1
            pass

        GlobalData["WriterAlgorithm"] = fileName
        print "WriterAlgorithm : writing to TFile re-created in '%s'" % fileName
        
        # initialize the output ttree
        if not self.tree:
            self.initBranches(TheSample)
            pass

        # speed-up adding new variables, by sorting them already by type:
        self.AddVarF = []
        self.AddVarI = []
        self.AddVarL = []
        self.AddVarf = []
        self.AddVari = []
        for var in self.AddVar:
            if   var[1] == "F": self.AddVarF.append( var )
            elif var[1] == "I": self.AddVarI.append( var )
            elif var[1] == "L": self.AddVarL.append( var )
            elif var[1] == "f": self.AddVarf.append( var )
            elif var[1] == "i": self.AddVari.append( var )
            pass

        return True



    def execute(self,T,AllEntriesData,GlobalData,ThisEntryData):

        # fill all the additional variables into our array:
        for var in self.AddVarF:
            num = min( len(ThisEntryData[var[0]]), var[2])
            for i in range(num): self.NewBranches[var[0]][i] = float(ThisEntryData[var[0]][i])
            pass
        for var in self.AddVarI:
            num = min( len(ThisEntryData[var[0]]), var[2])
            for i in range(num): self.NewBranches[var[0]][i] = int(ThisEntryData[var[0]][i])
            pass
        for var in self.AddVarL:
            num = min( len(ThisEntryData[var[0]]), var[2])
            for i in range(num): self.NewBranches[var[0]][i] = long(ThisEntryData[var[0]][i])
            pass        
        for var in self.AddVarf:
            self.NewBranches[var[0]][0] = float(ThisEntryData[var[0]])
            pass
        for var in self.AddVari:
            self.NewBranches[var[0]][0] = int(ThisEntryData[var[0]])
            pass

        self.tree.Fill()
        self.counter += 1
        return True


    def finalize(self,TheSample,AllEntriesData,GlobalData):
        print self.name," TTree.Fill() called",self.counter,"times"
        # in case the execute was never called, add (clone) the TTree structure
        if not self.tree:
            print "SHOULD NOT BE HERE ..."
            self.initBranches(TheSample)

        if isinstance(self.file, TFile):
            # self.tree.Scan("MT")
            self.file.Write()
            self.file.Close()
        # else:
            # mmh, we seemed to have lost our file. this could happen when we write out
            # loads of data and ROOT switches to new files.

        self.file = 0
        self.tree = 0

        return True


    def initBranches(self, TheSample):

        if self.CloneInputTree:
            T = TheSample.Chain
            T.GetEntries()
            T.GetEntry(0)
            # clone original tree header (all branches that are active) but do not copy events
            self.tree = TheSample.CloneTree(0)
        else:
            self.tree = TTree( self.OutputTreeName, self.OutputTreeName )
            TheSample.Dir = self.OutputTreeName
            # optionally, add more branches to the output tree
            pass
        
        #set maximum filesize to 19 GBytes to avoid multiple output files
        TTree.SetMaxTreeSize(19000000000L)

        for var in self.AddVar:
            if var[1] == "F" :
                maxn = int(var[2])
                self.NewBranches[var[0]] = array( var[1][0].lower(), maxn*[ 0. ])
                self.tree.Branch(var[0], self.NewBranches[var[0]], var[0]+"["+var[3]+"]/"+var[1][0])
            elif var[1] == "I" :
                maxn = int(var[2])
                self.NewBranches[var[0]] = array( var[1][0].lower(), maxn*[ 0 ])
                self.tree.Branch(var[0], self.NewBranches[var[0]], var[0]+"["+var[3]+"]/"+var[1][0])
            elif var[1] == "L" :
                maxn = int(var[2])
                self.NewBranches[var[0]] = array( var[1][0].lower(), maxn*[ 0 ])
                self.tree.Branch(var[0], self.NewBranches[var[0]], var[0]+"["+var[3]+"]/"+var[1][0])
            else:
                self.NewBranches[var[0]] = array( var[1][0].lower(), [0])
                self.tree.Branch(var[0], self.NewBranches[var[0]], var[0]+"/"+var[1][0])


class SimpleWriterAlgorithm(TTreeAlgorithm):
    def __init__(self,name, outFileName="./outFile.root", Branches=["*"], addVar = []):
        self.outFileName=outFileName
        self.file = 0
        self.Branches = Branches
        self.AddVar = addVar
        self.NewBranches = {}
        self.tree = 0
        TTreeAlgorithm.__init__(self,name,Branches)


    def initialize(self,T, AllEntriesData, GlobalData):

        # try to use Sample name for output root file:
        if GlobalData.has_key("Sample"):
            # get the output directory
            pathEntries = self.outFileName.rsplit("/",1)
            if len(pathEntries) > 0:
                dir = pathEntries[0]
                file = pathEntries[1]
            else:
                dir = "."
                file = pathEntries[0]

            fileName = dir+"/"+GlobalData["Sample"]+"_"+file


        else:
            fileName = self.outFileName

        self.file = TFile(fileName,"recreate")
        GlobalData["WriterAlgorithm"] = fileName

        if not self.tree:
            T.GetEntries()
            # clone original tree header (all branches that are active) but do not copy events
            self.tree = T.GetTree().CloneTree(0)

            # optionally, add more branches to the output tree
            for var in self.AddVar:
                self.NewBranches[var[0]] = array( var[1].lower(), [0])
                self.tree.Branch(var[0], self.NewBranches[var[0]], var[0]+"/"+var[1])
            T.GetEntry(0)

        return True



    def execute(self,T,AllEntriesData,GlobalData,ThisEntryData):


        # fill all the additional variables into our array:
        for var in self.AddVar:
            self.NewBranches[var[0]][0] = float(ThisEntryData[var[0]])

        self.tree.Fill()
        #print "test : %s" % T.MissingEt
        return True


    def finalize(self,T,AllEntriesData,GlobalData):
        # self.tree.Scan("MT")
        self.file.Write()
        self.file.Close()
        self.file = 0
        self.tree = 0
        return True
