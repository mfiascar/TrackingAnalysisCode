# ------------------------------------------------------------- #
# package: SPyRoot                                              #
# file: SampleHandler                                           #
# classes: SampleHandler                                        #
# purpose: Load Samples (=root ntuples), manage Samples ..      #
#                                                               #
# authors: Amir Farbin    <Amir.Farbin@cern.ch> - CERN          #
#          Till Eifert    <Till.Eifert@cern.ch> - U. of Geneva  #
#          Jamie Boyd     <Jamie.Boyd@cern.ch>  - CERN          #
#                                                               #
# File and Version Information:                                 #
# $Id: SampleHandler.py,v 1.61 2009/03/17 20:40:27 eifert Exp $
# ------------------------------------------------------------- #

from ROOT import *
from os import popen
from os import getcwd
import root_pickle
from Sample import Sample, SusySample, CombinedSample, FileStagerSample,ProofSample,NewProofSample
from SObject import SObject
#from QueueHandlers import GenevaQueueHandler

#set maximum filesize to 19 GBytes to avoid multiple output files
TTree.SetMaxTreeSize(19000000000L)

######################################################################################
## SampleHandler class
##
## Descirption: manage a list of Sample objects, ie load, save, compare,
##              make efficiency plots etc
##
######################################################################################

class SampleHandler:
    def __init__(self, name=""):
        self.name=name
        self.queueHandler = None #GenevaQueueHandler("GenevaQueueHandler")
        self.Samples={}
        self.DefaultAttributes=[{ "LineColor":2 , "FillStyle":3004, "FillColor":2 , "MarkerColor":2, "MarkerStyle":20},
                                { "LineColor":4 , "FillStyle":3004, "FillColor":4 , "MarkerColor":4, "MarkerStyle":21},
                                { "LineColor":1 , "FillStyle":3004, "FillColor":1 , "MarkerColor":1, "MarkerStyle":22},
                                { "LineColor":3 , "FillStyle":3004, "FillColor":3 , "MarkerColor":3, "MarkerStyle":23},
                                { "LineColor":11 , "FillStyle":3004, "FillColor":11 , "MarkerColor":11, "MarkerStyle":24},
                                { "LineColor":6 , "FillStyle":3004, "FillColor":6 , "MarkerColor":6, "MarkerStyle":25},
                                { "LineColor":7 , "FillStyle":3004, "FillColor":7 , "MarkerColor":7, "MarkerStyle":26},
                                { "LineColor":8 , "FillStyle":3004, "FillColor":8 , "MarkerColor":8, "MarkerStyle":27}
                                ]

    def LoadSamplesFromDir(self, path, pickleExtension='.pickled.root', require='', loadAllNtuples=True, quiet=True,
                           storeSamplesWithNameExt='', excludeFiles=[], XRDPath=None, defaultType=SObject):
        """
        This method loads pickled Sample objects from a given directory.

        When a sample was splitted (running several batch jobs) it will be merged.
        Note: things (int, float, TH1, TH2) get added. this can cause problems when things happened
        in the algorithm's finalize !!!

        path                :  directory containing all pickled files
        pickleExtension     :  file ending of pickled files [default '.pickled.root']
        require             :  string that is grep'ed for in the directory [default '']
        loadAllNtuples      :  look for additional ntuples (produced when ROOT reaches the limit of max entries per file)
        quiet               :  don't print debug messages
        storeSamplesWithNameExt : name extension to be used in the SampleHandler's internal dictionary for holding all Samples
        excludeFiles        :  list of strings. If any string is found in a file name, then this file is skipped
        XRDPath             : ?
        defaultType         : initial guess of sample type (default is SObject). Speeds up loading (if right type is specified)
        """

        import glob
        if not path[-1]=='/':
            path += '/'
        flist = glob.glob(path+'*'+require+'*'+pickleExtension)

        

        if type(excludeFiles) is str :
            if excludeFiles == '':
                excludeFiles = []
            else:
                excludeFiles = [ excludeFiles ]
                pass
            pass
        
        # load samples from directory
        samples = {}
        for myFile in flist:
            skip = False
            for ef in excludeFiles:
                if myFile.find(ef)!=-1 :
                    skip = True
                    break
                pass
            if skip: continue
            myFile = myFile.split(path)[-1]
            sample = self.loadSample(path=path, myFile=myFile, pickleExtension=pickleExtension,
                                         loadAllNtuples=loadAllNtuples, quiet=quiet, XRDPath=XRDPath, defaultType=defaultType)
            
            SplitPos=sample.name.find("_Split_")

            if SplitPos>-1:
                print "Merging", sample.name, "into", sample.name[0:SplitPos]+"."
                sample.name=sample.name[0:SplitPos]


            if not samples.has_key(sample.name):
                samples[ sample.name ] = sample
            else:
                # merge it ...
                #self.__mergeSamples__(samples[ sample.name ], sample)
                samples[ sample.name ].addSample( sample )

        # add samples to SampleHandler
        counter = 0
        for s in samples:
            newSample = samples[s]
            newName = newSample.name + storeSamplesWithNameExt
            # don't overwrite existing samples
            if newName in self.Samples:
                print "warning : a sample with name = %s exists already, keeping old one." % newSample.name
                continue

            self.Samples[ newName ] = newSample
            counter += 1

        if not quiet: print "Loaded %i samples from: %s" % (counter, path)
        return counter

    def SplitSampleByJobs(self,SampleName,NSamples):
        """ 
        Splits a sample into N sub-samples divided at file boundries.

        """

        OrigSample=self.Samples[SampleName]
        OrigFiles=OrigSample.Files
        NOrigFiles=len(OrigFiles)

        NSamplesCalc=1
        while(NSamplesCalc!=NSamples and NSamplesCalc>0 and NSamples>0):
            NFilesPerSample=NOrigFiles/NSamples
            NSamplesCalc=NOrigFiles/NFilesPerSample
            if NOrigFiles%NFilesPerSample!=0:
                NSamplesCalc=0

            NSamples=NSamples-1
            
        if NSamples<2:
            print "Unable to Split nicely... not splitting"
            return
            
        self.SplitSamples(SampleName,NSamples)


    def SplitSample(self,SampleName,NFilesPerSample,UseProof=False):
        """ 
        Splits a sample into sub-samples divided at file boundries with N input files per sample.
        """

        OrigSample=self.Samples[SampleName]
        OrigFiles=OrigSample.Files
        NOrigFiles=len(OrigFiles)

        if NOrigFiles<NFilesPerSample:
            print "Warning:",SampleName,"not split",NOrigFiles,NFilesPerSample
            return
        
        nSubSamples=NOrigFiles//NFilesPerSample
        NLastSample=NOrigFiles%(nSubSamples)

        I=0

        for FirstFileI in range(0,NOrigFiles,NFilesPerSample):
            if NOrigFiles>=FirstFileI+NFilesPerSample:
                EndI=FirstFileI+NFilesPerSample
            else:
                EndI=FirstFileI+NLastSample


            NewFiles= OrigFiles[FirstFileI:EndI]
