# ------------------------------------------------------------- #
# package: SPyRoot                                              #
#                                                               #
# authors: Till Eifert <Till.Eifert@cern.ch> - U. of Geneva     #
#                                                               #
# File and Version Information:                                 #
# $Id: Statistics.py,v 1.5 2008/10/29 13:28:41 eifert Exp $
# ------------------------------------------------------------- #

from ROOT import TMath
from ROOT import TRandom3
from ROOT import TVectorD
from ROOT import TDecompChol
from ROOT import TMatrixDSym
from ROOT import TMatrixD

# Statistical routines.

# To convert a probability (p-value) into a number of standard deviations (sigma)
# or vice verca, two approaches can be taken:
# 1) Two-tailed Gaussian integral or 2) One-tailed Gaussian integral
# Both ways are implemented! Choose the convention here:
TwoTailedGauss = False

# Description of 1) Two-tailed integral
# std deviation [sigma] : z = normal distribution from -z to z
#
# a quick conversion overview table:
#   Sigma  <=>  p-value         ~ exp. occurrences
#   0.0         0.0               1 out of 1
#   1.0         (1 - 68.27%)    ~ 3 out of 10
#   2.0         (1 - 95.45%)    ~ 5 out of 100
#   3.0         (1 - 99.73%)    ~ 3 out of 1000
#   4.0         (1 - 99.993%)   ~ 6 out of 10^5
#   5.0         (1 - 99.99994%) ~ 6 out of 10^7


# Description of 2) One-tailed integral
# the following methods are based on: hep 0312059 J. Linnemann and references therein
# definitions:
#   1)  null hypothesis (H0), p-value : p = P( s >= observed | assume only background )
#   2)  std deviation [sigma]         : Z = ErrInv( 1 - p )
#       with:  Err(z) = 1/sqrt(2 pi) * int_{-inf}^{z} { exp(-t^2 / 2) dt }
#                     = normal distribution from -inf to z
#
#   Note: this allows for negative Z numbers ! e.g. p=0 corresponds to Z=-inf;
#         p=0.5 corr. Z=0.0;
#
# The two methods below implement the defitions from above in a consistent way, ie
# 2e-6 = GetProbFromSigma( GetSigmaFromProb( 2e-6 ) ).
#
# a quick conversion overview table:
#   Sigma  <=>  p-value         ~ exp. occurrences
#   0.0         0.5               1 out of 2
#   1.0         (1 - 84.1%)     ~ 2 out of 10
#   2.0         (1 - 97.7%)     ~ 2 out of 100
#   3.0         (1 - 99.86%)    ~ 1 out of 1000
#   4.0         (1 - 99.9968%)  ~ 3 out of 10^5
#   5.0         (1 - 99.99997%) ~ 3 out of 10^7


# return sigma for given p-value
def GetSigmaFromProb(p):
    nsigma = 0.0
    if (p > 1.e-16):
        if TwoTailedGauss:
            nsigma = TMath.ErfInverse( 1.0 - 2.0 * p )*TMath.Sqrt(2.0)
        else:
            nsigma = TMath.ErfInverse( 1.0 - p )*TMath.Sqrt(2.0)
    elif ( p > 0. ):
        # use approximation, ok for sigma > 1.5
        u = -2.0 * TMath.Log( p*TMath.Sqrt( 2.*TMath.Pi() ) )
        nsigma = TMath.Sqrt( u - TMath.Log(u) )
    else:
        nsigma = -1

    return nsigma

# return p-value for given sigma
def GetProbFromSigma( nsigma ):
    # works only for ~ -8 < nsigma < 8
    if nsigma < 8.3 and nsigma > -8.3:
        if TwoTailedGauss:
            return 1. - (0.5 + 0.5 * TMath.Erf( nsigma / TMath.Sqrt(2.) ) )
        else:
            return 1. - (TMath.Erf( nsigma / TMath.Sqrt(2.) ) )
    elif nsigma > 0.:
        return RootFinding(GetSigmaFromProb, nsigma, 1e-320, 1e-16, maxIterations=500)
        # use approximation: erf^2 (x) ~= 1 - exp( - x^2 * (4/Pi() + a* x^2)/(1.+a*x^2))
        # where a = - 8. * (Pi() - 3.) / (3. * Pi() * ( Pi() - 4.))
        # precision: at least one correct decimal digit
        # however, works until sigma ~= 8.5 only !!!
        ###############################################################################
        #a = - 8. * (TMath.Pi() - 3.) / (3. * TMath.Pi() * ( TMath.Pi() - 4.))
        #arg = nsigma / TMath.Sqrt(2.)
        #erf = TMath.Sqrt(1.0 - TMath.Exp( - arg**2 * (4./TMath.Pi() + a* arg**2)/(1.+a*arg**2)))
    else:
        return -1.0


