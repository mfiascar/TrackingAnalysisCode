
import argparse
import sys
from ROOT import *

parser = argparse.ArgumentParser(description=
'Make ntuples from .dat files for one job',
formatter_class=argparse.RawTextHelpFormatter)

parser.add_argument('--inputDir', action='store', type=str,
                    help= 'Specify the input directory \n\
EX: --inputDirectory \'./\' ')

parser.add_argument('--outputDir', action='store', type=str,
                    help= 'Specify the output directory \n\
EX: --outputDirectory \'./\' ')

args=parser.parse_args()

if args.inputDir:
    inputDir = args.inputDir
else:
    inputDir = '/home/mfiascar/Physics/Accelerator/Simulation/OutputTests/run0057/'

if inputDir[len(inputDir)-1]!="/":
    inputDir = inputDir+"/"

if args.outputDir:
    outputDir = args.outputDir
else:
    outputDir = inputDir

if outputDir[len(outputDir)-1]!="/":
    outputDir = outputDir+"/"

print "in Ntuple making"
print "inputDir: %s, outputDir: %s" %(inputDir, outputDir)

ntuples = {
    'FirstImpacts':'np:iturn:icoll:nabs:s_imp:s_out:x_in:xp_in:y_in:yp_in:x_out:xp_out:y_out:yp_out',
    'dist0':"x:xp:y:yp:s:E",
    'Coll_Scatter_real':"icoll:iturn:np:nabs:dp:dxp:dyp", #remove for FCC
    'Coll_Scatter':"icoll:iturn:np:nabs:dp:dxp:dyp",
    'FLUKA_impacts':"icoll:c_rotation:s:x:xp:y:yp:nabs:np:iturn",
#    'coll_ellipse':"name/I:x/F:y:xp:yp:dEoverE:s:iturn/I:halo:nabs_type",  #add only for halo studies
#    #'FLUKA_impacts_all':"icoll:c_rotation:s:x:xp:y:yp:nabs:np:iturn",
#    'impacts_all_real':"icoll:c_rotation:s:x:xp:y:yp:nabs:np:iturn", #remove for FCC
    'impacts_real':"icoll:c_rotation:s:x:xp:y:yp:nabs:np:iturn",     #remove for FCC
    'LPI_BLP_out.s':"np:iturn:s:x:xp:y:yp:dEoverE:type:turns"        #remove for FCC
    }

for l in ntuples:
    print "Going to open file: %s" %l
    print "ntuple structure: ", ntuples[l]
    print ""
    t = TTree("ntuple","data from .dat file")
    inFileName = inputDir+l+".dat"
    if l == 'LPI_BLP_out.s':
        inFileName = inputDir + 'LPI_BLP_out.s'
    nlines = t.ReadFile(inFileName, ntuples[l])
    f = TFile(outputDir + l+ ".root","recreate")
    t.Write()
    f.Close()

print "DONE makeNtuple"