#            print NOrigFiles,NFilesPerSample,FirstFileI,EndI,NewFiles
            NewName=SampleName+"_Split_"+str(I)

            NewSample=OrigSample.Clone(name=NewName,
                                       Files=NewFiles)
            I+=1
            print "Created New Sample:",NewName
            
            if UseProof:
                NewSample=NewProofSample(NewSample)
            self.Samples[NewName]=NewSample

        if I != nSubSamples:
            print "Warning: Asked for", nSubSamples, "subsamples but produced ", I,"."

        return I


    def loadSample(self, path, myFile, pickleExtension='.pickled.root', loadAllNtuples=True, quiet=True, XRDPath=None, defaultType=SObject):
        """
        Internal method to load one Sample with its ntuples from a given
        directory. the Sample is _not_ stored into the SampleHandler
        but rather returned.

        path            : directory containg the Sample's pickled file
        myFile            : pickle file name
        pickleExtension : file ending of pickled files [default '.pickled.root']
        loadAllNtuples  : look for additional ntuples (produced when ROOT reaches the limit of max entries per file)
        quite           : print debug messages ?
        """
        if not path[-1]=='/':
            path += '/'
        fullFile = path + myFile
        fullFile = fullFile.strip()
        if not quiet:
            print "loading Sample from pickled file: %s" % (fullFile)

        #newSample = Sample('tmp')
        #newSample.unpickle(fullFile, quiet)
        newSample = defaultType.__call__('tmp')
        newSample.unpickle(fullFile, quiet)
        
        # initial guess of class type might be wrong ...
        if newSample.className == "Sample" and defaultType.__name__ != "Sample":
            newSample = Sample('tmp')
            newSample.unpickle(fullFile, quiet)
        elif newSample.className == "SusySample" and defaultType.__name__ != "SusySample":
            newSample = SusySample('tmp')
            newSample.unpickle(fullFile, quiet)
        elif newSample.className == "CombinedSample" and defaultType.__name__ != "CombinedSample":
            newSample = CombinedSample('tmp', self, [])
            newSample.unpickle(fullFile, quiet)
        elif newSample.className == "FileStagerSample" and defaultType.__name__ != "FileStagerSample":
            newSample = FileStagerSample('tmp')
            newSample.unpickle(fullFile, quiet)

        if loadAllNtuples and newSample.className != "FileStagerSample":
            lookForFiles = fullFile.split(pickleExtension)[0]
            ntupleFiles = popen('ls %s* | grep -v %s' %(lookForFiles, pickleExtension)).readlines()

            for ntuple in ntupleFiles:
                n = ntuple.strip()
                nFile = n.split('/')[-1]
                # do not add original file again (check file name only, not path!):
                if nFile in [ f.split('/')[-1] for f in newSample.Files ] :
                    continue
                newSample.AddFiles([n])

        # if we're dealing with a CombinedSample, reset the Chain to 0
        if newSample.className == "CombinedSample":
            newSample.Chain = 0

        # modify files names : add extension for xrdcp
        if XRDPath:
            newSample.setStageManager('castorXrcp')
            newFiles = []
            newChain = type(newSample.Chain)( newSample.Chain.GetName() )
            for afile in newSample.Chain.GetListOfFiles():
                oldfilename=afile.GetTitle()
                #print "Old:",oldfilename
                try:
                    #strippedfilename=oldfilename.split("xrd/")[1]
                    strippedfilename=oldfilename.split("gridcopy://")[1]
                except IndexError:
                    #strippedfilename=oldfilename.split("XRD/")[1]
                    strippedfilename=oldfilename
                newfilename=XRDPath+strippedfilename
                newChain.Add(newfilename)
                newFiles.append( newfilename )
                #print "New:",newfilename
                pass
            newSample.Files=newFiles
            newSample.Chain=newChain
            #print 'setting FileStager to xrdcp mode'
            pass
            
        return newSample


    def SaveSamplesToDir(self, path, fileExt='.pickled.root'):
        print "SaveSamplesToDir: dir= %s  fileExt=%s" %(path, fileExt)
        for S in self.Samples:
            fullFile = path + '/' + S + fileExt
            fullFile = fullFile.strip()
            print "saving Sample %s to file" % (S)
            self.Samples[S].pickle(fullFile)


    def CreateSample(self,SampleName,Directory):
        if not self.Samples.has_key(SampleName):
            self.Samples[SampleName]=Sample(SampleName,Directory)

    def Print(self):
        for S in self.Samples:
            self.Samples[S].Print()


    def ConvertSamplesToLocal(self,path="",UseProof=False):
        newSH=SampleHandler()

        for sample in self.Samples:
            s=self.Samples[sample]

            if type(s) == FileStagerSample:
                s=self.Samples[sample].SetLocalFiles(path)

            if UseProof:
                newSH.Samples[sample]=NewProofSample(s)
            else:
                newSH.Samples[sample]=s

        return newSH

    def EnableProof(self):
        for sample in self.Samples:
            self.Samples[sample].EnableProof()

    def DisableProof(self):
        for sample in self.Samples:
            self.Samples[sample].DisableProof()


    def AddFile(self,SampleName,File,Directory="", XSection=-1):
        self.CreateSample(SampleName,Directory)
        self.Samples[SampleName].AddFiles([File], XSection)
        pass
    
    def AddGridFile(self,SampleName,File,m0, m12, Directory="", XSection=-1):
        if not self.Samples.has_key(SampleName):
            self.Samples[SampleName] = SusySample(SampleName,m0,m12,Directory)

        self.Samples[SampleName].AddFiles(files=[File], XSection=XSection)
        pass

    def AddDirectory(self,SampleName,Path,Directory="",Require="",XSection=-1,XRD=False,prepend="",XRDHack=None):
        # TODO : remove HACK
        if SampleName in self.Samples:
            print "Sample: %s already added" % SampleName
            return
        self.CreateSample(SampleName,Directory)
        self.Samples[SampleName].AddDirectory(Path,Require,XSection,XRD,prepend,XRDHack)
        pass
    
    def AddDirectorySplit(self,SampleName,Path,Directory="",Require="",XSection=-1,Split=100,XRD=False,prepend=""):
        if SampleName in self.Samples:
            print "Sample: %s already added" % SampleName
            return
        require=Require
        if require == "":
            fileNames = popen('ls %s' %(Path)).readlines()
        else:
            fileNames = popen('ls %s | grep -E %s' %(Path,require)).readlines()
        fileNames.sort()
        
        if Path[-1] != '/':
            Path += '/'
        fullFileNames = []
        n=0
        m=0
        for file in fileNames:
            n=n+1
            #print "Adding: ", file
            #print "n ",  n,file[0:-1]

            fullFileNames += [ prepend+Path+file[0:-1] ]
            if n%Split == 0 or n==len(fileNames) :
                #print fullFileNames
                m=m+1
                if (m ==1 and n==len(fileNames)):
                    SampleN=SampleName
                else:    
                    SampleN="%s_Split_%d" %(SampleName,m) 
                self.CreateSample(SampleN,Directory)
                self.Samples[SampleN].AddFiles(fullFileNames)
                fullFileNames=[]
                pass
            pass
        pass


    def AddCombinedSample(self,SampleName, Group, Samples):
        if not self.Samples.has_key(SampleName):
            self.Samples[SampleName]=CombinedSample(SampleName,Group,Samples)
            pass
        pass

    def AddCombinedSampleReg(self, CombinedSampleName, SampleExp, Tags=[]):
        if not self.Samples.has_key(CombinedSampleName):
            listOfSamples = self.expandListOfSamples( samples=[], tags=Tags )
            listOfSamples += self.expandRegListOfSamples( SampleExp )
            self.Samples[CombinedSampleName]=CombinedSample(CombinedSampleName, Group=self, SampleNames=listOfSamples)
        else:
            print "CombinedSampleName = %s exists already, do nothing!" % CombinedSampleName
            pass
        pass

    def ExpandToList(self, arg, N):
        return [arg for i in xrange(N)]   


    def CheckList(self, l, N):
        if not isinstance(l,list):
            ll=self.ExpandToList(l,N)
        else:
            ll=l

        return ll



    def Compare(self, Samples, Expressions, Cuts="1", bins=0, min=0, max=0,
                Norm=1000.0, XTitle="", YTitle="",
                Attrib=[], Opts="", title="", UseEventWeight=True, UseSampleWeight=True,
                doLegend=True, defaultSystematic=0.0, systematics={},
                DontAllowNegativeBins=False,ymin=None,ymax=None,Titles=None,ResetNames=None):

        if Attrib==[]:
            Attrib=self.DefaultAttributes

        if Titles:
            TheTitles=Titles
        else:
            TheTitles=Samples

        if not isinstance(Samples,list):
            print "Compare Error: First Argument must be a list of samples names"
            return

        NSamples=len(Samples)

        TheExpressions=self.CheckList(Expressions,NSamples)
        TheCuts=self.CheckList(Cuts,NSamples)
        TheOpts=self.CheckList(Opts,NSamples)

        TheBins=self.CheckList(bins,NSamples)
        TheMins=self.CheckList(min,NSamples)
        TheMaxs=self.CheckList(max,NSamples)



        # SampleI = 0
        # print "Draw(%s, %s, %s, %s, %s, %s, %s, %s, True) " % (TheExpressions[SampleI], TheCuts[SampleI],TheOpts[SampleI],TheBins[SampleI],TheMins[SampleI],TheMaxs[SampleI], Samples[SampleI],TheNorms[SampleI])

        output=[]

        for SampleI in range(NSamples):

            sampleName= self.Samples[Samples[SampleI]].name

            h = self.Samples[Samples[SampleI]].Draw(expression=TheExpressions[SampleI],
                                                    cut=TheCuts[SampleI],
                                                    opts=TheOpts[SampleI],
                                                    bins=TheBins[SampleI],
                                                    min=TheMins[SampleI],
                                                    max=TheMaxs[SampleI],
                                                    HistName=sampleName,
                                                    Norm=Norm,
                                                    title=title,
                                                    DoDraw=False,
                                                    UseEventWeight=UseEventWeight,
                                                    defaultSystematic=defaultSystematic,
                                                    systematics=systematics,
                                                    DontAllowNegativeBins=DontAllowNegativeBins,
                                             #       UseSampleWeight=UseSampleWeight
                                                    )
            if h is None:
                continue

            if ymax is not None:
                h.SetMaximum(ymax)
            if ymin is not None:
                h.SetMinimum(ymin)
            if XTitle!="":
                h.GetXaxis().SetTitle( XTitle)
            if YTitle!="":
                h.GetYaxis().SetTitle( YTitle)

            if ResetNames:
                aname=h.GetName()
                h.SetName(aname+"_"+ResetNames)

            output+=[ h ]

        if len(output)>0: # need this or nicedraw crashes when Nhisto == 0
            self.NiceDraw(output,Attrib, doLegend,Titles=TheTitles)
        return output



    def CompareProfile(self, Samples, Expressions, Cuts="1", ybins=0, ymin=0, ymax=0, xbins=0, xmin=0, xmax=0,
                       XTitle="", YTitle="",
                       Attrib=[], Opts="", title="", UseEventWeight=True, doLegend=True, DoDraw=True,Titles=None,
                       MinEntries=10.):


        if Attrib==[]:
            Attrib=self.DefaultAttributes

        if Titles:
            TheTitles=Titles
        else:
            TheTitles=Samples

        if not isinstance(Samples,list):
            print "Compare Error: First Argument must be a list of samples names"
            return

        NSamples=len(Samples)

        TheExpressions=self.CheckList(Expressions,NSamples)
        TheCuts=self.CheckList(Cuts,NSamples)
        TheOpts=self.CheckList(Opts,NSamples)

        TheXBins=self.CheckList(xbins,NSamples)
        TheXMins=self.CheckList(xmin,NSamples)
        TheXMaxs=self.CheckList(xmax,NSamples)

        TheYBins=self.CheckList(ybins,NSamples)
        TheYMins=self.CheckList(ymin,NSamples)
        TheYMaxs=self.CheckList(ymax,NSamples)

        TheMinEntries=self.CheckList(MinEntries,NSamples)



        output0=[]
        output1=[]
        output2=[]
        output3=[]

        for SampleI in range(NSamples):

            sampleName= self.Samples[Samples[SampleI]].name

            h = self.Samples[Samples[SampleI]].Profile(expression=TheExpressions[SampleI],
                                                       cut=TheCuts[SampleI],
                                                       opts=TheOpts[SampleI],
                                                       xbins=TheXBins[SampleI],
                                                       xmin=TheXMins[SampleI],
                                                       xmax=TheXMaxs[SampleI],
                                                       ybins=TheYBins[SampleI],
                                                       ymin=TheYMins[SampleI],
                                                       ymax=TheYMaxs[SampleI],
                                                       HistName=sampleName,
                                                       title=title,
                                                       DoDraw=False,
                                                       UseEventWeight=UseEventWeight,
                                                       MinEntries=TheMinEntries[SampleI]
                                                    )
            if h is None:
                continue

            
            if XTitle!="":
                h[0].GetXaxis().SetTitle( XTitle)
                h[1].GetXaxis().SetTitle( XTitle)
                h[2].GetXaxis().SetTitle( XTitle)
                h[3].GetXaxis().SetTitle( XTitle)
            if YTitle!="":
                h[0].GetYaxis().SetTitle( YTitle)
                h[1].GetYaxis().SetTitle( YTitle)
                h[2].GetYaxis().SetTitle( YTitle)
                h[3].GetYaxis().SetTitle( YTitle)

            output0+=[ h[0] ]
            output1+=[ h[1] ]
            output2+=[ h[2] ]
            output3+=[ h[3] ]

        if DoDraw:
            c1=TCanvas("c1")
            c1.Divide(2,2)
            c1.cd(1)
            self.NiceDraw(output0,Attrib, False)
            c1.cd(2)
            self.NiceDraw(output1,Attrib, doLegend,Titles=TheTitles)
            c1.cd(3)
            self.NiceDraw(output2,Attrib, False)
            c1.cd(4)
            self.NiceDraw(output3,Attrib, False)
            
            
        return [output0,output1,output2,output3,c1]



