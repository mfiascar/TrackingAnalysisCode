# ------------------------------------------------------------- #
# package: SPyRoot                                              #
# file: OverlapRemoval                                          #
# classes: OverlapRemoval                                       #
# purpose: remove objects in ThisEntryData based on eta,phi     #
#                                                               #
# authors: Till Eifert <Till.Eifert@cern.ch> - U. of Geneva     #
#                                                               #
# File and Version Information:                                 #
# $Id: OverlapRemoval.py,v 1.5 2008/01/28 13:31:37 eifert Exp $
# ------------------------------------------------------------- #


from TTreeAlgorithm import *
from ROOT import *
from array import array

class OverlapRemoval(TTreeAlgorithm):
    def __init__(self, name,
                 target_eta, target_phi,
                 ref_eta, ref_phi,
                 delta_R_min,delta_R_max, # range for which target obj are removed !
                 target_vars_remove = [] ):

        self.target_eta = target_eta
        self.target_phi = target_phi
        self.ref_eta = ref_eta
        self.ref_phi = ref_phi
        self.delta_R_min = delta_R_min
        self.delta_R_max = delta_R_max
        self.target_vars_remove = target_vars_remove
        self.name = name
        
        Branches=[]
        #Branches  = [target_eta, target_phi, ref_eta, ref_phi]
        #Branches += target_associated_vars

        # print self.name, " In overlap removal -init"

        TTreeAlgorithm.__init__(self,name,Branches)


    def execute(self,T,AllEntriesData,GlobalData,ThisEntryData):

        # print self.name, " In overlap removal - execute"

        # if no reference objects available, skip this event
        if len(ThisEntryData[self.ref_eta]) == 0 :
            return True

        indices_to_remove = []
        #indices_to_remove = array('i',[]) # sort does not work ...
        # loop over each target object and look at it's eta and phi ...
        for i in xrange(len(ThisEntryData[self.target_eta])):

            target_eta = ThisEntryData[self.target_eta][i]
            target_phi = ThisEntryData[self.target_phi][i]

            # print self.name, " target # %i : eta=%f and phi=%f" % (i, target_eta, target_phi)

            # loop over reference objects to find possible matches ...
            for j in xrange(len(ThisEntryData[self.ref_eta])):

                ref_eta = ThisEntryData[self.ref_eta][j]
                ref_phi = ThisEntryData[self.ref_phi][j]

                delta_eta = fabs( ref_eta - target_eta )
                delta_phi = fabs(ref_phi - target_phi)
                if delta_phi > TMath.Pi():
                    delta_phi = 2.*TMath.Pi() - delta_phi

                delta_R = sqrt( delta_phi**2 + delta_eta**2 )

                # print self.name," reference # %i : eta=%f and phi=%f -> delta_eta=%f, delta_phi=%f, and delta_R=%f" % (j, ref_eta, ref_phi,
#                                                                                                            delta_eta, delta_phi, delta_R)

                # if delta_r in range [min, max] -> remove target object
                if delta_R >= self.delta_R_min and delta_R <= self.delta_R_max :
                    # print self.name," going to remove target objects (%s ...) from list!" % (self.target_vars_remove[0])
                    indices_to_remove.append( i ) # += [i]
                    # done with this target obj (it's removed already!)
                    break

        #print self.name," obj to remove",len(indices_to_remove), " old length",len(ThisEntryData[self.target_eta])

        # loop over each target objects to remove (in reverse order to not mess up the index)
        indices_to_remove.sort(reverse=True)
        for i in indices_to_remove:
            for var in self.target_vars_remove:
                #try:
                if type( ThisEntryData[ var ] ) is list or type( ThisEntryData[ var ] ) is array:
                    ThisEntryData[ var ].pop( i )
                elif type( ThisEntryData[ var ] ) is int:
                    ThisEntryData[ var ] -= 1
                else:
                    print "ERROR, don't know what do to with target variable: %s" % var
                    pass
                #except IndexError:
                #    print self.name,"ERROR, var=",var," index=",i


        #print self.name," new length",len(ThisEntryData[self.target_eta])

        return True
