# ------------------------------------------------------------- #
# package: SPyRoot                                              #
# file: QueueHandler                                            #
# classes: QueueHandler, GenevaQueueHandler                     #
# purpose: interface to a cluster queing system, maybe at one   #
#          point one can extend this to grids ...               #
#                                                               #
# authors: Till Eifert    <Till.Eifert@cern.ch> - U. of Geneva  #
#                                                               #
# File and Version Information:                                 #
# $Id: QueueHandlers.py,v 1.17 2008/08/05 16:25:00 eifert Exp $
# ------------------------------------------------------------- #


from os import popen

######################################################################################
## QueueHandler class
##
## Descirption: base class to all QueueHandler classes
##
######################################################################################
class QueueHandler:
    def __init__(self, name=""):
        self.name=name

class SSHQueueHandler(QueueHandler):
    def __init__(self, name=""):
        QueueHandler.__init__(self, name)

        self.runSSHSamplesCommand = 'ssh'
        self.sshScript = '/atlas/users/eifert/SPyRoot/qsub-scripts/runSamplesSSH2.sh'

        # SSH mode:
        # 12 login nodes (2 cores, 4GB ram)
        self.nodes = ['atlas001','atlas002','atlas003','atlas004','atlas005','atlas006','atlas007','atlas008','atlas009','atlas010','atlas011','atlas012']
        # 20 worker nodes from 3rd installation (4 cores, 8GB ram)
        # note: these nodes are also used by the std batch system !!!
        self.nodes += ['192.33.218.234','192.33.218.235', '192.33.218.236', '192.33.218.237', '192.33.218.238', '192.33.218.239',
                       '192.33.218.240', '192.33.218.241', '192.33.218.242', '192.33.218.243', '192.33.218.244', '192.33.218.245',
                       '192.33.218.246', '192.33.218.247', '192.33.218.248', '192.33.218.249', '192.33.218.250', '192.33.218.251',
                       '192.33.218.252', '192.33.218.253' ]

        self.nodes_busy = []
        self.maxJobsPerNode = 4

        self.runningJobs = {}

    def submitBatchJobs(self, script, copy_out, copy_out_mask, copy_in, py_inDir,
                        listOfSamples, samplesPerJob, log_dir, queue='long'):

        scriptFileName = script.split("/")[-1]
        from math import ceil
        counter = 0
        njobs = int( ceil( len(listOfSamples)/float(samplesPerJob) ) )
        for i in range(njobs):
            print "job #%i" % i
            # get subset of samples for this job
            samplesToProcess = []
            for j in range(samplesPerJob):
                if len(listOfSamples) > 0:
                    samplesToProcess += [ listOfSamples.pop() ]
                else:
                    break
            samples = ";".join(samplesToProcess)

            # set log file name
            logName = "%s/%s_job%i.log" % (log_dir, scriptFileName, i)

            # find node to submit job:
            node = ""
            for n in self.nodes:
                if self.nodes_busy.count(n) < self.maxJobsPerNode:
                    node = n
                    self.nodes_busy += [n]
                    break

            if node=="":
                print "no more free nodes! will stop submission..."
                break

            parameters = "'%s' '%s' '%s' '%s' '%s' '%s'" % (script, copy_out, copy_out_mask, copy_in, py_inDir, samples)

            str2exec = '%s %s \"%s %s &>! %s\" &>! /dev/null  &' % (self.runSSHSamplesCommand, node, self.sshScript, parameters, logName)
            print str2exec
            result = popen( str2exec ).readlines()
            counter += 1
            # monitoring add all jobs
            #self.runningJobs[s] = result[0].strip()

        print "Submitted %i jobs to the geneva batch system" % (counter)




class GenevaQueueHandler(QueueHandler):
    def __init__(self, name=""):
        QueueHandler.__init__(self, name)

        self.qsubCmd = 'qsub -q '
        self.runSamples = '/atlas/users/eifert/SPyRoot/qsub-scripts/runSamples.sh'
        self.runningJobs = {}


    def submitBatchJobs(self, script, copy_out, copy_out_mask, copy_in, py_inDir,
                        listOfJobs, log_dir, queue='long', batchScript=''):

        scriptFileName = script.split("/")[-1]
        runScript = self.runSamples
        if not batchScript == '':
            runScript = batchScript
        #from math import ceil
        counter = 0

        #njobs = int( ceil( len(listOfSamples)/float(samplesPerJob) ) )
        for j in listOfJobs:

            print "job #%i" % counter
            # get subset of samples for this job
            samplesToProcess = []
            for i in j:
                if type(i) is str:
                    samplesToProcess += [i]
            startEntry=j[1]
            maxEntries=j[2]

            samples = ";".join(samplesToProcess)

            # set log file name
            logName = "%s/%s_job%i.log" % (log_dir, scriptFileName, counter)
            # execution string
            str2exec = "%s %s -o %s -e %s -v script='%s',copy_out='%s',copy_out_mask='%s',copy_in='%s',py_inDir='%s',samples='%s',startEntry='%s',maxEntries='%s' %s" % \
                       (self.qsubCmd, queue, logName+".o", logName+".e", script, copy_out, copy_out_mask, copy_in, py_inDir, samples,
                        startEntry, maxEntries, runScript)

            print str2exec
            result = popen( str2exec ).readlines()
            counter += 1
            # monitoring add all jobs
            s = "%s_job%i" % (scriptFileName, counter)
            self.runningJobs[s] = result[0].strip()

        print "Submitted %i jobs to the geneva batch system" % (counter)


    def monitorJobs(self, runStatus=""):


        print "%-40s %-25s %-10s %-10s" %("SampleName", "Queue ID", "Running", "ExitStatus")
        print "_________________________________________________________________________________________"

        for j in self.runningJobs:

            str2exec = 'qstat -f %s' % (self.runningJobs[j])
            result = popen( str2exec ).readlines()

            running_state = "unknown"
            exit_status = "unknown"
            for line in result:
                if line.find("job_state")!=-1:
                    running_state = line.strip().split(" = ")[1]
                if line.find("exit_status")!=-1:
                    exit_status = line.strip().split(" = ")[1]

            if runStatus=="":
                print "%-40s %-25s %-10s %-10s" % (j, self.runningJobs[j], running_state, exit_status)
            elif running_state == runStatus:
                print "%-40s %-25s %-10s %-10s" % (j, self.runningJobs[j], running_state, exit_status)


    def clearMon(self):
        # do monitoring: clear list of running jobs
        self.runningJobs = {}

    def delJobs(self, jobID=""):

        if jobID == "":
            for j in self.runningJobs:
                str2exec = 'qdel %s' % (self.runningJobs[j])
                result = popen( str2exec ).readlines()
        else:
            str2exec = 'qdel %s' % (jobID)
            result = popen( str2exec ).readlines()


    def addMonitorJobs(self, owner, state=" R "):

        # build grep string:
        grpStr = "| grep %s" % owner
        if state != "":
            grpStr += "| grep %s" % state


        str2exec = 'qstat %s ' % (grpStr)
        result = popen( str2exec ).readlines()

        counter = 0

        for l in result:
            line = l.strip()
            print line
            parts = line.split(" ")

            if parts[0] != "":
                self.runningJobs["job_"+str(counter)] = parts[0]
                counter += 1
