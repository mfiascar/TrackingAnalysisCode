from ROOT import *

class amplitude(object):

    def __init__(self, betax, betay, alfax, alfay, sigx, sigy):

        self.betax = betax
        self.betay = betay
        self.alfax = alfax
        self.alfay = alfay
        self.sigx = sigx
        self.sigy = sigy

        return

    def _print(self):

        print "Settings: "
        print "Betax = ", self.betax, ", Alfax = ", self.alfax, ", Sigx = ", self.sigx
        print "Betay = ", self.betay, ", Alfay = ", self.alfay, ", Sigy = ", self.sigy

        return

    def calcAmplitude(self,x,y,xp,yp):
        
        amplx = sqrt((x*1e-3/self.sigx)**2 + ( (self.alfax*x*1e-3+ self.betax*xp*1e-3)/self.sigx )**2)
        amply = sqrt((y*1e-3/self.sigy)**2 + ( (self.alfay*y*1e-3+ self.betay*yp*1e-3)/self.sigy )**2 )
        amplit = sqrt(amplx**2 + amply**2)
        
        return amplit

    def calcAmplitude_noangle(self,x,y):

        amplx = sqrt((x*1e-3/self.sigx)**2 + ( (self.alfax*x*1e-3)/self.sigx )**2)
        amply = sqrt((y*1e-3/self.sigy)**2 + ( (self.alfay*y*1e-3)/self.sigy )**2 )
        amplit = sqrt(amplx**2 + amply**2)

        return amplit

    def calcAmplitude_oneterm(self,x,y):

        amplx = x*1e-3/self.sigx
        amply = y*1e-3/self.sigy
        amplit = sqrt(amplx**2 + amply**2)

        return amplit
        
