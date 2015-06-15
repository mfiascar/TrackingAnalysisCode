########################################################
#
# Make plot for layout of magnets and collimator
#
# input files: twiss_b1--thick.tfs, CollPositions.b1.dat
########################################################

import glob

try:
    inputDir
except NameError:
    inputDir = "/home/mfiascar/Physics/Accelerator/Simulation/7TeVStandard_commonfiles"

if inputDir[len(inputDir)-1]!="/":
    inputDir = inputDir+"/"

try:
    beam
except NameError:
    beam=1

LHCring = 26659.
deltaS = 0.1

h_coll_postion = TH1F("h_coll_position","h_coll_position",int(LHCring/deltaS),0.,LHCring)
h_dipole_postion = TH1F("h_dipole_position","h_dipole_position",int(LHCring/deltaS),0.,LHCring)
h_quadrupole_postion = TH1F("h_quadrupole_position","h_quadrupole_position",int(LHCring/deltaS),0.,LHCring)


# From CollPositions files get location of collimators
inputCollPosition = inputDir + "CollPositions.b%i.dat" %beam
f = open(inputCollPosition)
lines = f.readlines()
f.close()
collPos = {}
for l in lines:
    parts = l.split()
    if len(parts) >2:
        if parts[0].find("Ind") >=0:
            continue
        collPos[parts[1]] = [float(parts[2])]
print "Size of collPos vector: %i" %( len(collPos))

#find lengh of collimator
fsummary = open(inputDir + "coll_summary.b%i.dat" %beam,'r')
sum_lines = fsummary.readlines()
fsummary.close()
for l in sum_lines:
    if l.find("icoll") >=0 : #exclude header line
        continue
    s_parts = l.split()
    if len(s_parts) < 4:
        continue
    s_lenght = float(s_parts[6])
    collPos[s_parts[1]] += [ s_lenght]

toBeDeleted = []
for i in collPos:
    if len(collPos[i])<2:
        toBeDeleted += [i]

for i in toBeDeleted:
    del collPos[i]
print "Size of collPos vector:  after cleaning %i" %( len(collPos))
print ""
print "Collimators:"
for i in collPos:
    print "coll: ",i, ":", collPos[i]
    collStart = collPos[i][0]
    nbins = int(collPos[i][1]/deltaS+0.00001)
    for r in range(0,nbins):
        #print "Filling bin %i" %(h_coll_postion.FindBin(collStart)+r)
        h_coll_postion.SetBinContent(h_coll_postion.FindBin(collStart)+r,1.)
print ""



#Now look at location of dipoles and quadrupoles
inFileName =  []
os.chdir(inputDir)
for file in glob.glob("*thick.b%i*tfs" %beam):
    inFileName += [file]
if len(inFileName) ==0 :
    for file in glob.glob("*b%i*thick*tfs" %beam):
        inFileName += [file]
if len(inFileName) ==0 :
    print "ERROR: No thick file found"
if len(inFileName) > 1:
    print "more than one thick files found, using the first one", inFileNam[0]
inputMagnets = inputDir + inFileName[0]
print "Input twiss file: %s" %inputMagnets

fi = open(inputMagnets)
lines = fi.readlines()
fi.close()
#first find column for name, s pos and len
nfound = 0
for l in lines:
    if len(l) < 100:
        continue
    parts = l.split()
    ncol = {}
    pcounter = 0
    for p in parts:
        if p=="*":
            continue
        if (p.find("NAME")==0) and not ('NAME' in ncol):
            ncol['NAME']= pcounter
            nfound+=1
        if (p.find("S")==0) and not ('S' in ncol):
            ncol['S']= pcounter
            nfound+=1
        if (p.find("L")==0) and not ('L' in ncol):
            ncol['L']= pcounter
            nfound+=1
        pcounter +=1
        if nfound==3:
            break
    if nfound==3:
        break
print "Found columns: name %i, s %i, len %i" %(ncol['NAME'],ncol['S'],ncol['L'])

counter=0
for l in lines:
    counter+=1
    #if counter > 200:
    #    break
    isMQ = l.find("MQ")
    isMB = l.find("MB")
    if isMB < 0 and isMQ < 0:
        continue
    #if  (isMB >= 0 and isMB < 4) or (isMQ >= 0 and isMB<4):
    parts = l.split()
    #print "Part %s found dipole? %i found quadrupo? %i" %(parts[0],isMB,isMQ)
    name = parts[ncol['NAME']]
    s_pos = float(parts[ncol['S']])
    s_len = float(parts[ncol['L']])
    s_nbins = int(s_len/deltaS+0.00001)
    for r in range(0,s_nbins):
        if (isMB>=0):
            #print "Filling dipole"
            h_dipole_postion.SetBinContent(h_dipole_postion.FindBin(s_pos)+r,1.)
        if (isMQ>=0):
            #print "Filling quadrupole"
            h_quadrupole_postion.SetBinContent(h_quadrupole_postion.FindBin(s_pos)+r,1.)

outfile = TFile(inputDir +"Layout.root","recreate")
outfile.cd()
h_coll_postion.Write()
h_dipole_postion.Write()
h_quadrupole_postion.Write()
outfile.Close()
