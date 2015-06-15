# ------------------------------------------------------------- #
# package: SPyRoot                                              #
# file: Sample                                                  #
# classes: Sample, CombinedSample, GridSample                   #
#                                                               #
# authors: Amir Farbin    <Amir.Farbin@cern.ch> - CERN          #
#          Till Eifert    <Till.Eifert@cern.ch> - U. of Geneva  #
#          Jamie Boyd     <Jamie.Boyd@cern.ch>  - CERN          #
#                                                               #
# File and Version Information:                                 #
# $Id: Sample.py,v 1.40 2009/06/05 14:01:01 mfiascar Exp $
# ------------------------------------------------------------- #

from ROOT import *
from os import popen, getcwd, path
import root_pickle
from copy import deepcopy
from array import array
from SObject import SObject
from math import sqrt

######################################################################################
## Sample class
##
## Descirption: represent a physics sample with x-section, file names, histograms
##
######################################################################################

class Sample(SObject):
    def __init__(self, name, dir="", simpleCutFlow=True):
        # super class's constructor
        SObject.__init__(self, name=name)
        
        self.name       = name
        self.className  = "Sample"
        self.moduleName = "Sample"
        
        self.Files = []           # Ntuple file(s) containing the ttree(s) (with similar format!)
        self.Dir   = dir          # TTree name
        self.Chain = TChain(dir)  # Thain for the ttree(s)

        self.XSection  = -1.0     # cross section of the sample (this is also used by default as a sample weight!)
        self.genEvents = -1       # number of (effectively) generated events from MC - should correpsond to the XSection !
        self.Lumi      = -1.0     # integrated luminosity of sample
        self.LiveTime  = -1.0     # for data runs: trigger live time
        self.RunNumber = -1       # for data runs: Run Number
        self.Weight    = 1.0      # can be : assumed_lumi / mc_lumi  or  x-section / MC_events
        self.eventWeightVar = ""  # eventWeight variable, if existing in TTree
        # branch eventWeight, if existing in TTree (note: branch can be "myBranch", and weight "myBranch[0]")
        self.eventWeightBranch = self.eventWeightVar
        
        
        self.tags = []            # list of strings for grouping Sample objects together

        self.description = ""     # description of underlying process (e.g. MCi nfo, data information)

        self.extraMetaInformation = {} # can hold e.g. SUSY model specific parameters (m0 = '', ...)

        # analysis results
        self.analyses       = []  # list of analyses (names) that were run (just for reference)
        self.resultTObjects = {}  # any TObject results from the algorithms
        self.results        = {}  # any non TObject results from the algorithms
        self.Statistics     = {}  # every algorithm that was executed is stored together with evts before/after it
                                  # if an eventWeight is given, the weighter evts before/after are also stored

        self.__fStats = self.Statistics
        self.SimpleCutFlow = simpleCutFlow
        
        self.listPickleVars = [
            'name',
            'className',
            'moduleName',
            'Files',
            'Dir',
            'XSection',
            'genEvents',
            'Lumi',
            'LiveTime',
            'RunNumber',
            'Weight',
            'eventWeightVar',
            'eventWeightBranch',
            'tags',
            'description',
            'extraMetaInformation',
            'analyses',
            'resultTObjects',
            'results',
            'Statistics',
            'SimpleCutFlow',
            ]

        self.reg_stat_algos = {}
        
        self.__pathToPickleFile = '' # path to pickle file, can be useful for loading ntuples



    def Clone(self,**Dic ):
        """
        This is a Generic Clone Function
        """
        nS=Sample(self.name)

        # Copy All Attributes
        for obj in self.__dict__: 
            if Dic.has_key(obj):
                nS.__dict__[obj]=Dic[obj]
            else:
                nS.__dict__[obj]=self.__dict__[obj]

        NewChain=TChain(nS.Dir)

        for file in nS.Files:
            NewChain.AddFile(file)

        nS.Chain=NewChain

        return nS
        

    def Print(self, opt=''):
        """
        print information about this object

        opt contains 'v' : verbose mode = opt('crs')
        opt contains 'c' : print chain
        opt contains 'r' : print sample results
        opt contains 's' : print sample statistics
        """
        print "---  Print()"
        #theStr = self.__baseStr__()
        #print theStr
        if opt.find('v') != -1 : opt = 'crs'
        
        for v in self.listPickleVars:
            if v == 'Statistics' or v == 'results': continue
            print "  - %s : %s" % (v, eval("self."+v))
            pass
        if opt.find("r")!=-1:
            print "  - results : %s\n" % ( self.results )
            pass
        if opt.find("s")!=-1:
            print "  - statistics : %s\n" % ( self.Statistics )
            pass
        if opt.find("c")!=-1:
            print "  - Chain.Entries : ", self.Chain.GetEntries()
            print "-------------------------------------------"
            self.Chain.GetListOfLeaves().Print()
            pass
        pass

    def PrintChainSize(self,req=''):
        l = {}
        totsize = 0.
        tree = self.Chain
        for leave in tree.GetListOfLeaves():
            l[ leave.GetTitle() ] = leave.GetBranch().GetZipBytes()
            totsize += leave.GetBranch().GetZipBytes()
            pass
        # sort by size
        import operator
        sorted_x = sorted(l.iteritems(), key=operator.itemgetter(1))
        #return sorted_x
        tot_sel = 0.
        for s in sorted_x:
            if req=='' or s[0].find(req)!=-1:
                print '50%i (%2.2f%%): %s' % (s[1], (s[1]/totsize*100.), s[0])
                tot_sel += s[1]
                pass
            pass
        print '----------'
        print '50%i (%2.2f%%): require %s' % (tot_sel, (tot_sel/totsize*100.), req)
        pass


    def Leaves(self,filter=''):
        leaves=self.Chain.GetListOfLeaves()
        categories={}
        baseleaves=[]
        topList=([],{})
        print 'Variables in ntuple:'

        def addLeave(myList,name):
            cat,sep,var=name.partition('_')
            if sep:
                if not cat in myList[1]:
                    myList[1][cat]=([],{})
                addLeave(myList[1][cat],var)
            else:
                myList[0].append(name)

        for leave in leaves:
            name=leave.GetName()
            if name.find(filter)==-1: continue
            addLeave(topList,name)

        def printList(myList,prefix=''):
            if prefix.startswith('_'):
                prefix=prefix[1:]
            
            leaves=myList[0]
            myBranches=myList[1].keys()[:]
            for branch in myList[1].keys():
                if len(myList[1][branch][0])==1 and not myList[1][branch][1]:
                    myBranches.remove(branch)
                    leaves.append(branch+'_'+myList[1][branch][0][0])
            myBranches.sort()
            leaves.sort()
            if leaves:
                if prefix:
                    print ' ',prefix+'_ :',' '.join(leaves)
                else:
                    print ' ','\n  '.join(leaves)
            for branch in myBranches:
                printList(myList[1][branch],prefix+'_'+branch)

        printList(topList)
        
    def GetXSection(self):
        return self.XSection

    def GetLumi(self):
        return self.Lumi

    def GetWeight(self):
        return self.Weight

    def GetStatistics(self):
        return self.__fStats

    def AddFriendSample(self, friendSample):
        self.Chain.AddFriend( friendSample.Dir )
        return True

    def GetEntries(self):
        return self.Chain.GetEntries()

    def EnableProof(self):
        pass

    def DisableProof(self):
        pass


    def SetCutFlow( mode ):
        if self.SimpleCutFlow:
            print "Error, this Sample object was created in simpleStatMode!"
            return
            
        try:
            self.__fStats = self.Statistics[ mode ]
        except KeyError:
            print "Warning, cannot find stat mode",mode
            pass
        pass


    def GetWeightedEntries(self):
        """
        Return the sum over all event weights.
        If eventWeightVar is not given to this Sample,
        simply return the TChain.GetEntries()
        Note, for the TFileStager chain, GetEntries is not working (simply returns max INT)
        ==> we do something different here.
        """
        hist=TH1F('hist','hist',1,0,2)
        entries = self.Chain.Project("hist","1",self.eventWeightVar)
        weight=hist.GetBinContent(1)
        hist.Delete()
        return weight

    def ResetSampleWeight(self):
        """
        Reset Sample Weight by doing one of the following:
        1) if cross-section <= 0 : Weight = 1
        2) if cross-section > 0 AND genEvents > 0  : Weight = cross-section / genEvents
        3) if cross-section > 0 AND genEvents <= 0 :
           a) Re-calculate genEvents from ntuple(s) via GetWeightedEntries()
           b) then Weight = cross-section / genEvents
        """
        print "Re-Calculate Sample Weight !"
        if self.XSection <= 0   :
            print "No cross-section given ==> assume it's Data with Weight of 1"
            newWeight = 1.0
        elif self.genEvents > 0 :
            print "Cross-section and genEvents given ==> assume it's MC with Weight of cross-section / genEvents"
            newWeight = float(self.XSection) / float(self.genEvents)
        else :
            print "Cross-section given ==> assume it's MC with Weight of cross-section / genEvents"
            newGenEvents = self.GetWeightedEntries()
            print "calculated (weighted) ntuple entries to be",newGenEvents
            self.genEvents = newGenEvents
            newWeight = float(self.XSection) / float(self.genEvents)
            pass
        print "Setting Weight to",newWeight
        self.Weight = newWeight
        return self.Weight


    def GetExpectedEvents(self, luminosity, useCrossSection = False):
        """
        Return the expected number of events for the given luminosity.

        approach 1)

           exp_evts = sample_entries * sample_weight  * luminosity

           here, sample_entries is the sum over the remaining
           event weights (after given event selection),
           sample_weight is assumed to be
           1 / (integrated data luminosity) or x-section / MC_events.

        approach 2)  [if useCrossSection = True]

           exp_evts = cross-section * cut_eff * luminosity

           here, cross-section is associated to the sample
           whose event selection efficiency is the given
           cut_eff
        """

        if useCrossSection:
            return self.GetXSection() * self.GetCutEff() * luminosity
        else:
            return self.GetWeightedEntries() * self.GetWeight() * luminosity


    def initChain(self):
        return True

    ##################################
    ##     Ntuple File methods      ##

    def AddFiles(self, files = [], XSection=-1, AddToChainOnly=False, ):
        # set x-section
        if XSection > 0:
            self.XSection=XSection

        # add files
        for myFile in files:
            #print "adding file %s" % myFile
            if not AddToChainOnly:
                # avoid adding files several times
                if myFile in self.Files:
                    continue
                self.Files+=[myFile]
                pass
            if myFile.find('/castor/')!=-1 or path.isfile( myFile ) or myFile.find('root:')!=-1:
                self.Chain.AddFile( myFile )
            elif path.isfile( "%s/%s" % (self.__pathToPickleFile, myFile) ) or  path.islink( "%s/%s" % (self.__pathToPickleFile, myFile) ) :
                # try to add the path of the pickle file
                self.Chain.AddFile( "%s/%s" % (self.__pathToPickleFile, myFile) )
            else:
                print "ERROR adding file: %s (file not existing, check path!)" % myFile
                pass
            pass
        return True

    def AddFilesToChain(self):
        self.Chain=TChain(self.Dir)
        self.AddFiles(self.Files, AddToChainOnly=True)

    def AddDirectory(self, path, require="", XSection=-1,XRD=False,prepend="",XRDHack=None):
        self.XSection=XSection

        if path[-1] != '/':
            path += '/'

        if XRD:
            lsCommand="xrdls"
        else:
            lsCommand="ls"

        if not XRDHack:
            if require == "":
                fileNames = popen(lsCommand+' %s' %(path)).readlines()
            else:
                fileNames = popen(lsCommand+' %s | grep -E %s' %(path,require)).readlines()
        else:
            fileNames=self.MultiLS(path,require,XRDHack)

