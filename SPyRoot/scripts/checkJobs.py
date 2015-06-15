#!/usr/bin/env python
#
# usage: checkJobs <directory> 
#

from os import popen
import sys

mydirName = "run"

outFiles = ["collgaps","Coll_Scatter_real","LPI_BLP_out","coll_summary","first_imp_average","impacts_all_real","survival","dist0","efficiency","efficiency_dpop","FLUKA_impacts","impacts_real"]


##main

if __name__ == "__main__":
    
    if len(sys.argv) < 2:
        print 'usage', sys.argv[0], ' <directory> '
        sys.exit()
        pass

    directories = popen("ls %s | grep '%s'" % (sys.argv[1],mydirName)).readlines()

    print "Found %i directories" %len(directories)

    for di in directories:
        #print "checking directory: %s" %(di)

        missing = []

        foundFiles= popen("ls %s " % (sys.argv[1]+"/"+di)).readlines()

        for of in outFiles:
            found = False
            for f in foundFiles:
                if f.find(of) >=0 :
                    found = True
                    break
            if not found: missing += [of]
        
        if len(missing)>0:
            
            print "ERROR: missing files in dir %s" %(di)
            print "       -> missing files:", missing
            print ""


        