# see hep 0312059 J. Linnemann and references therein
def GetSigma_Z0( Nobs, Nb, deltaNb):
    alpha = deltaNb**2 / Nb
    x     = Nobs
    y     = Nb / alpha
    return 2. / TMath.Sqrt(1.+alpha) * ( TMath.Sqrt( x + 3./8.) - TMath.Sqrt(alpha*(y + 3./8.)))

# see hep 0312059 J. Linnemann and references therein
def GetSigma_ZL( Nobs, Nb, deltaNb):
    alpha = deltaNb**2 / Nb
    x     = Nobs
    y     = Nb / alpha
    return TMath.Sqrt(2. * ( x * TMath.Log( x*(1.+alpha)/((x+y)*alpha) ) + y * TMath.Log( y*(1.+alpha)/((x+y)) ) ) )


# see hep 0312059 J. Linnemann and references therein
def GetProb_ZP( Nobs, Nb):
    # get probability from poisson, ignore systematics !
    # p = P(>=Nobs; b) = sum_{j=x}^{inf} { exp(-b) * b^j / j! } = Gamma(x,0,b) / Gamma(x)
    return TMath.Gamma(Nobs, Nb) # TMath.Gamma is normalized already !


# see hep 0312059 J. Linnemann and references therein
# Uniformly Most Powerful test among class of Unbiased tests
# binomial probability with uncertainty on background
def GetProb_UMPU(Nobs, Nb, deltaNb):
    alpha = deltaNb**2 / Nb
    x     = Nobs
    y     = Nb / alpha
    w = alpha/(1. + alpha)
    # p = P(>=Nobs; w, k) = sum_{j=x}^{k} {k! / (j!(k-j)!  * w^j (1-w)^(k-j) }
    # this is analytically equivalent to
    # p = B(w, x, 1+y)/B(x, 1+y)
    p = TMath.BetaIncomplete(w, x, 1+y) # TMath.BetaIncomplete is normalized already !
    return p




def GetProb_toyMC1(Nobs, Nb, deltaNb, toyMC_N=1000000):

    # initialize calc
    seed = 19223451
    rand = TRandom3(seed)
    debugMsg = int(toyMC_N / 5 )
    passedEvts = 0.

    # toy MC event loop
    for i in xrange(toyMC_N):
        # print out status msg
        if i%debugMsg == 0:
            print "%-2.0f %% done" % (i/float(toyMC_N)*100.)

        # use the background uncertainty as a gaussian width
        n_b = rand.Gaus( Nb, deltaNb )
        N_rand = rand.Poisson( n_b )

        # 1-sided
        if N_rand >= Nobs:
            passedEvts += 1
        # 2-sided
##        if N_rand >= N_exp + fabs(N_obs - N_exp) or N_rand <= N_exp - fabs(N_obs - N_exp):
##            passedEvts += 1


    print "%-2.0f %% done" % (i/toyMC_N*100)

    # get results
    p   = passedEvts / toyMC_N
    ep  = TMath.Sqrt( p * (1.0 - p) / toyMC_N )
    nsigma  = GetSigmaFromProb( p )
    ensigma = TMath.fabs( GetSigmaFromProb( p + ep ) - nsigma )

    print "-- Results of toy MC"
    print "-- Nexp (bkg), Nobs : %4.2f, %4.2f" % (Nb, Nobs)
    print "-- accepted %i out of %2.0E events " % (passedEvts, toyMC_N)
    print "-- p-value : %-10.4E +- %-5.2E" % (p, ep)
    print "-- signifiance [sigma] : %-5.3f +-  %-5.3f" % (nsigma, ensigma)



