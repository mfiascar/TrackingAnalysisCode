
try:
    inputDir
except NameError:
    inputDir = "/home/mfiascar/Physics/Accelerator/Simulation/HL-LHC/v1.0/HorizB1/test"

if inputDir[len(inputDir)-1]!="/":
    inputDir = inputDir+"/"

infile = open(inputDir + "/betafunctions.dat","r")

countColl = []

lines = infile.readlines()    
ntitle = 1
for i in range(ntitle, len(lines)):
    iline = lines[i].split()
    name =  iline[1]
    if name.find("t")==0:
        countColl+= [name]

print "Found %i collimators", len(countColl)
print countColl