#        print path,fileNames

        fileNames.sort()

        fullFileNames = []
        for file in fileNames:
            # print "Adding: ", file
            #self.AddFile(path+file[0:-1])
            if not XRDHack:
                fullFileNames += [ prepend+path+file[0:-1] ]
            else:
                fullFileNames += [ file[0:-1] ]
        self.AddFiles(fullFileNames)

    def MultiLS(self, APath, require, Paths=["/Volumes/DataA_1/xrd",
                                             "/Volumes/DataA_2/xrd",
                                             "/Volumes/DataL_1/xrd",
                                             "/Volumes/DataL_2/xrd",
                                             "/Volumes/DataT_1/xrd"]):
        res=[]
        for Path in Paths:
            if require == "":
                fileNames = popen('ls %s 2>&1 | cat' %(Path+"/"+APath)).readlines()
            else:
                fileNames = popen('ls %s 2>&1 | grep -E %s' %(Path+"/"+APath,require)).readlines()
            for AFile in fileNames:
                if AFile.find("No such file or directory")==-1:
                    res+=[ Path+"/"+APath+"/"+AFile]

        return res

    def AddDirectoryXRD(self, path, require="", XSection=-1,prepend="", LocalDiskHack=None):
        self.XSection=XSection

        if path[-1] != '/':
            path += '/'

        if not LocalDiskHack:
            if require == "":
                fileNames = popen('xrdls %s' %(path)).readlines()
            else:
                fileNames = popen('xrdls %s | grep -E %s' %(path,require)).readlines()
        else:
            filesNames=self.MultiLS(path,LocalDiskHack,require)


        fileNames.sort()

        fullFileNames = []
        for file in fileNames:
            # print "Adding: ", file
            #self.AddFile(path+file[0:-1])
            if not Hack:
                fullFileNames += [ prepend+path+file[0:-1] ]
            else:
                fullFileNames += [ path+file[0:-1] ]
        self.AddFiles(fullFileNames)


    def ChangeNtupleDir(self, newDirectory):

        newFiles = []
        for f in self.Files:
            tmp = f.rsplit("/",1)
            newFiles += [ newDirectory + "/" + tmp[-1] ]

        self.Files = newFiles


    def CloneTree(self, evts=0):
        return self.Chain.GetTree().CloneTree(evts)


    ##################################
    ##        TTree Draw methods    ##

    def Draw(self, expression, cut="1", opts="",
             bins=100, min=0, max=1000, HistName="Hist",Norm=1000.0, maxLumi=-1, DoDraw=True,
             title="", UseEventWeight=True, defaultSystematic=0.0, systematics={},
             DontAllowNegativeBins=False, UseSampleWeight=True):
        """
        Samples's Draw method to draw any TTree variable of this sample.

        maxLumi: if you want to plot only a sub-sample of the dataset, use this option
                 Note that if maxLumi > 0, then Norm is set to be -1 (ie. histogram is NOT normalized)

                 maxLumi = -1 : run over full sample, apply normalization Norm
                 maxLumi > 0  : run over sub-sample, do not normalize histogram 

        """

        eventWeight = "1"
        if UseEventWeight and self.eventWeightVar != '' :
            eventWeight = self.eventWeightVar

        Nentries = TChain.kBigNumber #self.GetWeightedEntries()
        if maxLumi > 0 and self.GetExpectedEvents(maxLumi)< self.GetWeightedEntries() :
            Nentries = int(self.GetExpectedEvents(maxLumi))
            Norm = -1
            
        hist=TH1F("htemp", expression+" "+cut, bins, min, max)
        hist.Sumw2()
        if self.Chain.Project("htemp",expression,"("+eventWeight+")*"+cut,opts, Nentries) == 0:
#            print "WARNING, 0 entries in hist : %s" % hist.GetTitle()
            return

        if hist.GetEffectiveEntries() == 0:
#            print "WARNING, 0 entries in hist : %s" % hist.GetTitle()
            return

        self.NormalizeHist(hist,Norm,UseSampleWeight)


        # set systematic error to use
        sys = defaultSystematic
        if systematics.has_key( self.name ):
            sys = systematics[ self.name ] # use this one instead
        # add the systematic error to the existing error per bin
        if sys != 0.0:
            # debugging msg
            print "adding systematics %1.2f on top of MC stats errors for sample %s" % (sys, self.name)
            for bin in range(hist.GetNbinsX()):
                # bins start with 1, not 0 !
                error = hist.GetBinError(bin+1)
                content = hist.GetBinContent(bin+1)
                new_error = sqrt(error**2 + (sys*content)**2)
                hist.SetBinError(bin+1, new_error)

        hist.SetName(HistName)
        if title!="":
            hist.SetTitle(title)


        # set bins with negative content to 0.0
        if DontAllowNegativeBins:
            for bin in range(hist.GetNbinsX()):
                if hist.GetBinContent(bin+1) < 0.0:
                    hist.SetBinContent(bin+1, 0.0)

        if DoDraw:
            hist.Draw()
        return hist


    ##################################
    ##        TTree Draw methods    ##

    def Draw2D(self, expression, cut="1", opts="",
               xbins=100, xmin=0, xmax=1000, ybins=100, ymin=0, ymax=1000,
               HistName="Hist",Norm=1000.0, maxLumi=-1, DoDraw=True,
               title="", UseEventWeight=True,
               UseSampleWeight=True):
        """
        Samples's 2dim Draw method to draw any TTree variable of this sample.

        """

        eventWeight = "1"
        if UseEventWeight and self.eventWeightVar != '' :
            eventWeight = self.eventWeightVar

        Nentries = TChain.kBigNumber #self.GetWeightedEntries()
        if maxLumi > 0 and self.GetExpectedEvents(maxLumi)< self.GetWeightedEntries() :
            Nentries = int(self.GetExpectedEvents(maxLumi))
            Norm = -1

        hist=TH2F("htemp", expression+" "+cut, xbins, xmin, xmax, ybins, ymin, ymax)
        hist.Sumw2()
        if self.Chain.Project("htemp",expression,"("+eventWeight+")*"+cut,opts, Nentries) == 0:
#            print "WARNING, 0 entries in hist : %s" % hist.GetTitle()
            return

        if hist.GetEffectiveEntries() == 0:
#            print "WARNING, 0 entries in hist : %s" % hist.GetTitle()
            return

        self.NormalizeHist(hist,Norm,UseSampleWeight)

        hist.SetName(HistName)
        if title!="":
            hist.SetTitle(title)


        if DoDraw:
            hist.Draw()
        return hist


    def Draw2D_UB(self, expression, xbinArray, ybinArray, cut="1", opts="",
               xbins=100, ybins=100, zbins=100,
               HistName="Hist",Norm=1000.0, maxLumi=-1, DoDraw=True,
               title="", UseEventWeight=True,
               UseSampleWeight=True):
        """
        Samples's 2dim Draw method to draw any TTree variable of this sample.

        """
        Xmy_bins = array('d',xbinArray )
        Ymy_bins = array('d',ybinArray )

        eventWeight = "1"
        if UseEventWeight and self.eventWeightVar != '' :
            eventWeight = self.eventWeightVar

        Nentries = TChain.kBigNumber #self.GetWeightedEntries()
        if maxLumi > 0 and self.GetExpectedEvents(maxLumi)< self.GetWeightedEntries() :
            Nentries = int(self.GetExpectedEvents(maxLumi))
            Norm = -1

        hist=TH2F("htemp", expression+" "+cut, xbins, Xmy_bins, ybins, Ymy_bins)
        hist.Sumw2()
        if self.Chain.Project("htemp",expression,"("+eventWeight+")*"+cut,opts, Nentries) == 0:
#            print "WARNING, 0 entries in hist : %s" % hist.GetTitle()
            return

        if hist.GetEffectiveEntries() == 0:
#            print "WARNING, 0 entries in hist : %s" % hist.GetTitle()
            return

        self.NormalizeHist(hist,Norm,UseSampleWeight)

        hist.SetName(HistName)
        if title!="":
            hist.SetTitle(title)


        if DoDraw:
            hist.Draw()
        return hist


    def Profile(self, expression, cut="1", opts="",
                ybins=100, ymin=0, ymax=1000, xbins=100, xmin=0, xmax=1000,
                HistName="Hist", DoDraw=True,
                title="", UseEventWeight=True,
                UseSampleWeight=True,
                MinEntries=10.):
        """
        Profile...

        """

        eventWeight = "1"
        if UseEventWeight and self.eventWeightVar != '' :
            eventWeight = self.eventWeightVar


        hist=TH2F("htemp", expression+" "+cut, xbins, xmin, xmax, ybins, ymin, ymax)
        hist.Sumw2()

        if self.Chain.Project("htemp",expression,"("+eventWeight+")*"+cut) == 0:
            print "WARNING, 0 entries in hist : %s" % hist.GetTitle()
            return


        if hist.GetEffectiveEntries() == 0:
            print "WARNING, 0 entries in hist : %s" % hist.GetTitle()
            return

        hists=[]

        mean=TH1F(HistName+"_mean_fit","Mean "+expression+" "+cut,xbins,xmin,xmax)
        rms=TH1F(HistName+"_rms_fit","RMS "+expression+" "+cut,xbins,xmin,xmax)
        meanfit=TH1F(HistName+"_mean_fit","Fitted Mean "+expression+" "+cut,xbins,xmin,xmax)
        sigmafit=TH1F(HistName+"_sigma_fit","Fitted Sigma "+expression+" "+cut,xbins,xmin,xmax)

        for yb in xrange(0,ybins):
            h=hist.ProjectionY(HistName+"_Project_"+str(yb),yb,yb)
            #h=TH1F("htemp"+str(yb),expression+" "+cut,ybins,ymin,ymax)
            # for xb in xrange(0,xbins):
            #     C=hist.GetBinContent(yb,xb)
            #     E=hist.GetBinError(yb,xb)
                
            #     h.SetBinContent(xb,C)
            #     h.SetBinError(yb,E)

            if h:
                hists+=[h]

                if h.GetEntries()>MinEntries:
                    mean.SetBinContent(yb,h.GetMean())
                    mean.SetBinError(yb,h.GetMeanError())
            
                    rms.SetBinContent(yb,h.GetRMS())
                    rms.SetBinError(yb,h.GetRMSError())

                    Res=h.Fit("gaus","SqN")

                    if Res.Get(): #Store only good fits
                        meanfit.SetBinContent(yb,Res.Get().GetParams()[1])
                        meanfit.SetBinError(yb,Res.Get().GetErrors()[1])
                        sigmafit.SetBinContent(yb,Res.Get().GetParams()[2])
                        sigmafit.SetBinError(yb,Res.Get().GetErrors()[2])


        if title!="":
            hist.SetTitle(title)

        if DoDraw:
            c1=TCanvas("c1")
            c1.Divide(2,2)
            c1.cd(1)
            mean.Draw()
            c1.cd(2)
            rms.Draw()
            c1.cd(3)
            meanfit.Draw()
            c1.cd(4)
            sigmafit.Draw()
            return [mean,rms,meanfit,sigmafit,hist,hists,c1]

        return [mean,rms,meanfit,sigmafit,hist,hists]


    def Draw2D_UB(self, expression, xbinArray, ybinArray, cut="1", opts="",
               xbins=100, ybins=100, zbins=100,
               HistName="Hist",Norm=1000.0, maxLumi=-1, DoDraw=True,
               title="", UseEventWeight=True,
               UseSampleWeight=True):
        """
        Samples's 2dim Draw method to draw any TTree variable of this sample.

        """
        Xmy_bins = array('d',xbinArray )
        Ymy_bins = array('d',ybinArray )

        eventWeight = "1"
        if UseEventWeight and self.eventWeightVar != '' :
            eventWeight = self.eventWeightVar

        Nentries = TChain.kBigNumber #self.GetWeightedEntries()
        if maxLumi > 0 and self.GetExpectedEvents(maxLumi)< self.GetWeightedEntries() :
            Nentries = int(self.GetExpectedEvents(maxLumi))
            Norm = -1

        hist=TH2F("htemp", expression+" "+cut, xbins, Xmy_bins, ybins, Ymy_bins)
        hist.Sumw2()
        if self.Chain.Project("htemp",expression,"("+eventWeight+")*"+cut,opts, Nentries) == 0:
#            print "WARNING, 0 entries in hist : %s" % hist.GetTitle()
            return

        if hist.GetEffectiveEntries() == 0:
#            print "WARNING, 0 entries in hist : %s" % hist.GetTitle()
            return

        self.NormalizeHist(hist,Norm,UseSampleWeight)

        hist.SetName(HistName)
        if title!="":
            hist.SetTitle(title)


        if DoDraw:
            hist.Draw()
        return hist


    def Draw3D(self, expression, cut="1", opts="",
               xbins=100, xmin=0, xmax=1000, ybins=100, ymin=0, ymax=1000, zbins=100, zmin=0, zmax=1000,
               HistName="Hist",Norm=1000.0, maxLumi=-1, DoDraw=True,
               title="", UseEventWeight=True,
               UseSampleWeight=True):
        """
        Samples's 3dim Draw method to draw any TTree variable of this sample.

        """

        eventWeight = "1"
        if UseEventWeight and self.eventWeightVar != '' :
            eventWeight = self.eventWeightVar

        Nentries = TChain.kBigNumber #self.GetWeightedEntries()
        if maxLumi > 0 and self.GetExpectedEvents(maxLumi)< self.GetWeightedEntries() :
            Nentries = int(self.GetExpectedEvents(maxLumi))
            Norm = -1

        hist=TH3F("htemp", expression+" "+cut, xbins, xmin, xmax, ybins, ymin, ymax, zbins, zmin, zmax)
        hist.Sumw2()
        if self.Chain.Project("htemp",expression,"("+eventWeight+")*"+cut,opts, Nentries) == 0:
#            print "WARNING, 0 entries in hist : %s" % hist.GetTitle()
            return

        if hist.GetEffectiveEntries() == 0:
#            print "WARNING, 0 entries in hist : %s" % hist.GetTitle()
            return

        self.NormalizeHist(hist,Norm,UseSampleWeight)

        hist.SetName(HistName)
        if title!="":
            hist.SetTitle(title)


        if DoDraw:
            hist.Draw()
        return hist


# Options for histogram with unequal bin size

    def Draw3D_UB(self, expression, xbinArray, ybinArray, zbinArray, cut="1", opts="",
               xbins=100, ybins=100, zbins=100,
               HistName="Hist",Norm=1000.0, maxLumi=-1, DoDraw=True,
               title="", UseEventWeight=True,
               UseSampleWeight=True):
        """
        Samples's 3dim Draw method to draw any TTree variable of this sample.

        """
        Xmy_bins = array('d',xbinArray )
        Ymy_bins = array('d',ybinArray )
        Zmy_bins = array('d',zbinArray )

        eventWeight = "1"
        if UseEventWeight and self.eventWeightVar != '' :
            eventWeight = self.eventWeightVar

        Nentries = TChain.kBigNumber #self.GetWeightedEntries()
        if maxLumi > 0 and self.GetExpectedEvents(maxLumi)< self.GetWeightedEntries() :
            Nentries = int(self.GetExpectedEvents(maxLumi))
            Norm = -1

        hist=TH3F("htemp", expression+" "+cut, xbins, Xmy_bins, ybins, Ymy_bins, zbins, Zmy_bins)
        hist.Sumw2()
        if self.Chain.Project("htemp",expression,"("+eventWeight+")*"+cut,opts, Nentries) == 0:
#            print "WARNING, 0 entries in hist : %s" % hist.GetTitle()
            return

        if hist.GetEffectiveEntries() == 0:
#            print "WARNING, 0 entries in hist : %s" % hist.GetTitle()
            return

        self.NormalizeHist(hist,Norm,UseSampleWeight)

        hist.SetName(HistName)
        if title!="":
            hist.SetTitle(title)


        if DoDraw:
            hist.Draw()
        return hist



    def Project(self,HistName,expression,cut="1",opts=""):
        self.Chain.Project(HistName,expression,cut,opts)

    def NormalizeHist(self,hist,Norm,UseSampleWeight=True):
        """
        Normalize (scaling) histogram to have an area = sample weight * Norm
        unless
        *  Norm == 0  -> set area to 1.0
        *  Norm <  0  -> do nothing
        """
        if Norm==0:
            hist.Scale( 1./hist.Integral() )
            return

        if Norm<0:
            return

        if not UseSampleWeight:
            cutEff = self.GetCutEff()
            hist.Scale( Norm*cutEff*float(self.XSection) )
            return

        hist.Scale( self.GetWeight() * Norm )


    #####################################
    ##  copy obj, write/read to disk   ##

    def unpickle(self, fileName = '', quiet=False):
        """
        Unpickle (load) a Sample class from disk into memory.
        Use Scott's python add-on to handle ROOT stuff as well.

        fileName             : pickled file (path + file name)
        quite                : print debug messages ?
        ntupleFilesInSameDir : the ntuple files and pickle files are assumed to be in the same directory.
                               This option will cut off any ntuple directory information in the pickled files --> avoids problems
        """ 

        # call base class' unpickle:
        SObject.unpickle( self, fileName, quiet)

        # remember path to pickle file (can be used to load ntuples)
        self.__pathToPickleFile = path.dirname( fileName )

        self.__fStats = self.Statistics
       
        # add files to TChain:
        self.AddFilesToChain()
        pass


    def Copy(self, otherObj):
        """
        Copy given otherObj Sample object on this Sample obj.
        """
        # copy stuff
        for v in self.listPickleVars:
            #print "copying variable: %s" % v
            if v.find("resultTObjects")!=-1:
                for hist in otherObj.resultTObjects:
                    gROOT.cd("/")
                    self.resultTObjects[hist] = otherObj.resultTObjects[hist].Clone()
            else:
                try:
                    exec("self."+v+" = deepcopy(otherObj."+v+")")
                except AttributeError:
                    print "WARNING : this class has no variables with the name: %s  --> go on w/o setting this variable" % (v)
                except KeyError:
                    print "WARNING : variable '%s' not found in the object from which we copy --> go on w/o setting this variable" % (v)
        #
        # remember path to pickle file (can be used to load ntuples)
        self.__pathToPickleFile = otherObj.__pathToPickleFile
        #
        if self.SimpleCutFlow:
            self.__fStats = self.Statistics
            pass
        pass


    #####################################
    ##  Stats of Algorithms            ##

    def RegisterStatsAlgo(self, name, CutFlows=["Default"]):
        if self.SimpleCutFlow:
            if not name: return True
            # we want a unique algorithm name!
            if self.reg_stat_algos.has_key(name):
                print "ERROR: an algorithm named %s is already registerd!" % name
                return False

            sub_name = name
            # see whether an algorithm with the same name has added stats before
            if self.Statistics.has_key( name):
                # if so, change name until it's ok
                while self.Statistics.has_key(sub_name):
                    sub_name += '_'
                print "WARNING: an algorithm named %s was run before, going to modify name to %s (for key in Statistics)" % (name, sub_name)
            self.reg_stat_algos[name] = sub_name
            # create an empty statistics entry for sub_name
            self.Statistics[ sub_name ] = [0, 0, 0.0, 0.0]
            # save order of algorithms
            if not self.results.has_key( 'Statistics_listOfNames' ) : self.results[ 'Statistics_listOfNames' ] = []
            self.results[ 'Statistics_listOfNames' ].append( sub_name )
            return True
        else:
            # we want a unique algorithm name!
            if self.reg_stat_algos.has_key(name):
                print "ERROR: an algorithm named %s is already registerd!" % name
                return False

            for CutFlow in CutFlows:
                if not self.Statistics.has_key(CutFlow):
                    self.Statistics[CutFlow]={}
                sub_name = name
                # see whether an algorithm with the same name has added stats before
                if self.Statistics[CutFlow].has_key( name):
                    # if so, change name until it's ok
                    while self.Statistics[CutFlow].has_key(sub_name):
                        sub_name += '_'+CutFlow
                    print "WARNING: an algorithm named %s was run before, going to modify name to %s (for key in Statistics)" % (name, sub_name)
                self.reg_stat_algos[name] = sub_name
                # create an empty statistics entry for sub_name
                self.Statistics[CutFlow][ sub_name ] = [0, 0, 0.0, 0.0]
                # save order of algorithms
                if not self.results.has_key( 'Statistics_listOfNames' ) : 
                    self.results[ 'Statistics_listOfNames' ] = {CutFlow: []}
                else:
                    if not self.results[ 'Statistics_listOfNames' ].has_key(CutFlow):
                        self.results[ 'Statistics_listOfNames' ][CutFlow]=[]                    
                self.results[ 'Statistics_listOfNames' ][CutFlow].append( sub_name )
                pass
            return True
        pass


    def UnsubscribeStatsAlgo(self, name):
        # remove entry
        if not name: return True
        try:
            self.reg_stat_algos.pop(name)
        except KeyError:
            print "WARNING: could not unsubscribe algorithm named %s since it was never registered!" % name
            return False
        return True


    def AddStatsBeforeAlgo(self, algoName, weight,CutFlows=["Default"]):
        """
        Method to be called by an algorithm _before_ the algorithm's execute.
        this way, we can store how many times (events*eventWeight) the algorithm's
        execute was called.

        data is stored in self.Statistics, which's internal structure is:
        {cutflowname: {algoName : [evtsBefore, evtsAfter, weightedEvtsBefore, weightedEvtsAfter], ... }}
        """

        if not algoName: return True
        # get statistics key for algorithm name
        if not self.reg_stat_algos.has_key(algoName):
            print "ERROR: algorithm named %s was never registered!" % algoName
            return False

        key = self.reg_stat_algos[algoName]

        if self.SimpleCutFlow:
            self.Statistics[ key ] [0] += 1
            self.Statistics[ key ] [2] += weight
        else:
            for CutFlow in CutFlows:
                self.Statistics[CutFlow][ key ] [0] += 1
                self.Statistics[CutFlow][ key ] [2] += weight
                pass
            pass
        return True

    def AddStatsAfterAlgo(self, algoName, weight,CutFlows=["Default"]):
        """
        As in AddStatsBeforeAlgo(self, algoName, weight), but this method
        saves the times of a successfull algorithm filter + execution.
        """
        if not algoName: return True
        # get statistics key for algorithm name
        if not self.reg_stat_algos.has_key(algoName):
            print "ERROR: algorithm named %s was never registered!" % algoName
            return False
        key = self.reg_stat_algos[algoName]

        if self.SimpleCutFlow:
            self.Statistics[ key ] [1] += 1
            self.Statistics[ key ] [3] += weight
        else:
            for CutFlow in CutFlows:
                self.Statistics[CutFlow][ key ] [1] += 1
                self.Statistics[CutFlow][ key ] [3] += weight
                pass
            pass
        
        return True

    def CheckStatisticsConsistency(self):
        """
        Perform a self-check :
        * the output number of events of algorithm N should be identical to the input number of algorithm N+1
        returns True if everything is correct, otherwise False
        """

        if not self.results.has_key('Statistics_listOfNames') :
            print "cannot perform check because order of statistics cannot be found, old sample?"
            return True

        TheStats = self.results['Statistics_listOfNames']
        evtsIn = self.genEvents        
               
        for alg in TheStats:
            if evtsIn != self.__fStats[alg][0]:
                print self.name,"WARNING: found inconsistency in statistics for algorithm",alg
                return False
            evtsIn = self.__fStats[alg][1]
            pass
        
        return True

    def GetCutEffNumbers(self, algoName="", UseEventWeight = True, applyAllPreviousCuts=True):
        """
        Retrieve efficiency of a given algorithm or in
        case of algoName = '' or 'all' all applied algorithms.

        By default the weighted events are used for the eff.
        If, however, useEventWeight == False, then the pure
        TTree evts_out / evts_in is returned !

        This method also returns the (weighted) evt numbers before/after the cut, ie
        return : [eff, evts_in, evts_out]
        """
        indexIn  = 0
        indexOut = 1
        if UseEventWeight:
            indexIn  = 2
            indexOut = 3

        evts_in  = -1
        evts_out = -1

        # no algoName given, loop over all
        if algoName=="" or algoName.lower()=="all":
            for S in self.__fStats:
                if self.__fStats[S][indexIn] > evts_in:
                    evts_in = self.__fStats[S][indexIn]
                if self.__fStats[S][indexOut] < evts_out or evts_out == -1:
                    evts_out = self.__fStats[S][indexOut]

        else:
            # an algoName is given
            try:
                evts_in  = self.__fStats[algoName][indexIn]
                evts_out = self.__fStats[algoName][indexOut]
            except KeyError:
                print "ERROR: algoName %s not stored in Statistics ... " % algoName
                return [None, None, None]


        if applyAllPreviousCuts:
            # find highest evt number:
            maxEvt = 0
            for S in self.__fStats:
                if self.__fStats[S][indexIn] > maxEvt:
                    maxEvt = self.__fStats[S][indexIn]

            evts_in = maxEvt


        if evts_in > 0:
            eff = float(evts_out) / float(evts_in)
        else:
            eff = None

        return [ eff, evts_in, evts_out ]




    def GetCutEff(self, algoName="", UseEventWeight = True, applyAllPreviousCuts=True):
        """
        Retrieve efficiency of a given algorithm or in
        case of algoName = '' or 'all' all applied algorithms.

        By default the weighted events are used for the eff.
        If, however, useEventWeight == False, then the pure
        TTree evts_out / evts_in is returned !
        """
        eff = self.GetCutEffNumbers(algoName=algoName, UseEventWeight=UseEventWeight, applyAllPreviousCuts=applyAllPreviousCuts) [0]

        if eff is not None:
            return eff
        else:
            return 0.0

    def GetCutEffErr(self, algoName="", UseEventWeight = True, applyAllPreviousCuts=True):
        """
        Retrieve error for efficiency of a given algorithm or in
        case of algoName = '' or 'all' all applied algorithms.

        By default the weighted events are used for the eff.
        If, however, useEventWeight == False, then the pure
        TTree evts_out / evts_in is returned !
        """
        res = self.GetCutEffNumbers(algoName=algoName, UseEventWeight=UseEventWeight, applyAllPreviousCuts=applyAllPreviousCuts)
        eff     = res[0]
        evts_in = res[1]
        if eff is not None:
            return sqrt(eff*(1.0-eff)/evts_in)
        else:
            return 0.0

    def GetTTreeCutEffNumbers(self, cut, UseEventWeight = True, maxEntries=-1, applyAllPreviousCuts=True):
        """
        Figure out efficiency for given cut.
        if UseEventWeight is True and this Sample has an eventWeight, take it into account !

        This method also returns the (weighted) evt numbers before/after the cut, ie
        return : [eff, evts_in, evts_out]
        """

        indexIn  = 0
        indexOut = 1
        if UseEventWeight:
            indexIn  = 2
            indexOut = 3

        ew = False
        if UseEventWeight and self.eventWeightVar != '' :
            ew = True

        # get rid of spaces
        cut = cut.replace(" ", "")

        if cut.find(">") != -1:
            draw = cut.split(">")[0]
        elif cut.find("<") != -1:
            draw = cut.split("<")[0]
        elif cut.find("==") != -1:
            draw = cut.split("==")[0]
        else:
            print "ERROR, cut does not contain '<', '>', or '==' ?!?"
            return [None, None, None]

        #Data.Samples[sample].Chain.Draw(draw+ ">>h1", eventWeight+" * (1)")
        #Data.Samples[sample].Chain.Draw(draw+ ">>h1_cut", eventWeight+" * ("+cut+")")
        #allEntries = h1.Integral()
        #entries    = h1_cut.Integral()
        # problem when calling this method from inside other method -> h1, h1_cut are not re-created !!!!

        allEntries = 0.0
        entries    = 0.0

        # get TTree and activate needed branches:
        ch = self.Chain
        if maxEntries == -1:
            Nentries = ch.GetEntries()
        else:
            Nentries = maxEntries

        ch.SetBranchStatus("*", 0)
        ch.SetBranchStatus(draw, 1)
        if ew:
            ch.SetBranchStatus(self.eventWeightBranch, 1)

        for i in range(Nentries):
            ch.GetEntry(i)

            weight = 1.0
            if ew:
                weight = eval("ch."+self.eventWeightVar)

            allEntries += weight

            # cut passed ?
            if eval("ch."+cut):
                entries += weight
                # print "Passed, value = %f" % (eval("ch."+draw))

        if applyAllPreviousCuts:
            # find highest evt number:
            maxEvt = 0
            for S in self.Statistics:
                if self.Statistics[S][indexIn] > maxEvt:
                    maxEvt = self.Statistics[S][indexIn]

            allEntries = maxEvt

        if allEntries > 0:
            eff = float(entries) / float(allEntries)
        else:
            eff = None

        ch.SetBranchStatus("*", 1)
        return [ eff, allEntries, entries ]


    def GetTTreeCutEff(self, cut, UseEventWeight = True, maxEntries=-1, applyAllPreviousCuts=True):
        """
        Retrieve efficiency of a given cut

        By default the weighted events are used for the eff.
        If, however, useEventWeight == False, then the pure
        TTree evts_out / evts_in is returned !
        """
        eff = self.GetTTreeCutEffNumbers(cut=cut, UseEventWeight=UseEventWeight, maxEntries=maxEntries, applyAllPreviousCuts=applyAllPreviousCuts ) [0]

        if eff is not None:
            return eff
        else:
            return 0.0
        pass

    def GetTTreeCutEffErr(self, cut, UseEventWeight = True, maxEntries=-1, applyAllPreviousCuts=True ):

        numbers = self.GetTTreeCutEffNumbers(cut=cut, UseEventWeight=UseEventWeight, applyAllPreviousCuts=applyAllPreviousCuts )
        eff = numbers[0]
        evts_in = numbers[1]
        if evts_in == 0: return None
        return sqrt(eff*(1.0-eff)/evts_in)
    

    def PrintCutEff(self, require='', cutNames=[], UseEventWeight=True, applyAllPreviousCuts=True, printEff=True):

        indexIn  = 0
        indexOut = 1
        if UseEventWeight:
            indexIn  = 2
            indexOut = 3


        def StatsCmp(x,y):
            # first try evts out
            xN=x[1]
            yN=y[1]
            if int(yN == xN):
                # 2nd, try evts in
                xN2=x[2] 
                yN2=y[2]
                if int(yN2 == xN2):
                    return 0
                if int(yN2 > xN2):
                    return 1
                else:
                    return -1
            if int(yN > xN):
                return 1
            else:
                return -1

        TheStats = self.GetStatistics()

        # try to use ordered list of algorithms (if existing)
        if self.results.has_key('Statistics_listOfNames') : TheStats = self.results['Statistics_listOfNames']
        
        TheCutAlgs = []
        if len(cutNames)==0: # no list of algorithm given, make ordering here
            for alg in TheStats:
                if (require == "" or alg.find(require)!=-1 ) :
                    res = self.GetCutEffNumbers(algoName=alg,
                                                UseEventWeight=UseEventWeight,
                                                applyAllPreviousCuts=False) # do ordering using both input and output evts (!)
                    TheCutAlgs += [ [alg, res[2], res[1] ] ]
                    pass
                pass
            TheCutAlgs.sort(StatsCmp)
            pass
        else: # we use pre-defined algorithms in given order
            for alg in cutNames:
                TheCutAlgs += [ [ alg ] ]
                pass
            pass
        
        totalIn = 0
        totalOut = 0
        for alg in TheCutAlgs:
            res = self.GetCutEffNumbers(algoName=alg[0], UseEventWeight=UseEventWeight, applyAllPreviousCuts=applyAllPreviousCuts)
            eff   = res[0]
            n_in  = res[1]
            n_out = res[2]
            if eff is not None:
                if (n_in > 0.):
                    eff_err = sqrt( eff * (1.0 - eff) / n_in )
                else:
                    eff_err = -1.
                printStr = "Cut named: %20s -> events: [%7.2f,%7.2f] eff.: %5.3e +- %5.3e " % (alg[0], n_in, n_out, eff, eff_err)
            else:
                printStr = "Cut named: %20s -> events: [%7.2f,%7.2f] eff.: %5s +- %5s " % (alg[0], n_in, n_out, " -- ", " -- ")
                pass
            if not printEff:
                printStr = "Cut named: %20s -> events: %7.2f" % (alg[0], n_out)
            print printStr
            pass

 
    def __mergeSampleResults__(self, res, addRes):
        """
        Recursively add together python structures (list, dict).
        Only floats, ints, and TH1, TH2 are consider for addition.
        """
        if type(res) is dict and type(addRes) is dict:
            for key in res:
                if not addRes.has_key(key):
                    continue
                if (type(res[key]) is float and type(addRes[key]) is float) or (type(res[key]) is int and type(addRes[key]) is int):
                    res[key] += addRes[key]
                elif (type(res[key]) is dict and type(addRes[key]) is dict) or (type(res[key]) is list and type(addRes[key]) is list):
                    self.__mergeSampleResults__( res[key], addRes[key] )
                elif (isinstance(res[key], TH1) and isinstance(addRes[key], TH1)):
                    res[key].Add( addRes[key] )
                elif (isinstance(res[key], TH2) and isinstance(addRes[key], TH2)):
                    res[key].Add( addRes[key] )

        elif type(res) is list and type(addRes) is list:
            size = len(res)
            if len(addRes) < size:
                size = len(addRes)
            for i in xrange(size):
                if (type(res[i]) is float and type(addRes[i]) is float) or (type(res[i]) is int and type(addRes[i]) is int):
                    res[i] += addRes[i]
                elif (type(res[i]) is dict and type(addRes[i]) is dict) or (type(res[i]) is list and type(addRes[i]) is list):
                    self.__mergeSampleResults__( res[i], addRes[i] )
                elif (isinstance(res[i], TH1) and isinstance(addRes[i], TH1)):
                    res[i].Add( addRes[i] )
                elif (isinstance(res[i], TH2) and isinstance(addRes[i], TH2)):
                    res[i].Add( addRes[i] )



    def addSample(self, sampleToAdd, quiet=True):
        """
        When running over many events, one can split into several jobs.
        Thus, one ends up with several pickled and ntuple files belonging together.
        E.g.
        <SampleName>_0-999.pickled.root, <SampleName>_1000-1999.pickled.root
        <SampleName>_0-999.ntuple.root, <SampleName>_1000-1999.ntuple.root

        This method merges two Samples into one (which
        loads all ntuple.root files into its TChain).

        Note: things done in the algorithm's finalize might be corrupted after merging !

        """

        sample0 = self

        if self.SimpleCutFlow:
            gotEvents=True
            for s in sampleToAdd.Statistics:
                if sampleToAdd.Statistics[s][0]==0:
                    gotEvents=False
                    break
            if gotEvents:
                self.AddFiles( sampleToAdd.Files )
            else:
                if not quiet: print 'Skipping files in',sampleToAdd.name,'as no events were accepted'
                pass
            # statistics are simply added together
            for stat in self.Statistics:
                if sampleToAdd.Statistics.has_key(stat):
                    for i in range(len(sample0.Statistics[stat])):
                        self.Statistics[stat][i] += sampleToAdd.Statistics[stat][i]
            # results are recursively added (only float, int, TH1, TH2  are considered at the moment)
            self.__mergeSampleResults__(self.results, sampleToAdd.results)
            self.__mergeSampleResults__(self.resultTObjects, sampleToAdd.resultTObjects)
            return True
        else:
            self.AddFiles( sampleToAdd.Files )
            atLeastOneWithEvents=False
            for CutFlow in self.__fStats:
                gotEvents = True
                for s in sampleToAdd.Statistics[CutFlow]:
                    if sampleToAdd.Statistics[CutFlow][s][0]==0:
                        gotEvents=False
                        break
                    pass
                atLeastOneWithEvents = atLeastOneWithEvents or gotEvents
                pass
            if atLeastOneWithEvents:
                self.AddFiles( sampleToAdd.Files )
            else:
                if not quiet: print self.name,': Skipping files in',sampleToAdd.name,'as no events were accepted'
                pass
            # statistics are simply added together
            for CutFlow in self.Statistics:
                for stat in self.Statistics[CutFlow]:
                    if sampleToAdd.Statistics[CutFlow].has_key(stat):
                        for i in range(len(sample0.Statistics[CutFlow][stat])):
                            self.Statistics[CutFlow][stat][i] += sampleToAdd.Statistics[CutFlow][stat][i]
            # results are recursively added (only float, int, TH1, TH2  are considered at the moment)
            self.__mergeSampleResults__(self.results, sampleToAdd.results)
            self.__mergeSampleResults__(self.resultTObjects, sampleToAdd.resultTObjects)
            return True


    def Scan(self,VarList,Cut,Branches=[],VectorVar=None,table=None):
        """
        More advanced version of TChain.Scan

        varlist is list of variables. Formatting can be specified by using a tuple, e.g.
                varlist=['v1',('v2','%5.2f')]
        Cut is simple expression for selecting events
        if VectorVar is specified, "[]" in VarList is replaced with loop over the VectorVar
        result is returned as a new table or added to an existing specified one
        """
        vars=[]
        format=[]
        title=[]
        for v in VarList:            
            if type(v)==str:
                vars.append(v)
                format.append('%10.3g')
                title.append('%10s' % v)
            else:
                vars.append(v[0])
                format.append(v[1])
                if len(v)>2:
                    title.append(v[2])
                else:
                    title.append('%10s' % v[0])
        if not table:
            from Table import Table
            table=Table(rows=0,cols=vars)
            for vv,tt in zip(vars,title):
                table['__COL__',vv]=tt
        import TTreeAlgorithm
        algo=TTreeAlgorithm.TTreeAlgorithmLooper("ChainScanner")
        import ScanAlgorithm
        algo.AddAlgorithm( ScanAlgorithm.ScanAlgorithm("",vars,format,Cut,Branches,table,VectorVar) )
        algo.SetDebug(1,10000)
        algo.Loop(self)
        return table
        