# Root finding using Brents algorithm; taken from CERNLIB function RZERO
def RootFinding( function, refValue, rootMin, rootMax, maxIterations=100, absTolerance=0.0):

    a  = rootMin
    b  = rootMax
    fa = function( a ) - refValue
    fb = function( b ) - refValue
    if (fb*fa > 0):
        print "RootFinding initial interval w/o root: "\
              "(a=%e, b=%e), (F(a)=%e, F(b)=%e), (fa=%e, fb=%e), refValue = %e" \
              % (a,b, function(a), function(b), fa, fb, refValue)
        return 1

    ac_equal = False
    fc = fb
    c  = 0
    d  = 0
    e  = 0
    for i in range(maxIterations):

        if ((fb < 0 and fc < 0) or (fb > 0 and fc > 0)) :
            # Rename a,b,c and adjust bounding interval d
            ac_equal = True
            c  = a
            fc = fa
            d  = b - a
            e  = b - a

        if (TMath.Abs(fc) < TMath.Abs(fb)):
            ac_equal = True
            a  = b
            b  = c
            c  = a
            fa = fb
            fb = fc
            fc = fa

        tol = 0.5 * 2.2204460492503131e-16 * TMath.Abs(b)
        m   = 0.5 * (c - b)

        if fb == 0 or TMath.Abs(m) <= tol or TMath.Abs(fb) < absTolerance:
            return b

        # Bounds decreasing too slowly: use bisection
        if TMath.Abs (e) < tol or TMath.Abs(fa) <= TMath.Abs(fb) :
            d = m
            e = m
        else:
            # Attempt inverse cubic interpolation
            # Double_t p, q, r;
            s = fb / fa

            if ac_equal:
                p = 2 * m * s
                q = 1 - s
            else:
                q = fa / fc
                r = fb / fc
                p = s * (2 * m * q * (q - r) - (b - a) * (r - 1))
                q = (q - 1) * (r - 1) * (s - 1)

            # Check whether we are in bounds
            if (p > 0):
                q = -q
            else:
                p = -p

            min1 = 3 * m * q - TMath.Abs (tol * q)
            min2 = TMath.Abs (e * q)

            if 2 * p < min(min1,min2) :
                # Accept the interpolation
                e = d
                d = p / q
            else:
                d = m
                e = m
                # Interpolation failed: use bisection.

        # Move last best guess to a
        a  = b
        fa = fb
        # Evaluate new trial root
        if (TMath.Abs(d) > tol):
            b += d
        else:
            if m > 0: val = tol
            else:     val = -tol
            b += val
        fb = function( b ) - refValue



    # Return our best guess if we run out of iterations
    print "RootFinding maximum iterations (%i) reached before convergence" % maxIterations
    return b





########################################################
##  class holding observed and background information ##
########################################################
class StatDataSet:
    def __init__(self, Nobs):
        ## init member variables
        self.Nobserved = Nobs
        self.backgroundData = ParameterStore()


    def AddBackground(self, bkName, N, errN):
        self.backgroundData.AddParameter( Parameter(bkName, N, errN) )

    def SetCorrelation(self, bkName1, bkName2, rho):
        self.backgroundData.SetCorrelation( bkName1, bkName2, rho)


    def RunToyMC(self, toyMC_N=1000000):
        # init background data
        self.backgroundData.Init()
        # initialize calc
        seed = 19223451
        rand = TRandom3(seed)
        debugMsg = int(toyMC_N / 5 )
        passedEvts = 0.

        v = TVectorD( self.backgroundData.numParemeters )
        # toy MC event loop
        for i in xrange(toyMC_N):
            # print out status msg
            if i%debugMsg == 0:
                print "%-2.0f %% done" % (i/float(toyMC_N)*100.)

            # get random background numbers (corr. to their mean, covariance matrix)
            self.backgroundData.FillCorrRandomVec ( v )
            backgrounds = 0.
            for i in range( v.GetNrows() ):
                backgrounds += v[i]

            N_rand = rand.Poisson( backgrounds )

            # 1-sided
            if N_rand >= self.Nobserved:
                passedEvts += 1
            # 2-sided
    ##        if N_rand >= N_exp + fabs(N_obs - N_exp) or N_rand <= N_exp - fabs(N_obs - N_exp):
    ##            passedEvts += 1

        print "%-2.0f %% done" % (i/toyMC_N*100)

        # get results
        p   = passedEvts / toyMC_N
        ep  = TMath.Sqrt( p * (1.0 - p) / toyMC_N )
        nsigma  = GetSigmaFromProb( p )
        ensigma = TMath.fabs( GetSigmaFromProb( p + ep ) - nsigma )

        print "-- Results of toy MC"
        print "-- Nexp (bkg), Nobs : %4.2f, %4.2f" % (backgrounds, self.Nobserved )
        print "-- accepted %i out of %2.0E events " % (passedEvts, toyMC_N)
        print "-- p-value : %-10.4E +- %-5.2E" % (p, ep)
        print "-- signifiance [sigma] : %-5.3f +-  %-5.3f" % (nsigma, ensigma)






