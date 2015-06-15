import ROOT
import os,sys
from root_pickle import dump_root
from root_pickle import load_root

def save(fname=None):
    if not fname:
        fname=str(os.getpid())
    hlist = []
    for i in range (10):
        name = 'h%d' % i
        hlist.append (ROOT.TH1F (name, name, 10, 0, 10))

    hlist.append (ROOT.TH2F("hist2D","hist2D",10,0,10,10,0,10))
    hlist.append (ROOT.TH3F("hist3D","hist3D",10,0,10,10,0,10,10,0,10))
    nbins=2
    my_bins=[0,1,2]
    bins = array('d',my_bins )
    hlist.append (ROOT.TH3F("hist3Dbis","hist3Dbis",nbins,bins,nbins,bins,nbins,bins))
    hlist.append (ROOT.TGraphAsymmErrors() )

    tmpFileName = "/tmp/pickleRootTest"+fname+".root"
    print "pickleRootTest: testing with file %s" % tmpFileName

    dump_root (hlist, tmpFileName)

def delete(fname=None):
    if not fname:
        fname=str(os.getpid())
    
    tmpFileName = "/tmp/pickleRootTest"+fname+".root"
    
    print "pickleRootTest: Deleteing %s" % tmpFileName
    
    os.remove(tmpFileName)

def load(fname=None):
    if not fname:
        fname=str(os.getpid())
    tmpFileName = "/tmp/pickleRootTest"+fname+".root"
    hlist = load_root (tmpFileName)
    return hlist
