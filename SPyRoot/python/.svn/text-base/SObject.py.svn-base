# ------------------------------------------------------------- #
# package: SPyRoot                                              #
# file: SObject.py                                              #
#                                                               #
# authors: 
#          Till Eifert    <Till.Eifert@cern.ch> - CERN          #
#                                                               #
# created: October 2009
# ------------------------------------------------------------- #

from copy import deepcopy
import root_pickle
from ROOT import TFile, gROOT

class SObject(object):
    """
    Base class for some basic functionality -> pickling, printing
    """
    def __init__(self, name):

        self.name = name
        self.className = 'SObject'
        self.moduleName = 'SObject'
        self.pickleFileName = ''
        self.listPickleVars = [
            'name',
            'className',
            'moduleName',
            ]


    def __str__(self):
        return super.__str__(self) + "\n"+self.__baseStr__()

    def __baseStr__(self):
        theString = ""
        for v in self.listPickleVars:
            theString += "  - %s : %s\n" % (v, eval("self."+v))
            pass
        return theString.rstrip("\n")
    
    def Print(self):
        """
        print information about this object
        """
        print "---  Print()"
        theStr = self.__baseStr__()
        print theStr
        pass

    def pickle(self, fileName = '') :
        """
        Pickling is python's way of saving objects on disk.
        """
        if fileName == '':
            fileName = self.pickleFileName
            #fileName = './'+self.name+'.pickled.root'
            if fileName == '':
                print "ERROR, default pickle file name not set! will do nothing"
                return
            pass
        
        obj = {}

        for v in self.listPickleVars:
            obj[v] = eval("self."+v)
            pass
        #of = file(fileName, "w")
        #import pickle
        #pickle.dump( obj, of)
        #of.close()
        root_pickle.dump_root ( obj, fileName)
        pass

    def unpickle(self, fileName = '', quiet=False):
        """
        Unpickle (load) a Sample class from disk into memory.

        fileName             : pickled file (path + file name)
        quite                : print debug messages ?
        """ 
        if fileName == '':
            fileName = './'+self.name+'.pickled.root'

        fileName = fileName.strip()

        self.pickleFileName = fileName
        
        theFile = TFile( fileName )
        if not theFile:
            print " ERROR loading root file"
            return

        
        res = root_pickle.load( theFile, 0)


        theList = self.listPickleVars
        
        # add variables and histograms
        for v in theList:
            if v.find("resultTObjects") != -1 and res.has_key("resultTObjects"):
                for obj in res["resultTObjects"]:
                    try:
                        res["resultTObjects"][obj]
                    except NameError:
                        print "can't access object: %s in resultTObjects dict ?!?" % obj
                        continue
                    gROOT.cd("/")
                    # print "hist = %s" % hist
                    self.resultTObjects[obj] = res["resultTObjects"][obj].Clone()
            else:
                try:
                    exec("self."+v+" = deepcopy(res[v])")
                except AttributeError:
                    if not quiet:
                        print "warning : this class has no variables with the name: %s  --> go on w/o setting this variable" % (v)
                except KeyError:
                    if not quiet:
                        print "warning : the variable %s was not found in the pickled result --> go on w/o setting this variable" % (v)
                        pass
                    pass
                pass
            pass

        del res
        theFile.Close()
        del theFile
        pass
    
