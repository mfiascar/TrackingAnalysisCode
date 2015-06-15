try:
    inputDir
except NameError:
    inputDir = "/Users/mfiascar/Physics/Accelerator/Simulations/test/"

try:
    outputDir
except NameError:
    outputDir = inputDir

try:
    nparticle
except NameError:
    nparticle = 101

files = [
    'Coll_Scatter',
    'FLUKA_impacts_all',
    'FLUKA_impacts',
    'impacts_real',
    'Coll_Scatter_real']

print "-----------------------------------"
print "Checking particle : %i" %nparticle
print "-----------------------------------"

for name in files:
    f = TFile.Open(inputDir + name + ".root")
    t = f.Get("ntuple")
    print "Checking file: %s" %name
    t.Scan("iturn:icoll:nabs","np==%i"%nparticle)
    f.Close()
    print ""

