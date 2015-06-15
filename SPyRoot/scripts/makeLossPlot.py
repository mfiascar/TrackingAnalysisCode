from array import array
from os import popen

LHCring = 26659.
deltaS = 1.


try:
    inputDir
except NameError:
    inputDir = "/Users/mfiascar/Physics/Accelerator/Simulations/test/"

try:
    outputDir
except NameError:
    outputDir = inputDir

# From CollPositions files get location of collimators
inputCollPosition = inputDir + "CollPositions.b1.dat"
f = open(inputCollPosition)
lines = f.readlines()
f.close()
collPos = {}
icollPos = {}
for l in lines:
    parts = l.split()
    if len(parts) >2:
        if parts[0].find("Ind") >=0:
            continue
        collPos[parts[1]] = [int(parts[0]),float(parts[2])]
        icollPos[parts[0]] = float(parts[2])
print "Size of collPos vector: %i, %i" %( len(collPos), len(icollPos))
print collPos
print icollPos


# for variable bin sizes (eg. if you want to have a bin of size = collimator size)
#bins = [ 0. ]

#for i in range(1,27000):
#    s = deltaS*i
    #check if we are close to a collimator
    #for coll in collPos:
    #    if fabs(s-coll) < deltaS
#my_bins = array('d', bins)

#create histogram for nabs:
h_coll = TH1F("h_collimator_losses","h_collimator_losses", int(LHCring/deltaS), 0., LHCring)
h_coldlosses = TH1F("h_cold_losses","h_cold_losses", int(LHCring/deltaS), 0., LHCring)
h_coll_fromFluka = TH1F("h_collimator_lossesFromFluka","h_collimator_lossesFromFluka", int(LHCring/deltaS), 0., LHCring)

#Read in coll_summary.dat - note: need to loop over all sub-directories
fsummary = open(inputDir + "coll_summary.dat")
sum_lines = fsummary.readlines()
fsummary.close()
print "Reading coll_summary"
print sum_lines[0]
for l in sum_lines:
    if l.find("icoll") >=0 : #exclude header line
        continue
    #find s position corresponding to collimator
    print l
    s_parts = l.split()
    if len(s_parts) < 4:
        continue
    s_ind = collPos[s_parts[1]][0]
    if not s_ind == int(s_parts[0]):
        print "ERROR: collname ",s_parts[1]," has index ", s_ind ," in CollPositions and ", int(s_parts[0])," in Coll_Summary "
        continue
    s_pos = collPos[s_parts[1]][1]
    # now we can fill the histogram:
    print "Filling coll %s, icoll %i position %f with weight %f" %(s_parts[1], int(s_parts[0]), s_pos, float(s_parts[3]))
    h_coll.Fill(s_pos, float(s_parts[3]))

#Read in impacts_real.root
fluka = TFile.Open(inputDir + "impacts_real.root")
tf = fluka.Get("ntuple")
for entry in range(tf.GetEntries()):
    tf.GetEntry(entry)
    if tf.nabs !=4:
        continue
    s_pos = icollPos["%s" %int(tf.icoll)]
    h_coll_fromFluka.Fill(s_pos)


#Read in LPI_BLP_out.s: info about particles lost in cold losses
flpi = TFile.Open(inputDir + "LPI_BLP_out.s.root")
t = flpi.Get("ntuple")
for entry in range(t.GetEntries()):
    t.GetEntry(entry)
    #print "particle %i lost at s %f" %(t.np,t.s)
    h_coldlosses.Fill(t.s)

    
fout = TFile(outputDir + "StandardSetup_losses.root","recreate")
fout.cd()
h_coll.Write()
h_coldlosses.Write()
h_coll_fromFluka.Write()
fout.Close()
