import sys
import os
import time
from subprocess import Popen, call, PIPE
#from ROOT import *

class RunMultiple():
    def __init__(self,
                 Command="PyRootBatch",
                 ConstantArg="",
                 VariableArgs=[],
                 NSimultaneous=8,
                 Wait=10,
                 OutDir="."
                 ):

        # remember output var name:
        self.Command=       Command      
        self.ConstantArg=  ConstantArg 
        self.VariableArgs=  VariableArgs 
        self.NSimultaneous= NSimultaneous
        self.Wait=          Wait         
        self.OutDir=OutDir

    def NRunning(self,script_name):
        try:
            p1 = Popen(["ps", "aux"], stdout=PIPE)
            p2 = Popen(["grep", script_name], stdin=p1.stdout, stdout=PIPE)
            output = p2.communicate()[0]
            return len(output.split("\n"))-2
        except Exception, e:
            print >>sys.stderr, "Execution failed:",e
            return 10000

    def NiceWait(self):
        print "Waiting", str(self.Wait), "seconds ",
        for i in xrange(0,self.Wait):
            print ".",
            sys.stdout.flush()
            time.sleep(1)
        print

    def Run(self):
        n=0
        
        if not(os.path.isdir(self.OutDir)):
            os.mkdir(self.OutDir)

        while n<len(self.VariableArgs):
            RN=self.NRunning(self.Command)
            while(RN<=self.NSimultaneous and n<len(self.VariableArgs)):
                RN=self.NRunning(self.Command)
                print  "Running (",RN,"Currently Running ) "
                command="nohup "+self.Command+" "+self.ConstantArg+" "+self.VariableArgs[n]+ " > "+self.OutDir+"/"+self.VariableArgs[n].replace(' ','')+".log 2>&1 &"
                print n," Running: "+command
                os.system(command)
                time.sleep(1)
                n+=1
            if n<len(self.VariableArgs):
                self.NiceWait()
                            

    def Submit(self):
        n=0
        
        if not(os.path.isdir(self.OutDir)):
            os.mkdir(self.OutDir)

        while n<len(self.VariableArgs):
            command="~/Analysis/submit "+self.OutDir+"/"+self.VariableArgs[n].replace(' ','')+".log "+self.Command+" "+self.ConstantArg+" "+self.VariableArgs[n]
            print n,": Running: "+command
            os.system(command)
#            time.sleep(1)
            n+=1
#            if n<len(self.VariableArgs):
#                self.NiceWait()



        



