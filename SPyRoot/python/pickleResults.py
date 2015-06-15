# ------------------------------------------------------------- #
# package: SPyRoot                                              #
# file: pickleResults                                           #
# classes: -                                                    #
# purpose: load, save methods for the outcome of a user-defined #
#          analysis                                             #
#                                                               #
# authors: Amir Farbin <Amir.Farbin@cern.ch> - CERN             #
#          Till Eifert <Till.Eifert@cern.ch> - U. of Geneva     #
#          Jamie Boyd  <Jamie.Boyd@cern.ch>  - CERN             #
#                                                               #
# File and Version Information:                                 #
# $Id: pickleResults.py,v 1.2 2007/01/29 14:45:07 eifert Exp $
# ------------------------------------------------------------- #




from os import popen
import ROOT
#from root_pickle import dump_root
#from root_pickle import load_root
import root_pickle


def load(path="./", require = ""):
    if path[-1] != '/':
        path += '/'

    if require == "":
        fileNames = popen('ls %s' %(path)).readlines()
    else:
        fileNames = popen('ls %s | grep %s' %(path,require)).readlines()

    fileNames.sort()

    result = {}

    for file in fileNames:
        #print "File: ", file
        entries = file.split(".root")
        #entries2 = entries[0].split("_")
        #Sample = entries2[len(entries2)-1]
        Sample = entries[0]
        print Sample
        #result[Sample] = load_root(path+file[0:-1], 0)
        file = ROOT.TFile(path+file[0:-1])
        result[Sample] = root_pickle.load( file, 0)
        file.Close()
    return result


def save(Results, OutFileNameBase = "./myAnalysis_"):
    # save 1 Sample into 1 root file, otherwise not all THistograms are saved ...
    # maybe because of the same names ?!?
    for Sample in Results:
        root_pickle.dump_root (Results[Sample], OutFileNameBase+Sample+'.root')