## arguments 'list of samples', variable to plot eff against, cutA (both den & num), cutB (just num), rane (bins=0, min=0, max=0,Norms=1000.0)
    def CompareEff(self,Samples,Expressions,CutA="1", CutB="1", bins=0, min=0, max=0,
                   Attrib=[],Opts="", entries=-1, doLegend=True):

        if Attrib==[]:
            Attrib=self.DefaultAttributes

        if not isinstance(Samples,list):
            print "Compare Error: First Argument must be a list of samples names"
            return

        NSamples=len(Samples)

        TheExpressions=self.CheckList(Expressions,NSamples)
        TheCutsA=self.CheckList(CutA,NSamples)
        TheCutsB=self.CheckList(CutB,NSamples)
        TheOpts=self.CheckList(Opts,NSamples)

        TheBins=self.CheckList(bins,NSamples)
        TheMins=self.CheckList(min,NSamples)
        TheMaxs=self.CheckList(max,NSamples)


        outputA=[]
        outputB=[]
        eff=[]

        for SampleI in range(NSamples):
            histA=self.Samples[Samples[SampleI]].Draw(TheExpressions[SampleI],
                                                      TheCutsA[SampleI],
                                                      TheOpts[SampleI],
                                                      TheBins[SampleI],
                                                      TheMins[SampleI],
                                                      TheMaxs[SampleI],
                                                      Samples[SampleI],
                                                      0,
                                                      DoDraw=False)
            outputA += [histA]

            histB=self.Samples[Samples[SampleI]].Draw(TheExpressions[SampleI],
                                                      TheCutsB[SampleI]+"&&"+TheCutsA[SampleI],
                                                      TheOpts[SampleI],
                                                      TheBins[SampleI],
                                                      TheMins[SampleI],
                                                      TheMaxs[SampleI],
                                                      Samples[SampleI],
                                                      0,
                                                      DoDraw=False)
            outputB+=[histB]

            hist = TH1F(Samples[SampleI]+ "_eff",Samples[SampleI]+ "_eff",TheBins[SampleI],
                        TheMins[SampleI],
                        TheMaxs[SampleI])
            hist.SetMaximum(1.25)

            hist.Divide(histB,histA,1,1,"B")
            eff += [hist]

        output=[]
        output+=outputA
        output+=outputB


        self.NiceDraw(eff,Attrib, doLegend)
        output+=eff
        return output



    def NiceDraw(self,Hists,Attrib, doLegend=True,Titles=None):

        NHists=len(Hists)
        #print NHists
        TheOpts=self.CheckList(Attrib,NHists)

        #Legend=TLegend(0.7,0.9-.1*NHists,.9,.9);
        Legend=TLegend(0.72,0.85-.07*NHists,.91,.93);
        Legend.SetBorderSize(0)  #no border for legend
        Legend.SetFillColor(0) 
        TheHists=[]
        for histI in range(NHists):
            if Hists[histI] is None:
                continue
            MaxBin=Hists[histI].GetMaximum()
            MinBin=Hists[histI].GetMinimum()
            Norm=Hists[histI].GetNormFactor()

            Max=MaxBin
            Min=MinBin

            Mins=[]

            if Norm!=0:
                if Hists[histI].GetEntries()!=0:
                    Area=Hists[histI].Integral()  # This should be the integral!
                    # print Area
                    if Area!=0:
                        Max=float(Norm*MaxBin)/float(Area)
                        Min=float(Norm*MinBin)/float(Area)

            TheHists+=[ [Hists[histI],
                         Max,
                         TheOpts[histI],
                         Min, histI]]
            Mins.append(Min)

        TheMin=min(Mins)

        def Mycmp(x,y):
            xN=x[1]
            yN=y[1]
            if int(yN == xN):
                return 0
            if int(yN > xN):
                return 1
            else:
                return -1


        def Mycmp2(x,y):
            xN=x[0].GetName()
            yN=y[0].GetName()
            if int(yN == xN):
                return 0
            if int(yN > xN):
                return 1
            else:
                return -1


        TheHists.sort(Mycmp)

        first=True
        #c1 = TCanvas("c1","SPyRoot: NiceDraw")
        #if logY:
        #    c1.SetLogy()
        for hist in TheHists:
            if first:
                self.NiceHistogram(hist[0],hist[2])
                #Legend.AddEntry(hist[0],hist[0].GetName())
                if TheMin<0.:
                    hist[0].SetMinimum(1.1*TheMin)
                
                if hist[2].has_key("Draw"):
                    hist[0].Draw( hist[2]["Draw"] )
                else:
                    hist[0].Draw()
                first=False
            else:
                
                self.NiceHistogram(hist[0],hist[2])
                #Legend.AddEntry(hist[0],hist[0].GetName())
                opt = "sames"
                if hist[2].has_key("Draw"):
                    opt += hist[2]["Draw"]

                if hist[0].GetEntries() > 0.:
                    hist[0].Draw(opt)


        TheHists.sort(Mycmp2)

        if doLegend:        
            for i in xrange(len(TheHists)):
                hist=TheHists[i]
                if Titles:
                    Legend.AddEntry(hist[0],Titles[hist[4]])
                else:
                    Legend.AddEntry(hist[0],hist[0].GetTitle())

                Legend.Draw()
                Hists+=[Legend]

        #c1.Draw()
        #return c1

    def NiceDrawGraphs(self, Graphs, Attrib):

        NHists=len(Graphs)
        TheOpts=self.CheckList(Attrib,NHists)

        TheHists=[]

        first=True
        for i in xrange(len(Graphs)):
            opt = ""
            if first:
                opt = "A"
                first=False
            else:
                opt = "SAME"

            self.NiceHistogram( Graphs[i], TheOpts[i] )
            if TheOpts[i].has_key("Draw"):
                opt += TheOpts["Draw"]
            else:
                opt += "P"
            Graphs[i].Draw(opt)


    def NiceHistogram(self,hist,Opts):
        for Attrib in Opts:
            if not Attrib is "Draw":
                s="hist.Set"+Attrib+"(Opts[\""+Attrib+"\"])"
                eval(s)

    def Plot2D( self, varX, varY, varZ,
                funcX=lambda Sample, var: eval("Sample."+var),
                funcY=lambda Sample, var: eval("Sample."+var),
                funcZ=lambda Sample, var: eval("Sample."+var),
                samples=[], tags=[], Title="mSugra grid",
                sizeX = 10, minX = 0., maxX = 10.,
                sizeY = 10, minY = 0., maxY = 10., Selection=lambda Sample: True ):

        hist = TH2D("hist", Title, sizeX, minX, maxX, sizeY, minY, maxY)

        listOfSamples = self.expandListOfSamples(samples, tags)


        for s in listOfSamples:
            TheSample = self.Samples[s]
            if Selection(TheSample):
                hist.Fill( float(funcX( TheSample, varX)), float(funcY(TheSample, varY)),
                           float(funcZ(TheSample, varZ)) )
                pass
        #hist.Draw()

        return hist


    def expandListOfSamples(self,samples=[], tags=[], tagsAndLogic=False ):

        # when nothing is specified, return empty list !
        if samples == [] and tags == []:
            return []

        # otherwise, start collecting samples
        listOfSamples = []
        listOfSamples += samples

        for s in self.Samples:
            if not tagsAndLogic and len( filter(lambda x: x in tags, self.Samples[s].tags)) != 0:
                # print "adding sample: %s" % s
                listOfSamples += [s]
            if tagsAndLogic and len( filter(lambda x: x in tags, self.Samples[s].tags)) == len(tags):
                # print "adding sample: %s" % s
                listOfSamples += [s]
                
        listOfSamples = list(set(listOfSamples))

        # print "added %s samples" % len(listOfSamples)
        return listOfSamples

    def expandRegListOfSamples(self, sampleReg):

        # otherwise, start collecting samples
        listOfSamples = []

        for s in self.Samples:
            #print self.Samples[s].name
            if s.find( sampleReg ) != -1:
                listOfSamples += [s]

        # print "added %s samples" % len(listOfSamples)
        return listOfSamples


    def matchSamples(self, patterns, logicalAnd=False, verbose=False):
        """
        * patterns is a list of: (part of) sample names, or (exact) tag names
          if a pattern ends with '+\, then the beginning has to match (starting from first char)
        * logicalAnd : if set to True, all pattern expressions are required to match [default False]
        """
        sampleNames=[]
        samplePatterns=[]

        if not isinstance(patterns, list): patterns = [ patterns ]
        
        for p in patterns:
            if p.endswith('+'):
                samplePatterns.append(p[:-1])
            else:
                sampleNames.append(p)
                pass
            pass

        if verbose: print "samplePatterns", samplePatterns
        if verbose: print "sampleNames", sampleNames
        
        listOfSamples=[]
        if not logicalAnd:
            if verbose: print "in logical OR"
            for s in self.Samples:
                if s in sampleNames or len([t for t in self.Samples[s].tags if t in sampleNames]):
                    listOfSamples.append(s)
                else:
                    for p in samplePatterns:
                        if s.startswith(p) or len([t for t in self.Samples[s].tags if t.startswith(p)]):
                            listOfSamples.append(s)
                            break
                        pass
                    pass
                pass
            pass
        else:
            if verbose: print "in logical AND"
            for s in self.Samples:
                isGood = True
                for sn in sampleNames:
                    if not s == sn and len([t for t in self.Samples[s].tags if t == sn]) == 0 :
                        isGood = False
                        break
                    pass
                if not isGood: continue
                for p in samplePatterns:
                    if not s.startswith(p) and len([t for t in self.Samples[s].tags if t.startswith(p)])==0:
                        isGood = False
                        break
                    pass
                if isGood: listOfSamples.append(s)
                pass
            pass
        
        return listOfSamples

                                        

    def GridPlot(self, GridSamples, Function, FunctionVar = "", Cut="", Title="mSugra grid", GridSize = 5,
                 maxM0=3000, maxM12=1500, Attrib=[],Opts="", Factor=1.0, GridSizeX = -1, GridSizeY = -1,
                 minM0=0, minM12=0 ):

        if Attrib==[]:
            Attrib=self.DefaultAttributes

        if not isinstance(GridSamples,list):
            print "Compare Error: First Argument must be a list of GridSamples names"
            return

        NSamples=len(GridSamples)

        #TheNorms=self.CheckList(Norms,NSamples)

        # xs_hist = TH2D("XS_msugra", "XS_msugra",41,-50,4050,41,-12.5,1012.5)
        # xs_hist = TH2D("XS_msugra", "XS_msugra",5, 0, 3000, 5, 0, 1500)
        if GridSizeX < 0:
            GridSizeX = GridSize
        if GridSizeY < 0:
            GridSizeY = GridSize
        xs_hist = TH2D("mSugraGrid", "mSugraGrid", GridSizeX, minM0, maxM0, GridSizeY, minM12, maxM12)

        for Sample in GridSamples:
            TheSample = self.Samples[Sample]
            if isinstance(TheSample, SusySample):
                m0 = float(TheSample.m0)
                m12 = float(TheSample.m12)
            elif TheSample.extraMetaInformation.has_key('m0') and TheSample.extraMetaInformation.has_key('m12'):
                m0  = float(TheSample.extraMetaInformation['m0'])
                m12 = float(TheSample.extraMetaInformation['m12'])
            else:
                print "ouch, canot find m0/m12"
                continue
            # go on to nex sample if out of plot scope
            if m0 < minM0 or m0 > maxM0 or m12 < minM12 or m12 > maxM12:
                print "m0/m12 out of range", m0, m12," range m0:", minM0, maxM0,"range m12:",minM12,maxM12
                continue
            if FunctionVar == "":
                value = Function(TheSample)
            else:
                if Cut=="":
                    value = Function(TheSample, FunctionVar)
                else:
                    value = Function(TheSample, FunctionVar, Cut)
                    pass
                pass
            xs_hist.Fill( m0, m12, float(value) *float( Factor) )
            pass

        xs_hist.GetXaxis().SetTitle("m_{0} [GeV]")
        xs_hist.GetYaxis().SetTitle("m_{1/2} [GeV]")
        xs_hist.GetZaxis().SetTitle("")

        xs_hist.SetTitle(Title)
        # xs_hist.SetFillColor(45)
        # xs_hist.SetLineColor(10)
        # xs_hist.SetMarkerColor(4)

        # xs_hist.GetYaxis().SetLabelSize(0.025)
        # xs_hist.GetYaxis().SetTitleOffset(1.25)
        # xs_hist.GetXaxis().SetLabelSize(0.025)
        # xs_hist.GetZaxis().SetLabelSize(0.025)
        # xs_hist.SetStats(0)

        print "entries: "+str(xs_hist.GetEntries())

        # canvas1 = TCanvas("canvas1","canvas1", 600, 600);
        #canvas1.SetLogz()
        #xs_hist->Draw("A*")
        #xs_hist.SetMaximum(100000.)
        #xs_hist.SetMinimum(0.001)
        # xs_hist.Draw("colz")
        return xs_hist



    def ChangeNtupleSampleDir(self, newDirectory, TheSamples = []):

        if TheSamples == []:
            TheSamples = self.Samples


        for S in TheSamples:
            self.Samples[S].ChangeNtupleDir(newDirectory)


    def PrintCutEff(self, require='', TheSamples=[], algos=[], UseEventWeight=True, applyAllPreviousCuts=True,
                    printEff=True, CutFlow="Default"):
        """
        Print out event numbers and cut efficiencies for the list of algorithms and for the given sample names.

        require              : select algorithms having this string in their name
        TheSamples           : list of Sample names to make the printout for (these samples have to be known to SampleHandler)

        algos                : list of algorithm names. Default ([]) will use all algorithms that can be found inside the Statistics

        UseEventWeight       : use the weighted events. Default = True
        applyAllPreviousCuts : apply all previous cuts. Default = True
        CutFlow              : cut flow name.
        """
        if TheSamples == []:
            TheSamples = self.Samples

        # sort samples:
        sampleNames = []
        for S in TheSamples:
            sampleNames += [S]
        sampleNames.sort()

        for S in sampleNames:
            print "----  Sample %-15s ----  " % S
            self.Samples[S].PrintCutEff(require=require, cutNames=algos, UseEventWeight=UseEventWeight,
                                        applyAllPreviousCuts=applyAllPreviousCuts, printEff=printEff, CutFlow=CutFlow)





    def GetCutTable(self,TheSamples = [], Lumi=1000.0,CutFlow="Default"):

        if TheSamples == []:
            TheSamples = self.Samples

        def StatsCmp(x,y):
            xN=x[1]
            yN=y[1]
            if int(yN == xN):
                return 0
            if int(yN > xN):
                return 1
            else:
                return -1

            #TheHists.sort(Mycmp)

        print "Using Luminosity [pb]: "+str(Lumi)

        for S in TheSamples:
            print "Sample: "+S
            print "==================================="

            if self.Samples[S].Statistics.has_key(CutFlow):
                TheStats = self.Samples[S].Statistics[CutFlow]
                TheCutAlgs = []
                for alg in TheStats:
                    if alg.find("hist")==-1 : # and alg.find("Cut")!=-1
                        TheCutAlgs += [ [alg, TheStats[alg][0], TheStats[alg][1]]]

                TheCutAlgs.sort(StatsCmp)
            else:
                continue

            xsec = float(self.Samples[S].XSection)
            totalIn = 0
            totalOut = 0
            for alg in TheCutAlgs:
                if totalIn==0:
                    totalIn = float(alg[1])
                if alg[1] != 0:
                    eff = float(alg[2])/float(alg[1])
                    errEff = sqrt( eff * float( float(alg[1]) - float(alg[2]))) / float(alg[1])
                    totalOut=float(alg[2])

                else:
                    print "Final Cut Efficiency: 0.0"
                    break

                print "Cut named: %20s -> eff.: %2.3f +- %2.3f " % (alg[0], eff, errEff)
            if totalIn == 0:
                print "totalIn == 0 ..."
            else:
                totalEff = totalOut / totalIn
                totalEffErr = sqrt( totalEff * float( totalIn - totalOut)) / totalIn
                print "Final Cut Efficiency: %2.3f +- %2.3f" % (totalEff, totalEffErr)
                print "# exp. evts. (after cuts): %4.2f +- %2.2f" % ( ( xsec * Lumi), ( xsec * Lumi * totalEff* totalEffErr))



    def GetCutTable2(self,TheSamples = [], algos = [], outFileName="cutTable.txt", lumi=100.0, CutFlow="Default"):

        if TheSamples == []:
            TheSamples = self.Samples

        def StatsCmp(x,y):
            xN=x[1]
            yN=y[1]
            if int(yN == xN):
                return 0
            if int(yN > xN):
                return 1
            else:
                return -1

        first=True

        # sort samples:
        sampleNames = []
        for S in TheSamples:
            sampleNames += [S]
        sampleNames.sort()

        f = open(outFileName,'w')

        for S in sampleNames:

            if self.Samples[S].Statistics.has_key(CutFlow):
                TheStats = self.Samples[S].Statistics[CutFlow]
                TheCutAlgs = []
                for alg in TheStats:
                    if alg.find("hist")==-1 : # and alg.find("Cut")!=-1
                        TheCutAlgs += [ [alg, TheStats[alg][0], TheStats[alg][1]]]

                TheCutAlgs.sort(StatsCmp)
            else:
                continue


            # print out header the very first time
            if first:
                first=False
                alg_names = ""
                for alg in TheCutAlgs:
                    alg_names += "%-16s" % alg[0]
                tmp = "Sample"
                tmp2 = "total eff."
                tmp3 = "gen. xsec.[pb]"
                tmp4 = "exp. events for %s pb-1" % lumi
                alg_names += "%-16s" % tmp2
                alg_names += "%-16s" % tmp3
                alg_names += "%-16s" % tmp4
                print "%-16s %s" % (tmp, alg_names)
                f.write( "%-16s %s\n" % (tmp, alg_names) )
                print ""

            xsec = float(self.Samples[S].XSection)
            totalIn = 0
            totalOut = 0
            sampleEff = ""
            for alg in TheCutAlgs:
                if totalIn==0:
                    totalIn = float(alg[1])
                if alg[1] != 0:
                    eff = float(alg[2])/float(alg[1])
                    errEff = sqrt( eff * float( float(alg[1]) - float(alg[2]))) / float(alg[1])
                    totalOut=float(alg[2])

                else:
                    #print "Final Cut Efficiency: 0.0"
                    #break
                    eff = -1
                    errEff = 0

                #print "Cut named: %16s -> eff.: %2.3f +- %2.3f " % (alg[0], eff, errEff)
                tmp        = "%2.3f+-%2.3f  " % (eff, errEff)
                sampleEff += "%-16s" % tmp
            if totalIn == 0:
                #print "totalIn == 0 ..."
                totalEff = -1
                totalEffErr = 0

            else:
                totalEff = totalOut / totalIn
                totalEffErr = sqrt( totalEff * float( totalIn - totalOut)) / totalIn
                #print "Final Cut Efficiency: %2.3f +- %2.3f" % (totalEff, totalEffErr)
                #print "# exp. evts. (after cuts): %4.2f +- %2.2f" % ( ( xsec * Lumi), ( xsec * Lumi * totalEff* totalEffErr))
            tmp        = "%2.3f+-%2.3f  " % (totalEff, totalEffErr)
            sampleEff += "%-16s" % tmp

            xsec_str = "%2.5f" % xsec
            sampleEff += "%-16s" % (xsec_str)

            events = xsec * self.Samples[S].GetCutEff() * lumi
            eventStr = "%2.2f" % events
            sampleEff += "%-16s" % (eventStr)
            print "%-16s %s" % (S, sampleEff)
            f.write( "%-16s %s\n" % (S, sampleEff) )

        f.close()

    def Separation(self,Samples,Expressions, bins=100, min=0.0, max=1000000.0, Attrib=[], drawSeparation=False,
                   hist1 = None, hist2 = None):
        """
        plot 2 distributions f(x), g(x) each normalised to 1.0 and calculate the separation power,
        <S2> = 1/2 * Int_{-oo}^{oo} { ( f_hat(x) - g_hat(x) )**2 / (f_hat(x)+g_hat(x)) }

        f(x) and g(x) can be obtained from one or two Samples, from one or two Expressions !

        Parameters:

        Samples     : [sample1, sample2]  or sample1
        Expressions : [expr1, expr2] or expression
        bins        : number of bins
        min         : min of plot and integral !
        max         : max of plot and integral !
        Attrib      : attributes passed to NiceDraw for drawing
        drawSeparation : draw the separation histogram instead of returning the <S2>
        hist1       : use given histogram instead of producing it from the Samples (default None)
        hist2       : use given histogram instead of producing it from the Samples (default None)
        """

        if Attrib==[]:
            Attrib=self.DefaultAttributes
            pass
        
        if (hist1 is not None and hist2 is not None):
            h0 = hist1
            h1 = hist2
        else:
            # This is only to have a lenght 2 list for Expressions, input can be either list or not
            # The same for Samples
            TheExpressions=self.CheckList(Expressions,2)
            TheSamples=self.CheckList(Samples,2)

            NSamples=len(TheSamples)
            NExpressions=len(TheExpressions)

            if NSamples == 0 or NExpressions == 0 :
                print "Separation Error: You must enter a valid number of Samples or Variables"
                return
            if NSamples > 2 or NExpressions > 2 :
                print "Separation Error: <S2> not defined for more than 2 histograms"
                return
            if NSamples < 2 and NExpressions < 2 :
                print "Separation Error: <S2> not defined for less than 2 histograms"
                return

            h0 = self.Samples[TheSamples[0]].Draw(expression=TheExpressions[0], cut="1", opts="",
                                                  bins=bins, min=min, max=max,
                                                  HistName=TheSamples[0]+"."+TheExpressions[0], Norm=-1.0, DoDraw=False,
                                                  title="<S2>", UseEventWeight=True,
                                                  DontAllowNegativeBins=False)

            h1 = self.Samples[TheSamples[1]].Draw(expression=TheExpressions[1], cut="1", opts="",
                                                  bins=bins, min=min, max=max,
                                                  HistName=TheSamples[1]+"."+TheExpressions[1], Norm=-1.0, DoDraw=False,
                                                  title="<S2>", UseEventWeight=True,
                                              DontAllowNegativeBins=False)
            pass
        

        # Norm to area of 1.0
        area0=h0.Integral()
        area1=h1.Integral()
        if area0>0:
            h0.Scale( 1./area0 )
        else:
            return 0
        if area1>0:
            h1.Scale( 1./area1 )
        else:
            return 0

        ## <S2> Calculation
        s2=0.0
        for j in range( h0.GetNbinsX() ):
            if  (h0.GetBinContent(j+1)+h1.GetBinContent(j+1))  != 0.:
                s2 += 0.5*( h0.GetBinContent(j+1) - h1.GetBinContent(j+1) )**2/( h0.GetBinContent(j+1) + h1.GetBinContent(j+1) )
                pass
            pass

        if drawSeparation:
            print "<S2> = ",s2
            hists = []
            h0.SetTitle("<S2> = "+str(s2))
            h1.SetTitle("<S2> = "+str(s2))
            hists += [h0]
            hists += [h1]
            self.NiceDraw(hists,Attrib)
            return hists
        else:
            return s2

    def Separation2D(self,Samples,Expressions, xbins=100, xmin=0.0, xmax=1000000.0,
                     ybins=100, ymin=0.0, ymax=1000000.0, Attrib=[], drawSeparation=False):
        """
        plot 2 2D distributions f(x,y), g(x,y) each normalised to 1.0 and calculate the separation power,
        <S2> = 1/2 * Int_{-oo}^{oo} { ( f_hat(x,y) - g_hat(x,y) )**2 / (f_hat(x,y)+g_hat(x.y)) dx dy}

        f(x,y) and g(x,y) can be obtained from one or two Samples, from one or two Expressions !

        Parameters:

        Samples     : [sample1, sample2]  or sample1
        Expressions : [expr1, expr2] or expression
        bins        : number of bins
        min         : min of plot and integral !
        max         : max of plot and integral !
        Attrib      : attributes passed to NiceDraw for drawing
        drawSeparation : draw the separation histogram instead of returning the <S2>
        """

        if Attrib==[]:
            Attrib=self.DefaultAttributes

        ## This is only to have a lenght 2 list for Expressions, input can be either list or not
        ## The same for Samples
        TheExpressions=self.CheckList(Expressions,2)
        TheSamples=self.CheckList(Samples,2)

        NSamples=len(TheSamples)
        NExpressions=len(TheExpressions)

        if NSamples == 0 or NExpressions == 0 :
            print "Separation Error: You must enter a valid number of Samples or Variables"
            return
        if NSamples > 2 or NExpressions > 2 :
            print "Separation Error: <S2> not defined for more than 2 histograms"
            return
        if NSamples < 2 and NExpressions < 2 :
            print "Separation Error: <S2> not defined for less than 2 histograms"
            return

        h0 = self.Samples[TheSamples[0]].Draw2D(expression=TheExpressions[0], cut="1", opts="",
                                                xbins=xbins, xmin=xmin, xmax=xmax,
                                                ybins=ybins, ymin=ymin, ymax=ymax,
                                                HistName=TheSamples[0]+"."+TheExpressions[0], Norm=-1.0, DoDraw=False,
                                                title="<S2>", UseEventWeight=True)

        h1 = self.Samples[TheSamples[1]].Draw2D(expression=TheExpressions[1], cut="1", opts="",
                                                xbins=xbins, xmin=xmin, xmax=xmax,
                                                ybins=ybins, ymin=ymin, ymax=ymax,
                                                HistName=TheSamples[1]+"."+TheExpressions[1], Norm=-1.0, DoDraw=False,
                                                title="<S2>", UseEventWeight=True)

        # Norm to area of 1.0
        area0=h0.Integral()
        area1=h1.Integral()
        if area0>0:
            h0.Scale( 1./area0 )
        else:
            return 0
        if area1>0:
            h1.Scale( 1./area1 )
        else:
            return 0

        ## <S2> Calculation
        s2=0.0
        totInt = 0.0
        for i in range( h0.GetNbinsX() ):
            for j in range( h0.GetNbinsY() ):
                totInt += h0.GetBinContent(i+1, j+1)+h1.GetBinContent(i+1, j+1)
                if  (h0.GetBinContent(i+1, j+1)+h1.GetBinContent(i+1, j+1))  != 0.:
                    s2 += 0.5*( h0.GetBinContent(i+1,j+1) - h1.GetBinContent(i+1,j+1) )**2/( h0.GetBinContent(i+1,j+1) + h1.GetBinContent(i+1,j+1) )
                    pass
                pass

        #print "Cross-check: Int_{-oo}^{oo} { (f_hat(x,y)+g_hat(x.y)) dx dy} = %6.2f" % totInt

        if drawSeparation:
            print "<S2> = ",s2
            hists = []
            h0.SetTitle("<S2> = "+str(s2))
            h1.SetTitle("<S2> = "+str(s2))
            hists += [h0]
            hists += [h1]
            self.NiceDraw(hists,Attrib)
            return hists
        else:
            return s2



    def submitBatchJobs(self, script, copy_out, copy_out_mask="*", copy_in="", py_inDir = "",
                        samples=[], tags=[], eventsPerJob=-1, samplesPerJob=1, log_dir="", queue='long', batchScript='' ):
        """
        Submit a script to be executed on batch nodes.
        Each batch node job will process a certain number of samples (given by 'samplesPerJob').
        The list of samples to process is determined by:
        1) list of sample names
        2) all samples having (at least) one of the given tags.

        script         :  SPyRoot script to execute

        copy_out       :  copy output files here (see below)
        copy_out_mask  :  copy these files only [default is '*']
        copy_in        :  copy this to execution (tmp) directory on batch node (before processing)
                          this can be a space separated list of dirs/files e.g. './file1 /home/dir'

        py_inDir       :  set python var in_dir to that dir [default '']

        samples        :  add samples from this list
        tags           :  add samples having one of the given tags
        eventsPerJob   :  number of events each job should process [default -1 == not used]
        samplesPerJob  :  number of samples to process per batch job [default 1]
        log_dir        :  directory to put logfiles, if empty then use current working dir + ../queue-logs
        queue          :  what batch queue to use [default is 'long']
        batchScript    :  execute non-default batch script to start job [default '']

        Note : eventsPerJob dominates over samplesPerJob
               ie, when eventsPerJob<=0 (default) the jobs will process 'samplesPerJob' samples each.
               instead, when eventsPerJob > 0, 'samplesPerJob' is ignored and each job contains exactly
               one sample with maximum eventsPerJob events to process.
        """

        ## some sanity checks :
        if script=="":
            print "info : no script given to execute on the sample(s)!"
            return
        if copy_out=="":
            print "error : no copy_out given !"
            return
        if not type(samplesPerJob) is int:
            print "error : parameter: samplesPerJob not int !"
            return

        # complete relative path to full (using current working dir)
        if script[0] != "/"  :
            print "info : script given with no absolute path, will prepend current directory!"
            script = getcwd() + "/" + script
        if copy_out[0] != "/"  :
            print "info : copy_out given with no absolute path, will prepend current directory!"
            copy_out = getcwd() + "/" + copy_out

        if len(copy_in) > 0:
            parts = copy_in.split()
            newParts = []
            for i in parts:
                if i[0] != "/" :
                    newParts += [getcwd() + "/" + i]
                else:
                    newParts += [i]
            copy_in = " ".join(newParts)

        if log_dir=="":
            print "info : log directory not given, will use $PWD/../queue-logs/ !"
            log_dir = getcwd() + "/../queue-logs"

        # get list of samples
        listOfSamples = self.expandListOfSamples(samples, tags)

        if len(listOfSamples) == 0:
            print "error : No Samples found with the specified list of names, list of tags ..."
            return

        listOfJobs = []
        # find out event numbers of the samples, and put together list of jobs according to it
        if eventsPerJob > 0:
            events = {}
            tot_evts = 0
            for S in listOfSamples:
                events[S] = self.Samples[S].GetEntries()
                tot_evts += self.Samples[S].GetEntries()
            from math import ceil
            njobs = int( ceil( tot_evts/float(eventsPerJob) ) )
            print "njobs = %i, tot_evts=%i" % (njobs, tot_evts)
            startEvt = 0
            #for i in range(njobs):
            while len(listOfSamples) > 0:
                processEvts = eventsPerJob
                thisJob = []
                while processEvts>0:
                    S = listOfSamples[0]
                    #print "startEvt=%i processEvts = %i sample=%s, " % (startEvt, processEvts, S)
                    if events[S] > (startEvt + processEvts):
                        thisJob  += [S, startEvt, processEvts]
                        startEvt += processEvts
                        processEvts=0
                    elif events[S] == (startEvt + processEvts):
                        # end of job is end of sample
                        thisJob += [S, startEvt, processEvts ]
                        startEvt = 0
                        processEvts=0
                        listOfSamples.remove( S )
                    elif events[S] < (startEvt + processEvts):
                        # end of sample, but can process more evts in this job
                        # thisJob += [S, startEvt, -1]
                        # processEvts -= (events[S] - startEvt)
                        # startEvt = 0
                        # listOfSamples.remove( S )
                        # print "remaining evts = %i" % processEvts
                        thisJob += [S, startEvt, -1]
                        processEvts = 0
                        startEvt = 0
                        listOfSamples.remove( S )
                        # print "remaining evts = %i" % processEvts

                # add thisJob to list of jobs
                #print thisJob
                listOfJobs += [thisJob]

        else:
            while len(listOfSamples)>0:
                # process samplesPerJob samples:
                thisJob = []
                for j in range(samplesPerJob):
                    if len(listOfSamples) > 0:
                         thisJob += [ listOfSamples.pop(), 0, -1 ]
                listOfJobs += [thisJob]

        # debugging
        for j in listOfJobs:
            print j
        print "njobs = %i" % (len(listOfJobs))

        # debugging
        #print "script=%s, copy_out=%s, copy_out_mask=%s, copy_in=%s, py_inDir=%s, log_dir=%s" \
        #      % (script, copy_out, copy_out_mask, copy_in, py_inDir, log_dir)
        #print "samples="
        #print listOfSamples

        self.queueHandler.submitBatchJobs(script, copy_out, copy_out_mask, copy_in, py_inDir,
                                          listOfJobs, log_dir, queue, batchScript=batchScript)
        pass
    

    def RunFcnOnSamples(self, fcn, samples=[], tags=[], pickleSamplesAfterwards=False ):
        """
        Run a given functino on all Sample objects, where the Sample obj is given as a parameter: fcn(Sample object).
        The list of samples to process is determined by:
        1) list of sample names
        2) all samples having (at least) one of the given tags.

        script         :  script to execute
        samples        :  add samples from this list
        tags           :  add samples having one of the given tags
        """

        # get list of samples
        listOfSamples = self.expandListOfSamples(samples, tags)

        if len(listOfSamples) == 0:
            print "error : No Samples found with the specified list of names, list of tags ..."
            return

        for S in listOfSamples:
            TheSample = self.Samples[S]
            fcn( TheSample )
            if pickleSamplesAfterwards: TheSample.pickle()
            pass

        pass


    def MergeResultTObjectHists( self, samples=[], tags=[], useSampleWeights=True ):
        """
        Add all objects of type TH found in the list of samples in the resultTObjects.
        The useSampleWeights option will set use the Samples' Weight.

        A dictionary with the merged histograms is returned.
        """
        # get list of samples
        listOfSamples = self.expandListOfSamples(samples, tags)

        # get all sample names
        listOfSampleNames = []
        for s in listOfSamples:
            if isinstance( self.Samples[s], CombinedSample ): listOfSampleNames += self.Samples[s].SampleNames
            else: listOfSampleNames += [ self.Samples[s].name ]
            pass
        
        
        firstFile = True
        dictOfHists = {}
        for S in listOfSampleNames:
            sample = self.Samples[S]
            localHists = {}
            for key in sample.resultTObjects:
                obj = sample.resultTObjects[ key ]
                if isinstance( obj, TH1):
                    hist = obj.Clone()
                    hist.Sumw2()
                    if useSampleWeights and sample.GetWeight() != 0: hist.Scale( sample.GetWeight() )
                    localHists[ obj.GetName() ] =  hist
                    pass
                pass
            if firstFile:
                gROOT.cd("/")
                for key in localHists:
                    dictOfHists[ key ] = localHists[ key ]
                    pass
                firstFile = False
            else:
                for key in localHists:
                    if dictOfHists.has_key( key ): dictOfHists[ key ].Add( localHists[ key ] )
                    pass
                pass
            pass

        return dictOfHists #listOfHists