######################################################################################
## CombinedSample class
##
## Descirption: combination of several Sample objects
##
######################################################################################

class CombinedSample (Sample):
    def __init__(self, name, Group, SampleNames=[]):

        # super class's constructor
        Sample.__init__(self, name, dir="")

        # overwrite some Sample class attributes
        self.className = "CombinedSample"
        self.Chain = 0

        self.listPickleVars = [
            'name',
            'className',
            'XSection',
            'Lumi',
            'Weight',
            'tags',
            'analyses',
            'SampleNames'
            ]


        self.Group=Group
        self.SampleNames = []

        for S in SampleNames:
            # sanity check
            if not Group.Samples.has_key(S):
                print "warning: sample %s not found" % S
                continue
            if isinstance( Group.Samples[S], CombinedSample ):
                for d in Group.Samples[S].SampleNames:
                    self.SampleNames += [d]
            else:
                self.SampleNames += [S]

        self.XSection = -1
        self.Lumi     = -1


    def MakeUnique(self):
        """
        Go through list of samples and make a unique list out of
        it. this is then saved instead of the old list of samples.
        """
        mySet = set(self.SampleNames)
        self.SampleNames = list(mySet)


    def GetXSection(self):
        """
        the x-sections are additive, so we simply return the sum.
        """
        xs = 0.0
        for S in self.SampleNames:
            xs += float( self.Group.Samples[S].GetXSection() )
        return xs

    def GetLumi(self):
        """
        the integrated luminosities are additive, so we simply return the sum.
        """
        lumi = 0.0
        for S in self.SampleNames:
            lumi += float( self.Group.Samples[S].GetLumi() )
        return lumi


    def GetEntries(self):
        """
        Return the sum of all Sample's TChain.GetEntries()
        """
        n = 0
        for S in self.SampleNames:
            n += self.Group.Samples[S].GetEntries()
        return n

    def GetWeightedEntries(self):
        """
        Return the sum of all Sample's weighted events.
        """
        n = 0
        for S in self.SampleNames:
            n += self.Group.Samples[S].GetWeightedEntries()
        return n

    def GetExpectedEvents(self, luminosity, useCrossSection = False):
        """
        Return the expected number of events for the given luminosity.

        approach 1)

           exp_evts = sample_entries * sample_weight  * luminosity

           here, sample_entries is the sum over the remaining
           event weights (after given event selection),
           sample_weight is assumed to be
           1 / (integrated data luminosity) or x-section / MC_events.

        approach 2)  [if useCrossSection = True]

           exp_evts = cross-section * cut_eff * luminosity

           here, cross-section is associated to the sample
           whose event selection efficiency is the given
           cut_eff
        """

        if useCrossSection:
            return self.GetXSection() * self.GetCutEff() * luminosity
        else:
            exp_evts = 0.0
            for S in self.SampleNames:
                sample = self.Group.Samples[S]
                exp_evts += sample.GetWeightedEntries() * sample.GetWeight() * luminosity
                pass
            return exp_evts

    def GetStatistics(self, index = 0):
        """
        Return the Statistics dictionary of the Sample at position index.
        """
        if len(self.SampleNames) > index:
            return self.Group.Samples[ self.SampleNames[index] ].GetStatistics()
        else:
            return {}




    def GetCutEffNumbers(self, algoName="", UseEventWeight = True, applyAllPreviousCuts=True, UseSampleWeight = True ):
        """
        Return weighted cut eff. :
        eff. = (w1*N1*eff1 + w2*N2*eff2 + ..) / (w1*N1 + w2*N2 + ...)

        Note: Can only apply all previous cuts ...
        """

        if not applyAllPreviousCuts:
            print "ERROR: can not handle a single cut in CombinedSample, please use applyAllPreviousCuts=True !"
            return [None, None, None]

        tot_evts_in   = 0.0
        tot_evts_out  = 0.0

        for S in self.SampleNames:
            res = self.Group.Samples[S].GetCutEffNumbers(algoName=algoName, UseEventWeight=UseEventWeight, applyAllPreviousCuts=True)
            evts_in  = res[1]
            evts_out = res[2]
            sampleWeight = 1.0
            if UseSampleWeight:
                sampleWeight = float(self.Group.Samples[S].Weight)

            if  evts_in is not None and evts_out is not None:
                tot_evts_in  += sampleWeight * evts_in
                tot_evts_out += sampleWeight * evts_out

        if tot_evts_in > 0:
            eff = float(tot_evts_out) / float(tot_evts_in)
        else:
            eff = None

        return [ eff, tot_evts_in, tot_evts_out ]


    def GetCutEff(self, algoName="", UseEventWeight = True, applyAllPreviousCuts=True, UseSampleWeight = True ):
        """
        Return weighted cut eff. :
        eff. = (w1*N1*eff1 + w2*N2*eff2 + ..) / (w1*N1 + w2*N2 + ...)
        """
        eff = self.GetCutEffNumbers(algoName=algoName, UseEventWeight=UseEventWeight,
                                    UseSampleWeight=UseSampleWeight, applyAllPreviousCuts=applyAllPreviousCuts) [0]

        if eff is not None:
            return eff
        else:
            return 0.0


    def GetCutEffErr(self, algoName="", UseEventWeight = True, applyAllPreviousCuts=True, UseSampleWeight = True ):
        """
        Return weighted cut eff. err:
        # def eff. for sample i as eff_{i} = n_{i,+}/(n_{i,+} + n_{i,-})
        # taken from: https://www.desy.de/~blist/notes/effic.ps.gz
        """
        
        if not applyAllPreviousCuts:
            print "ERROR: can not handle a single cut in CombinedSample, please use applyAllPreviousCuts=True !"
            return [None, None, None]

        sumPlus     = 0.0
        sumPlusSq   = 0.0
        sumNeg      = 0.0
        sumNegSq    = 0.0
        sumAll      = 0.0

        for S in self.SampleNames:
            res = self.Group.Samples[S].GetCutEffNumbers(algoName=algoName, UseEventWeight=UseEventWeight, applyAllPreviousCuts=True)
            evts_in  = res[1]
            evts_out = res[2]
            evts_p   = evts_out
            evts_n   = evts_in - evts_out
            sampleWeight = 1.0
            if UseSampleWeight:
                sampleWeight = float(self.Group.Samples[S].Weight)
                pass                
            if  evts_in is None or evts_out is None:
                continue
            sumPlus   += sampleWeight*evts_p
            sumPlusSq += sampleWeight*sampleWeight*evts_p
            sumNeg    += sampleWeight*evts_n
            sumNegSq  += sampleWeight*sampleWeight*evts_n
            sumAll    += sampleWeight*evts_in
            pass

        if sumAll > 0.0:
            err = sqrt( (sumPlusSq*sumNeg*sumNeg + sumNegSq*sumPlus*sumPlus) ) / (sumAll*sumAll)
            return err
        else:
            print "ERROR: division by zero"
            return None
        

    def GetTTreeCutEffNumbers(self, cut, UseEventWeight = True, maxEntries=-1, applyAllPreviousCuts=True, UseSampleWeight = True ):
        """
        Return weighted ttree cut eff. :
        eff. = (w1*N1*eff1 + w2*N2*eff2 + ..) / (w1*N1 + w2*N2 + ...)

        Note: Can only apply all previous cuts ...
        """

        if not applyAllPreviousCuts:
            print "ERROR: can not handle a single cut in CombinedSample, please use applyAllPreviousCuts=True !"
            return [None, None, None]

        tot_evts_in   = 0.0
        tot_evts_out  = 0.0

        for S in self.SampleNames:
            res = self.Group.Samples[S].GetTTreeCutEffNumbers(cut=cut, UseEventWeight=UseEventWeight, maxEntries=maxEntries, applyAllPreviousCuts=True)
            evts_in  = res[1]
            evts_out = res[2]
            sampleWeight = 1.0
            if UseSampleWeight:
                sampleWeight = float(self.Group.Samples[S].Weight)

            if  evts_in is not None and evts_out is not None and type(sampleWeight) is float:
                tot_evts_in  += sampleWeight * evts_in
                tot_evts_out += sampleWeight * evts_out

        if tot_evts_in > 0:
            eff = float(tot_evts_out) / float(tot_evts_in)
        else:
            eff = None

        return [ eff, tot_evts_in, tot_evts_out ]

    def GetTTreeCutEff(self, cut, UseEventWeight = True, maxEntries=-1, applyAllPreviousCuts=True, UseSampleWeight = True):
        """
        Retrieve efficiency of a given cut

        By default the weighted events are used for the eff.
        If, however, useEventWeight == False, then the pure
        TTree evts_out / evts_in is returned !
        """
        eff = self.GetTTreeCutEffNumbers(cut=cut, UseEventWeight=UseEventWeight, UseSampleWeight=UseSampleWeight, applyAllPreviousCuts=applyAllPreviousCuts ) [0]

        if eff is not None:
            return eff
        else:
            return 0.0

    def GetTTreeCutEffErr(self, cut, UseEventWeight = True, maxEntries=-1, applyAllPreviousCuts=True, UseSampleWeight = True ):
        """
        Return weighted cut eff. err:
        # def eff. for sample i as eff_{i} = n_{i,+}/(n_{i,+} + n_{i,-})
        # taken from: https://www.desy.de/~blist/notes/effic.ps.gz
        """
        
        if not applyAllPreviousCuts:
            print "ERROR: can not handle a single cut in CombinedSample, please use applyAllPreviousCuts=True !"
            return [None, None, None]

        sumPlus     = 0.0
        sumPlusSq   = 0.0
        sumNeg      = 0.0
        sumNegSq    = 0.0
        sumAll      = 0.0

        for S in self.SampleNames:
            res = self.Group.Samples[S].GetTTreeCutEffNumbers(cut=cut, maxEntries=maxEntries, UseEventWeight=UseEventWeight, applyAllPreviousCuts=True)
            evts_in  = res[1]
            evts_out = res[2]
            evts_p   = evts_out
            evts_n   = evts_in - evts_out
            sampleWeight = 1.0
            if UseSampleWeight:
                sampleWeight = float(self.Group.Samples[S].Weight)
                pass                
            if  evts_in is None or evts_out is None:
                continue
            sumPlus   += sampleWeight*evts_p
            sumPlusSq += sampleWeight*sampleWeight*evts_p
            sumNeg    += sampleWeight*evts_n
            sumNegSq  += sampleWeight*sampleWeight*evts_n
            sumAll    += sampleWeight*evts_in
            pass

        if sumAll > 0.0:
            err = sqrt( (sumPlusSq*sumNeg*sumNeg + sumNegSq*sumPlus*sumPlus) ) / (sumAll*sumAll)
            return err
        else:
            print "ERROR: division by zero"
            return None
        


    def Draw(self,expression, cut="1",opts="", bins=100, min=0, max=1000, 
             HistName="Hist",Norm=1000.0,
             DoDraw=True, title="", UseEventWeight=True, defaultSystematic=0.0, systematics={}, DontAllowNegativeBins=False):
        """
        Add histograms of all combined samples together using ROOT's
        TH1 Add(..) method. With Sumw2() the errors are correctly propagated.
        """

        # final histogram
        hist=TH1F(expression+" "+cut,expression+" "+cut,bins,min,max)
        hist.Sumw2()
        if title!="":
            hist.SetTitle(title)

        # loop over all samples, draw them and add them together
        for S in self.SampleNames:
