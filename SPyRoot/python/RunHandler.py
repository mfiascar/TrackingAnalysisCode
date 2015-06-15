# ------------------------------------------------------------- #
# package: SPyRoot                                              #
# file: RunHandler                                              #
# classes: RunHandler                                           #
# purpose: Run a user-defined analysis over a list of Samples   #
#                                                               #
# authors: Amir Farbin <Amir.Farbin@cern.ch> - CERN             #
#          Till Eifert <Till.Eifert@cern.ch> - U. of Geneva     #
#          Jamie Boyd  <Jamie.Boyd@cern.ch>  - CERN             #
#                                                               #
# File and Version Information:                                 #
# $Id: RunHandler.py,v 1.24 2008/05/19 08:14:28 eifert Exp $
# ------------------------------------------------------------- #


from ROOT import *
import SampleHandler
import Sample
import os


class RunHandler:
    def __init__(self, Group, SampleNames, algo, name=""):
        self.name=name
        self.Group=Group
        if type(SampleNames) is type([]):
            self.SampleNames=SampleNames
        elif type(SampleNames) is str:
            self.SampleNames = [SampleNames]
        else:
            print "ERROR: argument SampleNames in wrong format!"
        self.Algo=algo
        self.Results={}


    def Loop(self, MaxEntries=-1, doPickle=False, pickleDir="./", firstEntry=0, castorDir=None):
        ts = TStopwatch()
        counter = 1
        MaxEntries = int(MaxEntries)
        for S in self.SampleNames:

            # measure time of execution

            ts.Start()

            counter = counter+1
            TheSample=self.Group.Samples[S]
            print "RunHandler: looping over sample nr: " + str(counter) + " ["+S+", nfiles="+str(len(TheSample.Files))+"]"
            self.Results[S] = {}
            gd = {}
            gd['Sample'] = S
            lastEntry = firstEntry + MaxEntries - 1
            if MaxEntries < 0:
                lastEntry = 'LastEntry'
            if firstEntry==0 and MaxEntries==-1:
                SampleUniqueName=S
            else:
                SampleUniqueName = S+"_"+str(firstEntry)+"-"+str(lastEntry)
            gd['SampleUniqueName'] = SampleUniqueName


            # examples:
            # firstEntry = 0,   MaxEntries = 50 => want to process evts 0 to 49
            # firstEntry = 50,  MaxEntries = 50 => want to process evts 50 to 99
            # firstEntry = 100, MaxEntries = 50 => want to process evts 100 to 149


##            # copy old values to newSample: (think of using a copy-constructor instead )
##	    if isinstance(TheSample, Sample.SusySample):
##                newSample = SampleHandler.SusySample(S)
##            elif isinstance(TheSample, AODSample.AODSample):
##                newSample = AODSample.AODSample(S)
##            else:
##                newSample = SampleHandler.Sample(S)

##            newSample.Copy( TheSample )
##            newSample.AddFilesToChain()

            newSample = TheSample
            [tot_evts, res] = self.Algo.Loop(newSample, MaxEntries, gd, firstEntry)

            ts.Stop()
            print "Spent time :"
            print ts.Print()

            print "tot processed evts. = %i => rate = %5.2f Hz (real time)" % ( tot_evts, tot_evts / ts.RealTime() )
            timePrefixName = "Timing_"+self.Algo.name+"_"
            res[timePrefixName+'_realTime'] = ts.RealTime()
            res[timePrefixName+'_cpuTime'] = ts.CpuTime()
            res[timePrefixName+'_evts'] = tot_evts
            ts.Reset()

            if gd.has_key("WriterAlgorithm"):
                for i in xrange( len(newSample.Files) ):
                    newSample.Files.pop(0)
                    pass
                newSample.Files = [ gd["WriterAlgorithm"].split('/')[-1] ]
                print newSample.Files

            # add files to TChain:
##            newSample.AddFilesToChain()

            # newSample.resultTObjects.clear()
            for name in res:
                if name != "Statistics":
                    # print Result["Results"][Sample].GetMean()
                    gROOT.cd("/")
                    if isinstance(res[name], TObject ):
                        newSample.resultTObjects[name] = res[name].Clone()
                    else:
                        newSample.results[name] = res[name]
                        pass
                    pass
                pass
            
            self.Results[SampleUniqueName] = newSample

            if castorDir and gd.has_key("WriterAlgorithm"):
                #if os.popen3('nsls '+castorDir)[2].readlines(): #exists?
                if True:
                    os.system('rfmkdir -p '+castorDir)
                    os.system('rfchmod 775 '+castorDir)
                file=gd["WriterAlgorithm"]
                filename=file.split('/')[-1]
                #os.system('ls -l '+tupleDir)
                os.system('rfcp '+file+' '+castorDir)
                os.system('rm '+file)
                os.system('rfchmod 775 '+castorDir+'/'+filename)
                print 'New ntuple:',castorDir+'/'+filename
                newSample.ChangeNtupleDir( castorDir )
                pass

            if doPickle:
                print "doing pickling: "+pickleDir
                picklename=self.pickleSample(SampleUniqueName, pickleDir)
                if castorDir:
                    os.system('rfcp '+picklename+' '+castorDir)
                    os.system('rfchmod 775 '+castorDir+'/'+(picklename.split('/')[-1]))
                    pass
                pass
            # print cut flow
            print newSample.name,"PrintCutEff(applyAllPreviousCuts=False):"
            newSample.PrintCutEff(applyAllPreviousCuts=False)
            

        return

    def pickle(self, directory = './'):

        if not os.path.isdir(directory):
            os.mkdir(directory)

        for S in self.Results:
            self.pickleSample(S, directory)
            #Results[S].pickle(directory+'/'+S+'.pickled.root')


    def pickleSample(self, sampleName, directory = './'):
        if not os.path.isdir(directory):
            os.system("mkdir -p "+directory)
        self.Results[sampleName].pickle(directory+'/'+sampleName+'.pickled.root')
        return directory+'/'+sampleName+'.pickled.root'

    def CompareResults(self, Samples, ObjectName,Attrib=None,doLegend=True,Titles=None):

        Objects=[]
        for sample in Samples:
            Objects+=[self.Results[sample].resultTObjects[ObjectName]]

        dummySH=SampleHandler.SampleHandler()
        if not Attrib:
            Attrib=dummySH.DefaultAttributes

        dummySH.NiceDraw(Objects,Attrib,doLegend,Titles)

        return Objects

                  
    def RenameHists(self):
        for sample in self.Results:
            for ObjectName in self.Results[sample].resultTObjects:
                aname=self.Results[sample].resultTObjects[ObjectName].GetName()
                self.Results[sample].resultTObjects[ObjectName].SetName(sample+"_"+aname)
            

        