from collections import MutableMapping

class SamplesDict(MutableMapping):
    """
    Small class to replace default python dict ( key: Sample names, value: Sample obj).
    Internally, a dict is used with all Sample names. However, the Sample obj are only loaded (unpickled)
    the first time they are accessed.

    Dec. 11, 2010
    author: Till Eifert, CERN
    """
    def __init__(self, loadingObj):
        self.samples = {}
        self.loadingObj = loadingObj
        self.toLoadInfo = {}
        pass

    def __setitem__(self,loc,value):
        self.samples[loc]=value


    def __getitem__(self,loc):
        
        if not self.samples.has_key(loc):
            raise KeyError(loc)
        else:
            if self.samples[loc]==0:
                # load (unpickle) sample
                #print "unpickle SObject",loc,"..."
                if not self.toLoadInfo.has_key(loc):
                    raise KeyError('no loading information stored for',loc)
                self.samples[loc] = self.loadingObj.loadSample( **self.toLoadInfo[loc] )
                pass
            return self.samples[loc]

        pass

    def __delitem__(self,key):
        if not self.samples.has_key(key):
            print 'key',key,'not found'
            return
        try:
            del self.samples[key]
        except:
            print 'del',key,'failed'
            pass

    def __len__(self):
        return len(self.samples)

    def has_key(self,loc):
        return self.samples.has_key(loc)

    def keys(self):
        return self.samples.keys()

    def __iter__(self):
        return self.samples.__iter__()

    
    
