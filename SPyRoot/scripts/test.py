inputDir = '/home/mfiascar/Physics/Accelerator/Simulation/Outputs/'

# From CollPositions files get location of collimators
inputCollPosition = inputDir + "clean_input/CollPositions.b1.dat"
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

#find lengh of collimator
for inDir in os.listdir("%s" %inputDir):
    if inDir.find(".root")>=0:
        continue
    if inDir.find("clean_input") >=0 :
        continue
    print "Found file for coll lengh"
    fsummary = open(inputDir + inDir+ "/coll_summary.dat",'r')
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
    break

print ""
print "Collimators:"
for i in collPos:
    print "coll: ",i, ":", collPos[i]


# for variable bin sizes (eg. if you want to have a bin of size = collimator size)
#bins = [ 0. ]

deltaS = 1.
LHCring = 26659.

#for i in range(1,27000):
#    s = bins[len(bins)-1] 
#    #check if we are close to a collimator
#    foundCloseColl = False
#    for coll in collPos:
#        if fabs(s-collPos[coll][1]) < deltaS:
#            bins += [ collPos[coll][1], collPos[coll][1]+ collPos[coll][2]]
#            foundCloseColl = True
#    if not foundCloseColl:
#        bins += [ s + deltaS ]
#    if bins[len(bins)-1] >= LHCring:
#        break

#print "Bins are:"
#print bins
#my_bins = array('d', bins)


warm=[0.0,22.5365,54.853,152.489,172.1655,192.39999999999998,199.48469999999998,224.3,3095.454284,3155.628584,3167.740084,3188.4330840000002,3211.4445840000003,3263.867584,3309.9000840000003,3354.9740840000004,3401.005584,3453.4285840000002,3476.440084,3494.065584,3505.885284,3568.318584,6405.4088,6457.9138,6468.7785,6859.513800000001,6870.3785,6923.5338,9735.907016000001,9824.730516000001,9830.832016,9861.730516,9878.732016,9939.985516,9950.548016,10043.462016,10054.024516,10115.278016,10132.279516,10163.970516,10170.072016,10257.603016,13104.989233,13129.804533,13136.889233,13157.123733,13176.800233,13271.647233,13306.752733,13351.825733,13386.931233000001,13481.778233000001,13501.454732999999,13522.784533,13529.869233,13554.684533,16394.637816,16450.871316,16456.972816,16487.271316000002,16493.372816,16830.871316,16836.972815999998,16867.271316,16873.372816,16928.294816,19734.8504,19760.6997,19771.5644,20217.9087,20228.773400000002,20252.9744,23089.979683999998,23138.576984,23150.396684,23171.375484,23194.386984,23246.809984,23292.842484,23337.915484,23383.947984,23436.370984,23459.382483999998,23480.082484,23492.193984,23553.115984,26433.4879,26458.3032,26465.387899999998,26486.7177,26506.3942,26601.2412,26636.346700000002,26658.883199999997]

newwarm = []
for w in range (len(warm)-1):
    if (w%2)==0:
        myw = [ warm[w],warm[w+1] ]
        newwarm += [ myw ]
    else:
        continue
print newwarm



        