#            print "adding hist: %s" %S
            TheSample=self.Group.Samples[S]

            # do not draw if no events there!
            if TheSample.GetEntries() == 0:
                continue

##            h = TH1F(HistName, expression+" "+cut, bins, min, max)
##            h.Sumw2()
##            if TheSample.Chain.Project(HistName, expression, "("+eventWeight+")*"+cut, opts) == 0:
##                print "WARNING, 0 entries in hist : %s" % hist.GetTitle()
##                continue

##            if h.GetEffectiveEntries() == 0:
##                print "WARNING, 0 entries in hist : %s" % hist.GetTitle()
##                continue

##            TheSample.NormalizeHist(h,Norm)
##            h.SetName(HistName)
            h = TheSample.Draw( expression=expression, cut=cut, opts=opts,
                                bins=bins, min=min, max=max,
                                HistName=HistName, Norm=Norm, DoDraw=False,
                                title="", UseEventWeight=UseEventWeight, defaultSystematic=defaultSystematic,
                                systematics=systematics, DontAllowNegativeBins=DontAllowNegativeBins)

            try:
               h
               if h.GetEntries()>0:
                  hist.Add(h)
            except:
               continue

        hist.SetName(HistName)
        if DoDraw:
            hist.Draw()

        return hist

    def Draw2D(self,expression, cut="1",opts="",xbins=100, xmin=0, xmax=1000, ybins=100, ymin=0, ymax=1000, 
               HistName="Hist",Norm=1000.0,
               DoDraw=True, title="", UseEventWeight=True,UseSampleWeight=True):
        """
        Add histograms of all combined samples together using ROOT's
        TH2 Add(..) method. With Sumw2() the errors are correctly propagated.
        """

        # final histogram
        hist=TH2F(expression+" "+cut,expression+" "+cut,xbins,xmin,xmax, ybins,ymin,ymax)
        hist.Sumw2()
        if title!="":
            hist.SetTitle(title)

        # loop over all samples, draw them and add them together
        for S in self.SampleNames:
#            print "adding hist: %s" %S
            TheSample=self.Group.Samples[S]

            # do not draw if no events there!
            if TheSample.GetEntries() == 0:
                continue

            h = TheSample.Draw2D( expression=expression, cut=cut, opts=opts,
                                  xbins=xbins, xmin=xmin, xmax=xmax,
                                  ybins=ybins, ymin=ymin, ymax=ymax,
                                  HistName=HistName, Norm=Norm, DoDraw=False,
                                  title="", UseEventWeight=UseEventWeight)
            try:
               h
               if h.GetEntries()>0:
                  hist.Add(h)
            except:
               continue

        if DoDraw:
            hist.Draw()

        return hist


    def Project(self,HistName,expression,cut="1",opts=""):
        for S in SampleNames:
            self.Group.Samples[S].Chain.Project(HistName,expression,cut,opts)


    def Print(self,opts=""):
        """
        print information about all Samples of this CombinedSample

        opt contains 'v' : verbose mode = opt('crs')
        opt contains 'c' : print chain
        opt contains 'r' : print sample results
        opt contains 's' : print sample statistics
        """
        print "--- CombinedSample.Print()"
        for S in self.SampleNames:
            print "--- printing Sample : %s" % S
            self.Group.Samples[S].Print( opts )
            pass
        pass

    def Leaves(self):
        if len(self.SampleNames) > 0:
            self.Group.Samples[ self.SampleNames[0] ].Leaves()
            pass
        pass
    
    def Scan(self,expression,cut="1",opts=""):
        for S in self.SampleNames:
            self.Group.Samples[S].Chain.Scan(expression,cut,opts)



######################################################################################
## SusySample class
##
## Descirption: specialised Sample class that is used for 2 dimensional mSugra points.
##              This class remembers all mSugra parameters: m_0 and m_12 for easier 2dim
##              plotting
##
######################################################################################

class SusySample(Sample):
    def __init__(self, name, m0=0, m12=0, dir=""):
        Sample.__init__(self,name,dir)

        self.className = "SusySample"
        self.m0=m0
        self.m12=m12
        self.A0 = None
        self.tanB = None
        self.sgnMu = None

        self.m_t = None   # top mass


        # Scalar and gaugino mass spectrum
        self.m_gluino = None # Gluino mass, PDG ID 1000021

        self.m_ldq = None # Left down Squark, PDG ID 1000001
        self.m_luq = None # Left up Squark, PDG ID 1000002
        self.m_lsq = None # Left Strange Squark, PDG ID 1000003
        self.m_lcq = None # Left charm Squark, PDG ID 1000004
        self.m_lbq = None # Lighter bottom Squark, PDG ID 1000005
        self.m_ltq = None # Lighter top Squark, PDG ID 1000006

        self.m_rdq = None # Right down Squark, PDG ID 2000001
        self.m_ruq = None # Right up Squark, PDG ID 2000002
        self.m_rsq = None # Right Strange Squark, PDG ID 2000003
        self.m_rcq = None # Right charm Squark, PDG ID 2000004
        self.m_hbq = None # Heavier bottom Squark, PDG ID 2000005
        self.m_htq = None # Heavier top Squark, PDG ID 2000006


        self.m_higgs_h0 = None # Lighter Scalar Higgs
        self.m_higgs_H0 = None # Heavier Scalar Higgs
        self.m_higgs_A0 = None # Pseudo-Scalar Higgs
        self.m_higgs_Hp = None # Positive Charged Higgs


        # add all these additional variables to the list of pickled vars. :
        self.listPickleVars += ['m0', 'm12', 'A0', 'tanB', 'sgnMu', 'm_t']
        self.listPickleVars += ['m_gluino']
        self.listPickleVars += ['m_ldq', 'm_luq', 'm_lsq', 'm_lcq', 'm_lbq', 'm_ltq']
        self.listPickleVars += ['m_rdq', 'm_ruq', 'm_rsq', 'm_rcq', 'm_hbq', 'm_htq']

        self.listPickleVars += ['m_higgs_h0', 'm_higgs_H0', 'm_higgs_A0', 'm_higgs_Hp']



######################################################################################
## FileStagerSample class
## this class uses Max Baak's FileStager class (ie TCopyChain) instead of the TChain
## this copies the needed ntuples behind the scenes to the local host
######################################################################################