class SmartSampleHandler(SampleHandler) :
    """
    This SampleHandler replaces the default Samples dict by the smart SamplesDict class.
    So we can delay the loading of Samples until needed.

    Dec. 11, 2010
    author: Till Eifert, CERN
    """
    def __init__(self, name=""):
        SampleHandler.__init__(self,name)
        self.Samples= SamplesDict(self)
        pass


    def LoadSamplesFromDir(self, path, pickleExtension='.pickled.root', require='', loadAllNtuples=True, quiet=True,
                           storeSamplesWithNameExt='', excludeFiles=[], XRDPath=None, defaultType=SObject, delayedLoading=True):
        """
        This method loads pickled Sample objects from a given directory.

        When a sample was splitted (running several batch jobs) it will be merged.
        Note: things (int, float, TH1, TH2) get added. this can cause problems when things happened
        in the algorithm's finalize !!!

        path                :  directory containing all pickled files
        pickleExtension     :  file ending of pickled files [default '.pickled.root']
        require             :  string that is grep'ed for in the directory [default '']
        loadAllNtuples      :  look for additional ntuples (produced when ROOT reaches the limit of max entries per file)
        quiet               :  don't print debug messages
        storeSamplesWithNameExt : name extension to be used in the SampleHandler's internal dictionary for holding all Samples
        excludeFiles        :  list of strings. If any string is found in a file name, then this file is skipped
        XRDPath             : ?
        defaultType         : initial guess of sample type (default is SObject). Speeds up loading (if right type is specified)
        delayedLoading      : load (unpickle) Sample objects only when accessed.
        
        """

        if not delayedLoading:
            return SampleHandler.LoadSamplesFromDir( path=path, pickleExtension=pickleExtension, require=require,
                                                     loadAllNtuples=loadAllNtuples, quiet=quiet,
                                                     storeSamplesWithNameExt=storeSamplesWithNameExt,
                                                     excludeFiles=excludeFiles, XRDPath=XRDPath,
                                                     defaultType=defaultType )
        
        

        import glob
        if not path[-1]=='/':
            path += '/'
        flist = glob.glob(path+'*'+require+'*'+pickleExtension)

        

        if type(excludeFiles) is str :
            if excludeFiles == '':
                excludeFiles = []
            else:
                excludeFiles = [ excludeFiles ]
                pass
            pass
        
        # load samples from directory
        samples = {}
        for myFile in flist:
            skip = False
            for ef in excludeFiles:
                if myFile.find(ef)!=-1 :
                    skip = True
                    break
                pass
            if skip: continue
            myFile = myFile.split(path)[-1]
            sampleName = myFile.split(pickleExtension)[0]
            
            samples[sampleName] = { 'path' : path, 'myFile' : myFile, 'pickleExtension' :pickleExtension,
                                    'loadAllNtuples': loadAllNtuples, 'quiet' : quiet, 'XRDPath' :XRDPath, 'defaultType':defaultType }
            pass

        # add samples to SampleHandler
        counter = 0
        for s in samples:
            loadInfo = samples[s]
            newName = s + storeSamplesWithNameExt
            # don't overwrite existing samples
            if newName in self.Samples:
                print "warning : a sample with name = %s exists already, keeping old one." % newName
                continue

            self.Samples[ newName ] = 0 # to be loaded later (!)
            self.Samples.toLoadInfo[ newName ] = loadInfo
            counter += 1

        if not quiet: print "Loaded %i samples from: %s" % (counter, path)
        return counter