class ParameterStore:

    def __init__(self, seed = 19223451):


        self.numParemeters = 0     # number of parameters
        self.correlationMatrix = 0 # TMatrixDSym(n)
        self.covarianceMatrix  = 0 # TMatrixDSym(n)

        self.parameterPos = []     # value: parName, array position = parameter position in matrices
        self.parameters = {}       # key: parName           ; value: parameter obj
        self.parameterCorr = {}    # key: parName1_parName2 ; value: rho

        self.seed = seed            # seed for random generator
        self.rand = TRandom3(seed)  # random generator

        self.covariance_decomposed_matrix = 0 # lower triangle matrix C of covariance = C*C~
        self.is_init = False

    def AddParameter(self, par):
        from copy import deepcopy
        # sanity checks
        if not isinstance(par, Parameter):
            print "ERROR: par is not an instance of Paremter!"
            return False
        if self.parameters.has_key( par.GetName() ):
            print "WARNING: parameter name %s already existing !" % ( par.GetName() )
            return False

        self.parameters[ par.GetName() ] = deepcopy(par)
        self.parameterPos += [ par.GetName() ]
        self.numParemeters += 1
        return True

    def SetCorrelation(self, parName1, parName2, rho):
        # sanity checks
        if rho > 1.0 or rho < -1.0:
            print "ERROR -> rho = %5.3f not within [-1,1] !" % rho
            return False
        if parName1 == parName2:
            print "ERROR -> cannot set correlation for parName1 == parName2 !"
            return False
        if not self.parameters.has_key( parName1 ) or not self.parameters.has_key( parName2 ):
            print "ERROR -> parName1 or parName2 not existing !"
            return False

        # set the value
        self.parameterCorr[ self.GetCorrName( parName1, parName2 ) ] = rho
        return True

    def GetCorrName(self, p1, p2):
        if type(p1) is str and type(p2) is str:
            return self.parameters[p1].GetName()+"_"+self.parameters[p2].GetName()
        elif isinstance(p1,Paremeter) and isinstance(p2,Paremeter):
            return p1.GetName()+"_"+p2.GetName()
        else:
            print "ERROR"
            return False


    def GetParNamesFromCorrName(self, corrName):
        return corrName.split("_")

    def GetCorrelationMatrix(self):
        self.Init()
        return self.correlationMatrix

    def GetCovarianceMatrix(self):
        self.Init()
        return self.covarianceMatrix

    def Reset(self):
        self.is_init = False
        self.correlationMatrix = 0
        self.covarianceMatrix  = 0
        self.covariance_decomposed_matrix = 0

    def Init(self):
        if self.is_init:
            return True

        n = self.numParemeters
        self.correlationMatrix = TMatrixDSym(n)
        self.covarianceMatrix  = TMatrixDSym(n)

        # set self-correlation to 1.0
        for i in range(self.numParemeters):
            self.correlationMatrix[i][i] = 1.0
        # set other correlations (if existing)
        for pc in self.parameterCorr:
            rho = self.parameterCorr[ pc ]
            parName1 = self.GetParNamesFromCorrName( pc )[0]
            parName2 = self.GetParNamesFromCorrName( pc )[1]
            pos1 = self.parameterPos.index(parName1)
            pos2 = self.parameterPos.index(parName2)
            self.correlationMatrix[pos1][pos2] = rho
            self.correlationMatrix[pos2][pos1] = rho


        # set correlation martix
        i = 0
        for p in self.parameterPos:
            erri = self.parameters[p].GetError()
            self.covarianceMatrix[i][i] = erri*erri
            # off-diagonal elements:
            for j in range( n - i - 1):
                j += i+1
                parNameJ = self.parameterPos[j]
                errj = self.parameters[parNameJ].GetError()
                self.covarianceMatrix[i][j] = errj * erri * self.correlationMatrix[i][j]
                self.covarianceMatrix[j][i] = self.covarianceMatrix[i][j]
            i += 1


        covMat_upper_right_triangle = TDecompChol( self.covarianceMatrix )
        covMat_upper_right_triangle.Decompose()
        self.covariance_decomposed_matrix = TMatrixD( TMatrixD.kTransposed, covMat_upper_right_triangle.GetU() )

        self.is_init = True
        return True

    def FillCorrRandomVec(self, vec):
        if not isinstance(vec, TVectorD):
            print "CorrRandomNumbers: ERROR -> GetRandomVec called with type(vec) not a TVectorD !"
            return False
        if vec.GetNrows() != self.numParemeters:
            print "size of vector is not the same as number of parameters!"
            return False

        self.Init()
        # generate gaus random numbers (mean=0, widht=1)
        for i in range( vec.GetNrows() ):
            vec[i] = self.rand.Gaus( )

        # multiply correlated errors
        vec *= self.covariance_decomposed_matrix

        # add mean to it
        for i in range( vec.GetNrows() ):
            vec[i] += self.parameters[ self.parameterPos[i] ].GetValue()

        return True


class Parameter:
    def __init__(self, name, value, error):
        # sanity checks:
        if type(name) is not str :
            print "ERROR: name is not of type str!"
            name = "tmp"
        if name.find("_") != -1:
            print "WARNING: replacing '_' by '-' in parameter name!"
            name.replace("_","-")

        self.name = name
        self.value = value
        self.error = error

    def GetName(self):
        return self.name

    def GetValue(self):
        return float(self.value)

    def GetError(self):
        return float(self.error)