class FileStagerSample(Sample):
    def __init__(self, name, dir="", doStaging = True, stageMode = 'castor'):
        Sample.__init__(self,name,dir)

        self.className = "FileStagerSample"
        self.doStaging = doStaging
        self.prefix = 'gridcopy://'
        self.stageMode=stageMode
        self.listPickleVars += [
            'prefix',
            'stageMode',
            ]
        
        # load extra lib
        gSystem.Load("libFileStagerLib.so")
        # make sure ROOT picks up TCopyFile when filename starts with gridcopy://
        gROOT.GetPluginManager().AddHandler("TFile", "^gridcopy:", "TCopyFile","TCopyFile_cxx", "TCopyFile(const char*,Option_t*,const char*,Int_t)")

        from ROOT import TCopyChain, TCopyFile
        # setup FileStager manager
        if (doStaging) :
            # turn on staging functionality
            TCopyChain.SetOriginalTChain(False)
            TCopyFile.SetOriginalTFile(False)
            # stager settings
            self.setStageManager( stageMode )
            pass
        
        self.Chain = TCopyChain(dir)

        pass


    def SetLocalFiles(self, path):
        self.Chain = TChain( self.Dir )
        localFiles = []
        for f in self.Files:
            localFiles.append( path+'/'+f.split("/")[-1] )
            pass
        self.Files = localFiles
        self.AddFilesToChain()

        tmp = Sample( 'tmp' )
        tmp.Copy( self )
        tmp.AddFilesToChain()
        
        return tmp
        
        
        
    def getStageManager(self):
        """
        return singleton of TStageManager
        """
        return TStageManager.instance()
    

    def setStageManager(self, stageMode = 'castor'):
        """
        set TStageManager to stageMode =
        'castor' : use rfcp command
        '...' : ...
        """

        if stageMode == 'castor':
            manager = self.getStageManager()
            manager.setInfilePrefix("gridcopy://")
            manager.setCpCommand("rfcp")
            # by default manager stores in $TMPDIR, or else /tmp ifndef
            # manager.setBaseTmpdir("/tmpdir")
            # manager.setPipeLength(1)
            # turn on verbosity
            #manager.verbose()     # lots of output
            manager.verboseWait()   # useful to see if your next has not yet finished staging
        elif stageMode == 'castorXrcp':
            manager = self.getStageManager()
            manager.setInfilePrefix("gridcopy://")
            self.prefix="gridcopy://root://castoratlas/"
            manager.setCpCommand("xrdcp")
            # by default manager stores in $TMPDIR, or else /tmp ifndef
            # manager.setBaseTmpdir("/tmpdir")
            # manager.setPipeLength(1)
            # turn on verbosity
            #manager.verbose()     # lots of output
            manager.verboseWait()   # useful to see if your next has not yet finished staging
        elif stageMode == 'XRD':
            manager = self.getStageManager()
            manager.setInfilePrefix("gridcopy://") #root://pcuta1.cern.ch///xrd/")
            self.prefix="gridcopy://root://pcuta1.cern.ch///xrd/"
            manager.setCpCommand("xrdcp")
            # by default manager stores in $TMPDIR, or else /tmp ifndef
            manager.setBaseTmpdir("/tmp")
            # manager.setPipeLength(1)
            # turn on verbosity
            #manager.verbose()     # lots of output
            manager.verboseWait()   # useful to see if your next has not yet finished staging
        else:
            print "stageMode=%s not supported (yet)" % (stageMode)
            pass

        pass


    def SetInteractive(self, mode = True):
        """
        In interactive mode, the staged ntuples and log files will be kept until deleted by user.
        """
        manager = self.getStageManager()
        manager.setInteractive( mode )
        pass
    
    
    def AddFilesToChain(self):
        from ROOT import TCopyChain, TCopyFile
        # setup FileStager manager
        if (self.doStaging) :
            # turn on staging functionality
            TCopyChain.SetOriginalTChain(False)
            TCopyFile.SetOriginalTFile(False)
            # stager settings
            self.setStageManager( self.stageMode )
            pass

        theFiles = [ self.prefix+fn[ fn.rfind('/castor'):].replace('//','/') for fn in self.Files]
        
        self.Chain=TCopyChain(self.Dir)
        self.AddFiles( theFiles, AddToChainOnly=True)

    def AddDirectory(self, path, require="", XSection=-1):
        self.XSection=XSection

        if path[-1] != '/':
            path += '/'
            pass

        if self.stageMode=="XRD":
            lsCommand="xrdls"
        else:
            lsCommand="nsls"

        CastorFiles={}
        
        if self.stageMode=="castor":
            directories = popen(lsCommand+' -l %s' %(path)).readlines()

            for fileentry in directories:
                fileEL=fileentry.split()
                filename=fileEL[8]
                filesize=int(fileEL[4])
                CastorFiles[filename]=filesize
                                                            
        if require == "":
            fileNames = popen(lsCommand+' %s' %(path)).readlines()
        else:
            fileNames = popen(lsCommand+' %s | grep -E %s' %(path,require)).readlines()

        fileNames.sort()

        self.Files += [ path + myFile[0:-1] for myFile in fileNames ]
        theFiles = [ self.prefix + path + myFile[0:-1] for myFile in fileNames ]
        self.AddFiles(theFiles, AddToChainOnly=True)




######################################################################################
## ProofSample class
## implements extra methods to make it run with PROOF
######################################################################################

class ProofSample(Sample):
    def __init__(self, name, dir=""):
        Sample.__init__(self,name,dir)
        self.OldChain = None
        self.TDSet = None

        self.Entries=-1


    def EnableProof(self):
        if not self.TDSet:
            self.TDSet=TDSet(self.Chain)
        
        self.OldChain=self.Chain

        self.TDSet=TDSet(self.Chain)

        self.Chain=self.TDSet

    def DisableProof(self):
        self.Chain=self.OldChain

    def GetEntries(self):
        if self.Entries==-1:
            
            if type(self.Chain)== TDSet:
                self.Entries=self.OldChain.GetEntries()
            else:
                self.Entries=self.Chain.GetEntries()

        return self.Entries

    def ProofProject(self, histname, expression, cut):
        if type(self.Chain)==TDSet:
            Cname=None
            try:
                Cname=gPad.GetName()
            except ReferenceError:
                Cname=None

            MyCan=TCanvas("ROOTSUCKS")
            entries=self.Chain.Draw(expression+">>"+histname,cut)
            MyCan.Close()
            if Cname:
                gROOT.FindObject(Cname).cd()
        else:
            entries = self.Chain.Project(histname,expression,cut)                
        return entries

    def GetWeightedEntries(self):
        """
        Return the sum over all event weights.
        If eventWeightVar is not given to this Sample,
        simply return the TChain.GetEntries()
        Note, for the TFileStager chain, GetEntries is not working (simply returns max INT)
        ==> we do something different here.
        """
        hist=TH1F('hist','hist',1,0,2)
        entries = self.ProofProject("hist","1",self.eventWeightVar)
        weight=hist.GetBinContent(1)
        hist.Delete()
        return weight


    ##################################
    ##        TTree Draw methods    ##

    def Draw(self, expression, cut="1", opts="",
             bins=100, min=0, max=1000, HistName="Hist",Norm=1000.0, maxLumi=-1, DoDraw=True,
             title="", UseEventWeight=True, defaultSystematic=0.0, systematics={},
             DontAllowNegativeBins=False, UseSampleWeight=True):
        """
        Samples's Draw method to draw any TTree variable of this sample.

        maxLumi: if you want to plot only a sub-sample of the dataset, use this option
                 Note that if maxLumi > 0, then Norm is set to be -1 (ie. histogram is NOT normalized)

                 maxLumi = -1 : run over full sample, apply normalization Norm
                 maxLumi > 0  : run over sub-sample, do not normalize histogram 

        """

        eventWeight = "1"
        if UseEventWeight and self.eventWeightVar != '' :
            eventWeight = self.eventWeightVar

        Nentries = TChain.kBigNumber #self.GetWeightedEntries()
        if maxLumi > 0 and self.GetExpectedEvents(maxLumi)< self.GetWeightedEntries() :
            Nentries = int(self.GetExpectedEvents(maxLumi))
            Norm = -1
            
        hist=TH1F("htemp2", expression+" "+cut, bins, min, max)
        hist.Sumw2()
        if type(self.Chain)==TDSet:
            Cname=None
            try:
                Cname=gPad.GetName()
            except ReferenceError:
                Cname=None

            MyCan=TCanvas("ROOTSUCKS")
            NN=self.Chain.Draw(expression+">>htemp2","("+eventWeight+")*"+cut,opts, Nentries)
            MyCan.Close()
            if Cname:
                gROOT.FindObject(Cname).cd()
        else:
            NN=self.Chain.Project("htemp2",expression,"("+eventWeight+")*"+cut,opts, Nentries)

        if NN == 0:
#            print "WARNING, 0 entries in hist : %s" % hist.GetTitle()
            return

        if hist.GetEffectiveEntries() == 0:
#            print "WARNING, 0 entries in hist : %s" % hist.GetTitle()
            return

        self.NormalizeHist(hist,Norm,UseSampleWeight)


        # set systematic error to use
        sys = defaultSystematic
        if systematics.has_key( self.name ):
            sys = systematics[ self.name ] # use this one instead
        # add the systematic error to the existing error per bin
        if sys != 0.0:
            # debugging msg
            print "adding systematics %1.2f on top of MC stats errors for sample %s" % (sys, self.name)
            for bin in range(hist.GetNbinsX()):
                # bins start with 1, not 0 !
                error = hist.GetBinError(bin+1)
                content = hist.GetBinContent(bin+1)
                new_error = sqrt(error**2 + (sys*content)**2)
                hist.SetBinError(bin+1, new_error)

        hist.SetName(HistName)
        if title!="":
            hist.SetTitle(title)


        # set bins with negative content to 0.0
        if DontAllowNegativeBins:
            for bin in range(hist.GetNbinsX()):
                if hist.GetBinContent(bin+1) < 0.0:
                    hist.SetBinContent(bin+1, 0.0)

        if DoDraw:
            hist.Draw()
        return hist


    ##################################
    ##        TTree Draw methods    ##

    def Draw2D(self, expression, cut="1", opts="",
               xbins=100, xmin=0, xmax=1000, ybins=100, ymin=0, ymax=1000,
               HistName="Hist",Norm=1000.0, maxLumi=-1, DoDraw=True,
               title="", UseEventWeight=True,
               UseSampleWeight=True):
        """
        Samples's 2dim Draw method to draw any TTree variable of this sample.

        """

        eventWeight = "1"
        if UseEventWeight and self.eventWeightVar != '' :
            eventWeight = self.eventWeightVar

        Nentries = TChain.kBigNumber #self.GetWeightedEntries()
        if maxLumi > 0 and self.GetExpectedEvents(maxLumi)< self.GetWeightedEntries() :
            Nentries = int(self.GetExpectedEvents(maxLumi))
            Norm = -1

        hist=TH2F("htemp2", expression+" "+cut, xbins, xmin, xmax, ybins, ymin, ymax)
        hist.Sumw2()

        if type(self.Chain)==TDSet:
            Cname=None
            try:
                Cname=gPad.GetName()
            except ReferenceError:
                Cname=None
            MyCan=TCanvas("ROOTSUCKS")
            NN=self.Chain.Draw(expression+">>htemp2","("+eventWeight+")*"+cut,opts, Nentries)
            MyCan.Close()
            if Cname:
                gROOT.FindObject(Cname).cd()
        else:
            NN=self.Chain.Project("htemp2",expression,"("+eventWeight+")*"+cut,opts, Nentries)

        if hist.GetEffectiveEntries() == 0:
            print "WARNING, 0 entries in hist : %s" % hist.GetTitle()
            return 

        self.NormalizeHist(hist,Norm,UseSampleWeight)

        hist.SetName(HistName)
        if title!="":
            hist.SetTitle(title)


        if DoDraw:
            hist.Draw()
        return hist

def NewProofSample(sample):
    nS=ProofSample(sample.name,sample.Dir)
        # Copy All Attributes
    for obj in sample.__dict__: 
        nS.__dict__[obj]=sample.__dict__[obj]
            
    NewChain=TChain(nS.Dir)
            
    for file in nS.Files:
        NewChain.AddFile(file)
                
    nS.Chain=NewChain
                

    return nS
