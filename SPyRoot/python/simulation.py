import os,sys,string
import glob
from WarmParts import warm
from array import array
from ROOT import *

import RootStyles
rs = RootStyles.RootStyles()
rs.setAtlasStyle2()
rs.style.cd()
rs.style.SetPadRightMargin( 0.17 )
rs.style.SetPadTopMargin( 0.07 )
rs.style.SetPaintTextFormat("2.1f")
rs.setPalette()
ROOT.gROOT.ForceStyle()

def GraphProperties( g, x_title, y_title, l_color, l_style, m_color, m_style, time_axis = False ):
    g.GetXaxis().CenterTitle()
    g.GetYaxis().CenterTitle()
    g.GetXaxis().SetTitle( x_title )
    g.GetYaxis().SetTitle( y_title )
    g.SetLineColor( l_color )
    g.SetLineStyle( l_style )
    g.SetMarkerColor( m_color )
    g.SetMarkerStyle( m_style )
    if m_style!=-1:
        g.SetDrawOption("AL")

def Graph2DProperties( g, x_title, y_title, z_title, l_color, l_style, m_color, m_style, time_axis = False ):
    g.GetXaxis().CenterTitle()
    g.GetYaxis().CenterTitle()
    g.GetZaxis().CenterTitle()
    g.GetXaxis().SetTitle( x_title )
    g.GetYaxis().SetTitle( y_title )
    g.GetZaxis().SetTitle( z_title )
    g.SetLineColor( l_color )
    g.SetLineStyle( l_style )
    g.SetMarkerColor( m_color )
    g.SetMarkerStyle( m_style )
    if m_style!=-1:
        g.SetDrawOption("AL")

LHCring = 26659.
FCCring = 101898.2192       
 
class simulation(object):


    def __init__(self, directory):
        if os.path.exists(directory) == True:
            self.Directory = directory
            print "Reading input directory: ",self.Directory

            self.Beam = 0
            if "b2" in directory or "B2" in directory or "b4" in directory or "B4" in directory: self.Beam = 2
            if "b1" in directory or "B1" in directory: self.Beam = 1

            self.Plane = "def"
            if "hor" in directory or "HOR" in directory or "Hor" in directory: self.Plane = "HORIZONTAL"
            if "ver" in directory or "VER" in directory or "Ver" in directory: self.Plane = "VERTICAL"
 
            self.isFCC = False
            self.ring = LHCring
            if "FCC" in directory:
                self.isFCC = True
                self.ring = FCCring

            self.baseDirectory= ""
            if os.path.exists(directory+"/test") == True:
                self.baseDirectory = directory+"/test"
                print "Reading input directory for common files: ",self.baseDirectory

            if self.Directory[len(self.Directory)-1]!="/":
                    self.Directory = self.Directory+"/"
            if self.baseDirectory!="" and self.baseDirectory[len(self.baseDirectory)-1]!="/":
                    self.baseDirectory = self.baseDirectory+"/"

            try:
                os.stat(self.Directory+"/plots")
            except:
                os.mkdir(self.Directory+"/plots")       

        else:
            print "ERROR: ",directory," does not exists...exiting\n"
            sys.exit(-1)

        self.deltaS = 0.1
        self.binadjust = 1./self.deltaS
        self.emittance_x = 0.
        self.emittance_y = 0.

        self._read_collgaps()
        self._read_betafunctions()
        self._read_emittance()
        self.inDirs=[]
        self._get_inputDirs()


        return

    def setBaseDir(self,directory):
        if os.path.exists(directory) == True:
            self.baseDirectory = directory
            print "Reading input directory for common files: ",self.baseDirectory

            if self.baseDirectory[len(baseDirectory)-1]!="/":
                self.baseDirectory = self.baseDirectory+"/"

        else:
            print "ERROR: ",directory," does not exists...exiting\n"
            sys.exit(-1)

        return

    def setBinSize(self, binSize):
        self.deltaS = binSize

    def _read_emittance(self):
        infile = open(self.Directory + "clean_input/fort.3","r")
        iline = infile.readlines()[54].split()
        if len(iline) < 2:
            print "ERROR in fort.3 file"
            return
        self.emittance_x = float(iline[0])
        self.emittance_y = float(iline[1])
        self.sigx_d = 1.
        self.sigy_d = 1.
        self.sigxp_d = 1.
        self.sigyp_d = 1.
        if fabs(self.beta_x_ip1) > 0.0:
            self.sigx_d = sqrt(self.beta_x_ip1*self.emittance_x )
        if fabs(self.beta_y_ip1) > 0.0:
            self.sigy_d = sqrt(self.beta_y_ip1*self.emittance_y )
        if fabs(self.alfa_x_ip1) != 0.0:
            self.sigxp_d = sqrt(self.emittance_y*(1+self.alfa_x_ip1*self.alfa_x_ip1)/self.beta_x_ip1)
        if fabs(self.alfa_y_ip1) > 0.0:
            self.sigyp_d = sqrt(self.emittance_y*(1+self.alfa_y_ip1*self.alfa_y_ip1)/self.beta_y_ip1)
        
        self.g_beta_times_emit_x = TGraph()
        self.g_beta_times_emit_y = TGraph()
        for n in range(self.g_betax.GetN()):
            spos = Double()
            betax = Double()
            betay = Double()
            self.g_betax.GetPoint(n,spos,betax)
            self.g_beta_times_emit_x.SetPoint( n, spos, sqrt(betax*self.emittance_x) )
            self.g_betay.GetPoint(n,spos,betay)
            self.g_beta_times_emit_y.SetPoint( n, spos, sqrt(betay*self.emittance_y) )
        GraphProperties( self.g_beta_times_emit_x, "s [m]", "Sigma x [m]", kBlue, 1, kBlue, -1, False)
        GraphProperties( self.g_beta_times_emit_y, "s [m]", "Sigma y [m]", kRed, 1, kRed, -1, False)        

        return

    def _read_collgaps(self):
        self.collimator_id = {}
        self.collimator_betax = {}
        self.collimator_betay = {}
        self.collimator_nsig = {}
        self.collimator_angle = {}
        self.collimator_material = {}
        self.collimator_length = {}
        self.collimator_sigx = {}
        self.collimator_sigy = {}
        self.collimator_alfax = {}
        self.collimator_alfay = {}
        self.collimator_dispx = {}
        infile = open(self.baseDirectory + "/collgaps.dat","r")
        lines = infile.readlines()    
        ntitle = 1
        for i in range(ntitle, len(lines)):
            iline = lines[i].split()
            coll_name = iline[1]
            print coll_name
            if "TCDQA.A4L6.B" in coll_name: coll_name = "TCDQA.A4L6.B2"
            if "TCDQA.B4L6.B" in coll_name: coll_name = "TCDQA.B4L6.B2"
            if "TCDQA.C4L6.B" in coll_name: coll_name = "TCDQA.C4L6.B2"
            if "TCDQA.A4R6.B" in coll_name: coll_name = "TCDQA.A4R6.B1"
            if "TCDQA.B4R6.B" in coll_name: coll_name = "TCDQA.B4R6.B1"
            if "TCDQA.C4R6.B" in coll_name: coll_name = "TCDQA.C4R6.B1"
            if "TCRYO.10R7.B" in coll_name and self.Beam == 1: coll_name = "TCRYO.10R7.B1"
            if "TCRYO.10R7.B" in coll_name and self.Beam == 2: coll_name = "TCRYO.10R7.B2"
            if "TCRYO.10RD.B" in coll_name and self.isFCC: coll_name = "TCRYO.10RD.B1"
            if "TCRYO.11RD.B" in coll_name and self.isFCC: coll_name = "TCRYO.11RD.B1"
            self.collimator_id[coll_name] = int( iline[0])
            self.collimator_angle[coll_name] = float( iline[2])
            self.collimator_betax[coll_name] = float( iline[3])
            self.collimator_betay[coll_name] = float( iline[4])
            self.collimator_material[coll_name] = iline[6]
            self.collimator_length[coll_name] = float( iline[7])
            self.collimator_sigx[coll_name] = float( iline[8])
            self.collimator_sigy[coll_name] = float( iline[9])
            self.collimator_nsig[coll_name] = float( iline[12])            
        infile.close()


        #print "Collimator id max: ",max(self.collimator_id.values()), " and size ",len(self.collimator_id)
        self.collimator_name = max(self.collimator_id.values())*[0.]
        for key in self.collimator_id.keys():
            self.collimator_name[ self.collimator_id[key] - 1 ] = key
        #print "Size of collimator array: %i " %(len(self.collimator_name))
        #print self.collimator_name
        #print "Now coll. ID:"
        #print self.collimator_id
              
        return

    def _read_betafunctions(self):
        self.g_betax = TGraph()
        self.g_betay = TGraph()
        self.h_betax = TH1F("h_betax","h_betax",int(self.ring/1),0.,self.ring)
        self.h_betay = TH1F("h_betay","h_betay",int(self.ring/1),0.,self.ring)
        self.collimator_spos = {}
        infile = open(self.baseDirectory + "/betafunctions.dat","r")
        lines = infile.readlines()    
        ntitle = 1
        self.beta_x_ip1 = 0.
        self.beta_y_ip1 = 0.
        self.alfa_x_ip1 = 0.
        self.alfa_y_ip1 = 0.
        #should be changed!!! Taken for now from twiss file
        #should also add how to get alfa for LHC case (need to use amplitude.dat)

        startOfRingFound = False
        for i in range(ntitle, len(lines)):
            iline = lines[i].split()
            #index = int( iline[0] )
            name =  iline[1] 
            s_pos = float( iline[2]) 
            betax = float( iline[3]) 
            betay = float( iline[4]) 
            if s_pos != 0:
                self.g_betax.SetPoint( self.g_betax.GetN(), s_pos, betax )
                self.g_betay.SetPoint( self.g_betay.GetN(), s_pos, betay )
                ibin = self.h_betax.FindBin(s_pos)
                self.h_betax.SetBinContent(ibin,betax)
                self.h_betay.SetBinContent(ibin,betay)
                for icoll in self.collimator_id.keys():
                    if name.upper() in icoll:
                        self.collimator_spos[ icoll ] = s_pos
            if not self.isFCC and name.find("ip1")==0:
                self.beta_x_ip1 = betax
                self.beta_y_ip1 = betay
            if self.isFCC and name.find("ipa")==0: 
                startOfRingFound = True
                self.beta_x_ip1 = betax
                self.beta_y_ip1 = betay

        #values valid for TOY_V1 
        if self.isFCC and not startOfRingFound:
            self.beta_x_ip1 = 353.363894
            self.beta_y_ip1 = 62.551244
            self.alfa_x_ip1 = 0.012076
            self.alfa_y_ip1 = -0.014194

        infile.close()
                
        #now look at amplitude.dat to get alfax and alfay for collimators:
        amplfile = open(self.baseDirectory + "/amplitude.dat","r")
        lines = amplfile.readlines()    
        for i in range(ntitle, len(lines)):
            iline = lines[i].split()
            name =  iline[1]
            alfax = float( iline[7])
            alfay = float( iline[8])
            dispx = float( iline[13])
            if not self.isFCC and name.find("ip1")==0:
                self.alfa_x_ip1 = alfax
                self.alfa_y_ip1 = alfay
            if self.isFCC and name.find("ipa")==0: 
                self.alfa_x_ip1 = alfax
                self.alfa_y_ip1 = alfay
            for icoll in self.collimator_id.keys():
                if name.upper() in icoll:
                     self.collimator_alfax[icoll] = alfax
                     self.collimator_alfay[icoll] = alfay
                     self.collimator_dispx[icoll] = dispx

        GraphProperties( self.g_betax, "s [m]", "Beta Function [m]", kBlue, 1, kBlue, 20, False)
        GraphProperties( self.g_betay, "s [m]", "Beta Function [m]", kRed, 1, kRed, 20, False)        
        return
        

    def _print(self):
        print "inputDir: ", self.Directory, ", baseDir: ",self.baseDirectory
        print "number of inputDir: ", len(self.inDirs)
        print "machine: isFF? ", self.isFCC
        print "circumference: ", self.ring
        print "beam ", self.Beam, ", plane ", self.Plane
        print "binning: ",self.deltaS
        print "emittance x: ", self.emittance_x 
        print "emittance y: ", self.emittance_y 
        print "betax start of ring: ", self.beta_x_ip1
        print "betay start of ring: ", self.beta_y_ip1
        print "sigx start of ring: ",self.sigx_d
        print "sigy start of ring: ",self.sigy_d
        print ""
        print "Collimator settings: "
        print ""
        print "N collimators: ",len(self.collimator_spos)
        print "POS: ", self.collimator_spos, "\n"
        print "ID: ", self.collimator_id, "\n"
        print "NAME:", self.collimator_name, "\n"
        print "BETAx:", self.collimator_betax, "\n"
        print "SIGMAx:",self.collimator_sigx, "\n"
        print "ALFAx:", self.collimator_alfax, "\n"
        print "DISPx:", self.collimator_dispx, "\n"
        return

    def _get_inputDirs(self):

        self.inDirs=[]
        for inDir in os.listdir("%s" %self.Directory):
            if inDir.find(".root")>=0:
                continue
            if inDir.find("clean_input") >=0 :
                continue
            if inDir.find("test") >=0:
                continue
            if not inDir.find("run")==0:
                continue
            self.inDirs += [ inDir ]

        print "Found %i inputDir" %len(self.inDirs)
        print self.inDirs
        return

    def _read_dist0(self):
        
        h_x_y_d = {}
        h_x_y_d = TH2F("x_y_d","Transverse distribution",500,-10.,10.,500,-10.,10.) 
#        h_x_xp_d = TH2F("x_xp_d","X' VS X",500,-8,8,200,-0.5,0.5) 
#        h_y_yp_d = TH2F("y_yp_d","Y' VS Y",500,-8,8,200,-0.5,0.5) 
        h_x_xp_d = TH2F("x_xp_d","X' VS X",500,-10,10,500,-10,10) 
        h_y_yp_d = TH2F("y_yp_d","Y' VS Y",500,-10,10,500,-10,10) 

        infile = TFile.Open(self.Directory + "dist0.root")
        t = infile.Get("ntuple")
        for i in range(t.GetEntries()):
            t.GetEntry(i)
            h_x_y_d.Fill(t.x/self.sigx_d,t.y/self.sigy_d)
            h_x_xp_d.Fill(t.x/self.sigx_d,t.xp/self.sigxp_d)
            h_y_yp_d.Fill(t.y/self.sigy_d,t.yp/self.sigyp_d)

        outfile = TFile(self.Directory + "plots/TransverseDist0.root" ,"recreate")
        outfile.cd()
        h_x_y_d.Write()
        h_x_xp_d.Write()
        h_y_yp_d.Write()
        outfile.Close()

        return
#        line_format = [float]*6
#        for inDir in self.inDirs:
#            if not os.path.isfile(self.Directory + inDir+ "/dist0.dat"):
#                continue
#            thisfile = open(self.Directory + inDir+ "/dist0.dat",'r')
#            for iline in thisfile.readlines()[1:]:
#              #  print iline.split()
#                data_d = [line_format[i](xx) for i, xx in enumerate(iline.split())]
#                x_d = data_d[0]
#                xp_d = data_d[1]*1000 #/0.02904607 #to have mrad
#                y_d = data_d[2]
#                yp_d = data_d[3]*1000 #/0.02904607 #to have mrad
                    
               # sigy_d = self.collimator_sigy[ self.collimator_name[ coll_id -1 ] ]
#                self.h_x_y_d.Fill(x_d/sigx_d,y_d/sigy_d)
#                self.h_x_xp_d.Fill(x_d/sigx_d,xp_d)
#                self.h_y_yp_d.Fill(y_d/sigy_d,yp_d)
#            thisfile.close() 
              
    def _read_firstImpacts(self):

        ntotimp = 0
        self.ParticlesLostAtCollID_first = max(self.collimator_id.values())*[0] 

        h_x_y_first_imp_notnorm = {}
        h_x_y_first_imp = {}
        h_y_yp_first_imp = {}
        h_x_xp_first_imp = {}

        #Note: x is actually the impact parameter!!! 
        h_x_y_first_imp["TCP.C"] = TH2F("x_y_f_imp_TCP.C","Transverse distribution first_impacts TCP.C L=0.60 cm",200,-0.1,0.35,200,-7,7) 
        h_x_y_first_imp["TCP.B"] = TH2F("x_y_f_imp_TCP.B","Transverse distribution first_impacts TCP.B L=0.60 cm",200,-0.1,2,200,-7,7) 
        h_x_y_first_imp["TCP.D"] = TH2F("x_y_f_imp_TCP.D","Transverse distribution first_impacts TCP.D L=0.60 cm",200,-0.1,0.35,200,-7,7) 
        h_x_y_first_imp_notnorm["TCP.C"] = TH2F("x_y_f_imp_notnorm_TCP.C","Transverse distribution first_impacts TCP.C L=0.60 cm",200,0, 0.2e-3,200,-1.5e-3,1.5e-3) 
        h_x_y_first_imp_notnorm["TCP.B"] = TH2F("x_y_f_imp_notnorm_TCP.B","Transverse distribution first_impacts TCP.B L=0.60 cm",200,0., 0.2e-3,200,-1.5e-3,1.5e-3) 
        h_x_y_first_imp_notnorm["TCP.D"] = TH2F("x_y_f_imp_notnorm_TCP.D","Transverse distribution first_impacts TCP.D L=0.60 cm",200,0., 0.2e-3,200, -1.5e-3,1.5e-3) 
        
        h_x_xp_first_imp["TCP.C"] = TH2F("x_xp_f_TCP.C","X'- X  TCP.C",200,-0.1,0.35,200,-7,7)
        h_x_xp_first_imp["TCP.B"] = TH2F("x_xp_f_TCP.B","X'- X  TCP.B",200,-0.1,2.,200,-7,7)
        h_x_xp_first_imp["TCP.D"] = TH2F("x_xp_f_TCP.D","X'- X  TCP.D",200,-0.1,0.35,200,-7,7)
        
        h_y_yp_first_imp["TCP.C"] = TH2F("y_yp_f_TCP.C","Y'- Y  TCP.C",200,-7,7,200,-7,7)
        h_y_yp_first_imp["TCP.B"] = TH2F("y_yp_f_TCP.B","Y'- Y  TCP.B",200,-7,7,200,-7,7)
        h_y_yp_first_imp["TCP.D"] = TH2F("y_yp_f_TCP.D","Y'- Y  TCP.D",200,-7,7,200,-7,7)
        

        infile = TFile.Open(self.Directory + "FirstImpacts.root")
        t = infile.Get("ntuple")
        print "Number of first impacts: ", t.GetEntries()
        for i in range(t.GetEntries()):
            t.GetEntry(i)
            icoll = int(t.icoll)-1
            if t.nabs == 1: 
                self.ParticlesLostAtCollID_first[icoll] += 1
            sigx_2 = self.collimator_sigx[ self.collimator_name[ icoll ] ]
            sigy_2 = self.collimator_sigy[ self.collimator_name[ icoll ] ]
            sigxp_2 = sqrt(( 1 + self.collimator_alfax[ self.collimator_name[ icoll ] ]*self.collimator_alfax[ self.collimator_name[ icoll ] ])/self.collimator_betax[ self.collimator_name[ icoll ] ]*self.emittance_x )
            sigyp_2 = sqrt((1+ self.collimator_alfay[ self.collimator_name[ icoll ] ]*self.collimator_alfay[ self.collimator_name[ icoll ] ])/self.collimator_betay[ self.collimator_name[ icoll ] ]*self.emittance_y)
            if "TCP.B" in self.collimator_name[ icoll ] :
                h_x_y_first_imp["TCP.B"].Fill(t.x_in/sigx_2,t.y_in/sigy_2)
                h_x_y_first_imp_notnorm["TCP.B"].Fill(t.x_in,t.y_in)
                h_x_xp_first_imp["TCP.B"].Fill(t.x_in/sigx_2,t.xp_in/sigxp_2)
                h_y_yp_first_imp["TCP.B"].Fill(t.y_in/sigy_2,t.yp_in/sigyp_2)
            if "TCP.C" in self.collimator_name[ icoll ] :
                h_x_y_first_imp["TCP.C"].Fill(t.x_in/sigx_2,t.y_in/sigy_2)
                h_x_y_first_imp_notnorm["TCP.C"].Fill(t.x_in,t.y_in)
                h_x_xp_first_imp["TCP.C"].Fill(t.x_in/sigx_2,t.xp_in/sigxp_2)
                h_y_yp_first_imp["TCP.C"].Fill(t.y_in/sigy_2,t.yp_in/sigyp_2)
            if "TCP.D" in self.collimator_name[icoll] :      
                h_x_y_first_imp["TCP.D"].Fill(t.x_in/sigx_2,t.y_in/sigy_2)
                h_x_y_first_imp_notnorm["TCP.D"].Fill(t.x_in,t.y_in)
                h_x_xp_first_imp["TCP.D"].Fill(t.x_in/sigx_2,t.xp_in/sigxp_2)
                h_y_yp_first_imp["TCP.D"].Fill(t.y_in/sigy_2,t.yp_in/sigyp_2)

        infile.Close()
        outfile = TFile(self.Directory + "plots/FirstImpacts.root" ,"recreate")
        outfile.cd()
        for h in h_x_y_first_imp:
            h_x_y_first_imp[h].Write()
        for h in h_x_y_first_imp_notnorm:
            h_x_y_first_imp_notnorm[h].Write()
        for h in h_y_yp_first_imp:
            h_y_yp_first_imp[h].Write()
        for h in h_x_xp_first_imp:
            h_x_xp_first_imp[h].Write()
        outfile.Close()

        return


    def _read_impacts(self):

        h_x_y_impacts = {}        
        h_x_y_impacts["TCP.C"] = TH2F("x_y_impacts_TCP.C","Transverse distribution impacts TCP.C ",200,-20,20,200,-20,20) 
        h_x_y_impacts["TCP.B"] = TH2F("x_y_impacts_TCP.B","Transverse distribution impacts TCP.B ",200,-20,20,200,-20,20) 
        h_x_y_impacts["TCP.D"] = TH2F("x_y_impacts_TCP.D","Transverse distribution impacts TCP.D ",200,-20,20,200,-20,20) 
        h_x_y_impacts["TCTH.4L1"] = TH2F("x_y_impacts_TCTH.4L1","Transverse distribution impacts TCTH.4L1 ",200,-20,20,200,-20,20) 
        h_x_y_impacts["TCTH.4L3"] = TH2F("x_y_impacts_TCTH.4L3","Transverse distribution impacts TCTH.4L3 ",200,-20,20,200,-20,20) 

        h_x_xp_impacts = {}        
        h_x_xp_impacts["TCP.C"] = TH2F("x_xp_impacts_TCP.C","Phase space impacts TCP.C ",200,-20,20,200,-20,20) 
        h_x_xp_impacts["TCP.B"] = TH2F("x_xp_impacts_TCP.B","Phase space impacts TCP.B ",200,-20,20,200,-20,20) 
        h_x_xp_impacts["TCP.D"] = TH2F("x_xp_impacts_TCP.D","Phase space impacts TCP.D ",200,-20,20,200,-20,20) 

        h_y_yp_impacts = {}        
        h_y_yp_impacts["TCP.C"] = TH2F("y_yp_impacts_TCP.C","Phase space impacts TCP.C ",200,-20,20,200,-20,20) 
        h_y_yp_impacts["TCP.B"] = TH2F("y_yp_impacts_TCP.B","Phase space impacts TCP.B ",200,-20,20,200,-20,20) 
        h_y_yp_impacts["TCP.D"] = TH2F("y_yp_impacts_TCP.D","Phase space impacts TCP.D ",200,-20,20,200,-20,20) 

        h_spos_abs = {}
        h_spos_abs["TCP.C"] = TH1F("s_abs_TCP.C","Spos absorbed in TCP.C ",100,0.,1.) 
        h_spos_abs["TCP.B"] = TH1F("s_abs_TCP.B", "Spos absorbed in TCP.B ",100,0.,1.) 
        h_spos_abs["TCP.D"] = TH1F("s_abs_TCP.D","Spos absorbed in TCP.D ",100,0.,1.) 

        h_nturn_abs= {}
        h_nturn_abs["TCP.C"] = TH1F("nturn_abs_TCP.C","nturn absorbed in TCP.C ",200,0,200) 
        h_nturn_abs["TCP.B"] = TH1F("nturn_abs_TCP.B", "nturn absorbed in TCP.B ",200,0,200) 
        h_nturn_abs["TCP.D"] = TH1F("nturn_abs_TCP.D","nturn absorbed in TCP.D ",200,0,200) 

        #first try with impacts_real.root
        infileName = ""
        outfileName = ""
        if os.path.isfile(self.Directory + "impacts_real.root"):
            infileName = self.Directory + "impacts_real.root"
            outfileName = self.Directory + "plots/impacts_real.root"
            print "Reading impacts_real.root"
        elif os.path.isfile(self.Directory + "FLUKA_impacts.root"):
            infileName = self.Directory + "FLUKA_impacts.root"
            outfileName = self.Directory + "plots/FLUKA_impacts.root"
            print "Reading FLUKA_impacts.root"
        infile = TFile.Open(infileName)
        t = infile.Get("ntuple")

        for i in range(t.GetEntries()):
            t.GetEntry(i)
            icoll = int(t.icoll)-1
            sigx_2 = self.collimator_sigx[ self.collimator_name[ icoll ] ]
            sigy_2 = self.collimator_sigy[ self.collimator_name[ icoll ] ]
            sigxp_2 = sqrt(( 1 + self.collimator_alfax[ self.collimator_name[ icoll ] ]*self.collimator_alfax[ self.collimator_name[ icoll ] ])/self.collimator_betax[ self.collimator_name[ icoll ] ]*self.emittance_x )
            sigyp_2 = sqrt((1+ self.collimator_alfay[ self.collimator_name[ icoll ] ]*self.collimator_alfay[ self.collimator_name[ icoll ] ])/self.collimator_betay[ self.collimator_name[ icoll ] ]*self.emittance_y)
            if "TCP.B" in self.collimator_name[ icoll ] :
                h_x_y_impacts["TCP.B"].Fill(t.x*0.001/sigx_2,t.y*0.001/sigy_2) #x and xp in mm and mrad
                h_x_xp_impacts["TCP.B"].Fill(t.x*0.001/sigx_2,t.xp*0.001/sigxp_2)
                h_y_yp_impacts["TCP.B"].Fill(t.y*0.001/sigy_2,t.yp*0.001/sigyp_2)
                if t.nabs==1:
                    h_spos_abs["TCP.B"].Fill(t.s)
                    h_nturn_abs["TCP.B"].Fill(t.iturn)
            if "TCP.C" in self.collimator_name[ icoll ] :
                h_x_y_impacts["TCP.C"].Fill(t.x*0.001/sigx_2,t.y*0.001/sigy_2)
                h_x_xp_impacts["TCP.C"].Fill(t.x*0.001/sigx_2,t.xp*0.001/sigxp_2)
                h_y_yp_impacts["TCP.C"].Fill(t.y*0.001/sigy_2,t.yp*0.001/sigyp_2)
                if t.nabs==1:
                    h_spos_abs["TCP.C"].Fill(t.s)
                    h_nturn_abs["TCP.C"].Fill(t.iturn)
            if "TCP.D" in self.collimator_name[ icoll ] :
                h_x_y_impacts["TCP.D"].Fill(t.x*0.001/sigx_2,t.y*0.001/sigy_2)
                h_x_xp_impacts["TCP.D"].Fill(t.x*0.001/sigx_2,t.xp*0.001/sigxp_2)
                h_y_yp_impacts["TCP.D"].Fill(t.y*0.001/sigy_2,t.yp*0.001/sigyp_2)
                if t.nabs==1:
                    h_spos_abs["TCP.D"].Fill(t.s)
                    h_nturn_abs["TCP.D"].Fill(t.iturn)
            if "TCTH.4L1" in self.collimator_name[ icoll ] :
                h_x_y_impacts["TCTH.4L1"].Fill(t.x*0.001/sigx_2,t.y*0.001/sigy_2)
            if "TCTH.4L3" in self.collimator_name[ icoll ] :
                h_x_y_impacts["TCTH.4L3"].Fill(t.x*0.001/sigx_2,t.y*0.001/sigy_2)

        infile.Close()
        outfile = TFile(outfileName ,"recreate")
        outfile.cd()
        for h in h_x_y_impacts:
            h_x_y_impacts[h].Write()
        for h in h_x_xp_impacts:
            h_x_xp_impacts[h].Write()
        for h in h_y_yp_impacts:
            h_y_yp_impacts[h].Write()
        for h in h_spos_abs:
            h_spos_abs[h].Write()
        for h in h_nturn_abs:
            h_nturn_abs[h].Write()
        outfile.Close()

        return

    def _print_betafunctions(self):
        g_coll_betax = TGraph()
        g_coll_betay = TGraph()
        #print "In _print_betafunctions"
        for key in self.collimator_id.keys():
            #print key
            #print self.collimator_spos[key]
            #print self.collimator_betax[key]
            g_coll_betax.SetPoint( g_coll_betax.GetN(), self.collimator_spos[key], self.collimator_betax[key])
            g_coll_betay.SetPoint( g_coll_betay.GetN(), self.collimator_spos[key], self.collimator_betay[key])
        GraphProperties( g_coll_betax, "s [m]", "Beta Function [m]", kBlue, 1, kBlue, 20, False)
        GraphProperties( g_coll_betay, "s [m]", "Beta Function [m]", kRed, 1, kRed, 20, False)
        self.g_betax.SetTitle("B%i"%self.Beam+"  "+self.Plane)
        self.g_betay.SetTitle("B%i"%self.Beam+"  "+self.Plane)

        leg1 = TLegend(0.2,0.6,0.4,0.8)
        leg1.SetFillStyle(0)
        leg1.SetBorderSize(0)
        leg1.AddEntry(self.g_betax, "Beta X","L")
        leg1.AddEntry(self.g_betay, "Beta Y","L")
        leg1.AddEntry(g_coll_betax, "Collimator: Beta X","P")
        leg1.AddEntry(g_coll_betay, "Collimator: Beta Y","P")        

        c1 = TCanvas("c1","BetaFunctions",1000,500)
        #gPad.SetLogy(True)
        self.g_betax.Draw("AL")
        self.g_betax.GetXaxis().SetRangeUser(0.,self.ring)
        self.g_betay.Draw("L")
        g_coll_betax.Draw("P")
        g_coll_betay.Draw("P")
        leg1.Draw()

        c1.SaveAs(self.Directory+"/plots/BetaFunctions.pdf")
        c1.SaveAs(self.Directory+"/plots/BetaFunctions.png")

        f = TFile(self.Directory+"/plots/BetaFunctions.root","recreate")
        f.cd()
        self.g_betax.SetName("Betax")
        self.g_betay.SetName("Betay")
        self.g_betax.Write()
        self.g_betay.Write()
        g_coll_betax.SetName("Coll_betax")
        g_coll_betay.SetName("Coll_betay")
        g_coll_betax.Write()
        g_coll_betay.Write()
        self.h_betax.Write()
        self.h_betay.Write()
        self.g_beta_times_emit_x.SetName("Amplitude_x")
        self.g_beta_times_emit_y.SetName("Amplitude_y")
        self.g_beta_times_emit_x.Write()
        self.g_beta_times_emit_y.Write()
        f.Close()

        return

    def _makeLayout_(self):

        self.h_coll_postion = TH1F("h_coll_position","h_coll_position",int(self.ring/self.deltaS),0.,self.ring)
        self.h_dipole_postion = TH1F("h_dipole_position","h_dipole_position",int(self.ring/self.deltaS),0.,self.ring)
        self.h_quadrupole_postion = TH1F("h_quadrupole_position","h_quadrupole_position",int(self.ring/self.deltaS),0.,self.ring)

        for key in self.collimator_id.keys():
            if self.collimator_length[key]==0.:
                continue
            #print "coll: ",key, " pos: ", self.collimator_spos[key], ", lenght: ",self.collimator_length[key]
            collStart = self.collimator_spos[key]
            nbins = int(self.collimator_length[key]/self.deltaS+0.00001)
            for r in range(0,nbins):
                self.h_coll_postion.SetBinContent(self.h_coll_postion.FindBin(collStart)+r,1.)

        #Now look at location of dipoles and quadrupoles
        inFileName =  []
        os.chdir(self.baseDirectory)
        for file in glob.glob("*thick.b%i*tfs" %self.Beam):
            inFileName += [file]
        if len(inFileName) ==0 :
            for file in glob.glob("*b%i*thick*tfs" %self.Beam):
                inFileName += [file]
        if self.Beam==0:
            for file in glob.glob("*thick*tfs"):
                inFileName += [file]
        if len(inFileName) ==0 :
            print "ERROR: No thick file found"
        if len(inFileName) > 1:
            print "more than one thick files found, using the first one", inFileNam[0]
        inputMagnets = self.baseDirectory + inFileName[0]
        print "Input twiss file: %s" %inputMagnets

        fi = open(inputMagnets)
        lines = fi.readlines()
        fi.close()
        #first find column for name, s pos and len
        nfound = 0
        for l in lines:
            if len(l) < 100:
                continue
            parts = l.split()
            ncol = {}
            pcounter = 0
            for p in parts:
                if p=="*":
                    continue
                #if (p.find("KEYWORD")==0) and not ('KEYWORD' in ncol):
                #    ncol['KEYWORD']= pcounter
                #    nfound+=1
                if (p.find("NAME")==0) and not ('NAME' in ncol):
                    ncol['NAME']= pcounter
                    nfound+=1
                    print "Found name"
                if (p.find("S")==0) and not ('S' in ncol):
                    ncol['S']= pcounter
                    nfound+=1
                    print "Found s"
                if (p.find("L")==0) and not ('L' in ncol):
                    ncol['L']= pcounter
                    nfound+=1
                    print "Found L"
                pcounter +=1
                if nfound==3:
                    break
            if nfound==3:
                break
        print "Found columns: name %i, s %i, len %i" %(ncol['NAME'],ncol['S'],ncol['L'])

        counter=0
        for l in lines:
            counter+=1
            #if counter > 200:
            #    break
            isMQ = l.find("MQ") or l.find("QUADRUPOLE")
            isMB = l.find("MB") or l.find("SBEND")
            if isMB < 0 and isMQ < 0:
                continue
            #if  (isMB >= 0 and isMB < 4) or (isMQ >= 0 and isMB<4):
            parts = l.split()
            #print "Part %s found dipole? %i found quadrupo? %i" %(parts[0],isMB,isMQ)
            name = parts[ncol['NAME']]
            s_pos = float(parts[ncol['S']])
            s_len = float(parts[ncol['L']])
            s_nbins = int(s_len/self.deltaS+0.00001)
            for r in range(0,s_nbins):
                if (isMB>=0):
                    #print "Filling dipole"
                    self.h_dipole_postion.SetBinContent(self.h_dipole_postion.FindBin(s_pos-s_len)+r,1.)
                if (isMQ>=0):
                    #print "Filling quadrupole"
                    self.h_quadrupole_postion.SetBinContent(self.h_quadrupole_postion.FindBin(s_pos-s_len)+r,1.)

                
        outfile = TFile(self.Directory +"plots/Layout.root","recreate")
        outfile.cd()
        self.h_coll_postion.Write()
        self.h_dipole_postion.Write()
        self.h_quadrupole_postion.Write()
        outfile.Close()


        return


    def nsigmaColl(self, print_plot= True):

        self.h_nsigColl = TH1F("n\sigma collimators","",len(self.collimator_spos)*2,0,len(self.collimator_spos))  

        i=0.5
        for ikey in sorted(self.collimator_spos, key=self.collimator_spos.get, reverse=False):
            print ikey, self.collimator_spos[ikey], self.collimator_id[ikey]

            self.h_nsigColl.Fill(i,self.collimator_nsig[ikey])
            self.h_nsigColl.GetXaxis().SetBinLabel(int(i+0.5)*2,ikey)

            i+=1

        self.h_nsigColl.GetYaxis().SetRangeUser(0,40)
        self.h_nsigColl.LabelsOption("v","X")
        self.h_nsigColl.SetFillColor(kBlue)
        #self.h_nsigColl.SetFillStyle(1)

        #min = self.h_nsigColl.GetMinimum()

        c1 = TCanvas("c1","n\sigma collimators",1750,500)
        c1.cd(1)        


        gPad.SetLeftMargin(0.06)
        gPad.SetBottomMargin(0.3)
        gPad.SetRightMargin(0.06)
        gPad.SetGridy()
        self.h_nsigColl.SetStats(0)

        self.h_nsigColl.Draw() #self.h_nsigColl.Draw("B")
        self.h_nsigColl.GetYaxis().SetTitle("# of \sigma")
        self.h_nsigColl.SetTitleOffset(0.4,"Y")                                 
        #line = TLine(0,min,len(self.collimator_spos),min)
        #line.SetLineStyle(2)
        #line.SetLineColor(1)
        #line.SetLineWidth(1)
        #line.Draw("same")

        gPad.Update()
        c1.Update()

        if print_plot == True:
            c1.SaveAs(self.Directory+"/plots/nsigmaColl.png")
            c1.SaveAs(self.Directory+"/plots/nsigmaColl.pdf")
            #c1.SaveAs("/plots/nsigmaColl.C")

        return
            
    def npartColl(self):

        self.collimator_nimp = {}
        self.extracoll_nimp = {}
        self.collimator_nabs = {}
        self.extracoll_nabs = {}

        self.h_nimp = TH1F("nimpacts_collimators","",len(self.collimator_spos)*2,0,len(self.collimator_spos)) 
        self.h_nabs = TH1F("nabs_collimators","",len(self.collimator_spos)*2,0,len(self.collimator_spos)) 

        #initialize
        for icoll in self.collimator_id:
            self.collimator_nimp[icoll] = 0
            self.collimator_nabs[icoll] = 0

        for inDir in self.inDirs:
            if not os.path.isfile(self.Directory + inDir+ "/coll_summary.dat"):
                continue
            fsummary = open(self.Directory + inDir+ "/coll_summary.dat",'r')
            sum_lines = fsummary.readlines()
            fsummary.close()
            for l in sum_lines:
                if l.find("icoll") >=0 : #exclude header line
                    continue
                s_parts = l.split()
                if len(s_parts) < 4:
                    continue
                s_name = s_parts[1]
                if s_name not in self.collimator_nimp.keys():
                    if s_name not in self.extracoll_nimp.keys():
                        self.extracoll_nimp[s_name] = int(s_parts[2])
                        self.extracoll_nabs[s_name] = int(s_parts[3])
                    else:
                        self.extracoll_nimp[s_name] += int(s_parts[2])
                        self.extracoll_nabs[s_name] += int(s_parts[3])
                else:
                    self.collimator_nimp[s_name] += int(s_parts[2])
                    self.collimator_nabs[s_name] += int(s_parts[3])
    
        i=0.5
        for ikey in sorted(self.collimator_spos, key=self.collimator_spos.get, reverse=False):
            print ikey, self.collimator_spos[ikey], self.collimator_id[ikey]

            self.h_nimp.Fill(i,self.collimator_nimp[ikey])
            self.h_nimp.GetXaxis().SetBinLabel(int(i+0.5)*2,ikey)
            self.h_nabs.Fill(i,self.collimator_nabs[ikey])
            self.h_nabs.GetXaxis().SetBinLabel(int(i+0.5)*2,ikey)

            i+=1
   
        self.h_nimp.LabelsOption("v","X")
        self.h_nimp.SetFillColor(kBlue)
        self.h_nimp.SetStats(0)
        self.h_nimp.GetYaxis().SetTitle("# of \sigma")
        self.h_nimp.SetTitleOffset(0.4,"Y")                                 
        c1 = TCanvas("c1","nimp collimators",1750,500)
        c1.cd(1)        
        gPad.SetLeftMargin(0.06)
        gPad.SetBottomMargin(0.3)
        gPad.SetRightMargin(0.06)
        gPad.SetGridy()
        gPad.SetLogy()
        self.h_nimp.Draw() 
        gPad.Update()
        c1.Update()
        c1.SaveAs(self.Directory+"/plots/nimpColl.png")
        c1.SaveAs(self.Directory+"/plots/nimpColl.pdf")

        self.h_nabs.LabelsOption("v","X")
        self.h_nabs.SetFillColor(kBlue)
        self.h_nabs.SetStats(0)
        self.h_nabs.GetYaxis().SetTitle("# of \sigma")
        self.h_nabs.SetTitleOffset(0.4,"Y")                                 
        c1 = TCanvas("c1","nabs collimators",1750,500)
        c1.cd(1)        
        gPad.SetLeftMargin(0.06)
        gPad.SetBottomMargin(0.3)
        gPad.SetRightMargin(0.06)
        self.h_nabs.Draw() 
        gPad.SetGridy()
        gPad.SetLogy()
        gPad.Update()
        c1.Update()
        c1.SaveAs(self.Directory+"/plots/nabsColl.png")
        c1.SaveAs(self.Directory+"/plots/nabsColl.pdf")

        fout = TFile.Open(self.Directory+"/plots/NpartColl.root","recreate")
        fout.cd()
        self.h_nimp.Write()
        self.h_nabs.Write()
        fout.Close()
        print "n impacts on all collim: %i" %self.h_nimp.Integral()
        print "n abs on all collim: %i" %self.h_nabs.Integral()
        print "Collimators not included in plot:"
        print "n impacts: ", self.extracoll_nimp
        print "n abs: ", self.extracoll_nabs

        return
    

    def makeLossPlots(self):

        self.h_coll_norm = TH1F("h_collimator_losses_norm","h_collimator_losses_norm", int(self.ring/self.deltaS), 0., self.ring) 
        self.h_coll = TH1F("h_collimator_losses","h_collimator_losses", int(self.ring/self.deltaS), 0., self.ring)
        self.h_allLHC_losses_norm = TH1F("h_allLHC_losses_norm","h_allLHC_losses_norm", int(self.ring/self.deltaS), 0., self.ring) 
        self.h_coldlosses = TH1F("h_cold_losses","h_cold_losses", int(self.ring/self.deltaS), 0., self.ring)
        self.h_warmlosses = TH1F("h_warm_losses","h_warm_losses", int(self.ring/self.deltaS), 0., self.ring)

        self.collimator_nabs={}
        for key in self.collimator_id.keys():
            self.collimator_nabs[key]= 0

        #Read in coll_summary.dat - note: need to loop over all sub-directories
        for inDir in self.inDirs:
            if not os.path.isfile(self.Directory + inDir+ "/coll_summary.dat"):
                continue
            fsummary = open(self.Directory + inDir+ "/coll_summary.dat",'r')
            sum_lines = fsummary.readlines()
            fsummary.close()
 
            for l in sum_lines:
                if l.find("icoll") >=0 : #exclude header line
                    continue
                #find s position corresponding to collimator
                #print l
                s_parts = l.split()
                if len(s_parts) < 4:
                    continue
                s_name = s_parts[1]
                if s_name not in self.collimator_spos.keys():
                    print "Error: collimator %s not found" %s_name
                    continue
                #if not s_ind == int(s_parts[0]):
                #    print "ERROR: collname ",s_parts[1]," has index ", s_ind ," in CollPositions and ", int(s_parts[0])," in Coll_Summary "
                #    continue
                s_pos =  self.collimator_spos[s_name]
                lenght = self.collimator_length[s_name]
                # now we can fill the histogram:
                #print "Filling coll %s, icoll %i position %f lenght %f with weight %f" %(s_name, int(s_parts[0]), s_pos, lenght, float(s_parts[3]))
                self.h_coll.Fill(s_pos, float(s_parts[3])/lenght)
                self.h_coll_norm.Fill(s_pos, float(s_parts[3]))
                self.collimator_nabs[s_name] += float(s_parts[3])

        print "nabs per collimator: ", self.collimator_nabs

        #Read in LPI_BLP_out.s: info about particles lost in cold/warm sections
        flpi = TFile.Open(self.Directory + "LPI_BLP_out.s.root")
        t = flpi.Get("ntuple")
        for entry in range(t.GetEntries()):
            t.GetEntry(entry)
            #print "particle %i lost at s %f" %(t.np,t.s)
            self.h_allLHC_losses_norm.Fill(t.s)

            #check if it is a cold or warm aperture:
            isWarm = False
            for w in range(len(warm)):
                if ( (t.s >= warm[w][0]) and (t.s < warm[w][1]) ):
                    isWarm = True
                    break
            if isWarm: 
                self.h_warmlosses.Fill(t.s, self.binadjust)
            else:
                self.h_coldlosses.Fill(t.s, self.binadjust)

        fout = TFile(self.Directory + "plots/StandardSetup_losses_bin%1.1f.root" %self.deltaS,"recreate")
        fout.cd()
        self.h_coll.Write()
        self.h_coll_norm.Write()
        self.h_coldlosses.Write()
        self.h_warmlosses.Write()
        self.h_allLHC_losses_norm.Write()
        fout.Close()

        return

    def efficiency(self):

        heff_rad = TH1F("efficiency_vs_amplitude_rad","efficiency_vs_amplitude_rad",40,0.,20.)
        heff_x = TH1F("efficiency_vs_amplitude_x","efficiency_vs_amplitude_x",40,0.,20.)

        heff_y = TH1F("efficiency_vs_amplitude_y","efficiency_vs_amplitude_y",40,0.,20.)
        h_ntot_abs = TH1F("ntot_abs_vs_amplitude","ntot_abs_vs_amplitude",40,0.,20.)

        for inDir in self.inDirs:
            if not os.path.isfile(self.Directory + inDir+ "/efficiency.dat"):
                continue
            fsummary = open(self.Directory + inDir+ "/efficiency.dat",'r')
            sum_lines = fsummary.readlines()
            fsummary.close()
            for l in sum_lines:
                if l.find("rad_sigma") >=0 : #exclude header line
                    continue
                s_parts = l.split()
                if len(s_parts) < 8:
                    continue
                #print "num rad %1.2f, x %1.2f, y %1.2f, n_abs %1.2f" %(float(s_parts[4]),float(s_parts[5]), float(s_parts[6]),float(s_parts[7]) )
                heff_rad.Fill(float(s_parts[0]),float(s_parts[6]))
                heff_x.Fill(float(s_parts[0]),float(s_parts[4]))
                heff_y.Fill(float(s_parts[0]),float(s_parts[5]))
                h_ntot_abs.Fill(float(s_parts[0]),float(s_parts[7]))

        #Now file efficiency efficiency_dpop.dat
        #Take binning from the .dat file
        bins = []
        refDir = self.inDirs[0]
        for i in range(len(self.inDirs)):
            if os.path.isfile(self.Directory + self.inDirs[i]+ "/efficiency_dpop.dat"):
                refDir = self.inDirs[i]
                break
        ffile = open( self.Directory+ refDir+ "/efficiency_dpop.dat",'r')
        lines = ffile.readlines()
        ffile.close()
        for l in lines:
            if l.find("n_dpop") >=0 :
                continue
            bins+= [float(l.split()[0])*100.]
        if bins[0] < 1e-11*100:
            bins[0]=1e-11*100
        print "Bins: ", bins
        my_bins = array('d',bins)

        heff_dpop =  TH1F("efficiency_vs_dpOverp","efficiency_vs_dpOverp",len(bins)-1,my_bins)
        h_ntot_abs_dpop = TH1F("ntot_abs_vs_dpOverp","ntot_abs_vs_dpOverp",len(bins)-1,my_bins)

        for inDir in self.inDirs:
            if not os.path.isfile(self.Directory + inDir+ "/efficiency_dpop.dat"):
                continue
            fsummary = open(self.Directory + inDir+ "/efficiency_dpop.dat",'r')
            sum_lines = fsummary.readlines()
            fsummary.close()
            for l in sum_lines:
                if l.find("n_dpop") >=0 :
                    continue
                s_parts = l.split()
                if len(s_parts) < 4:
                    continue
                bin0 = float(s_parts[0])*100.
                if bin0 < 1e-11*100: 
                    bin0=1e-11*100
                heff_dpop.Fill(bin0,float(s_parts[2]))
                h_ntot_abs_dpop.Fill(bin0,float(s_parts[3]))


        heff_rad_num = heff_rad.Clone("efficiency_vs_amplitude_rad_num")
        heff_x_num = heff_x.Clone("efficiency_vs_amplitude_x_num")
        heff_y_num = heff_y.Clone("efficiency_vs_amplitude_y_num")
        heff_dpop_num = heff_dpop.Clone("efficiency_vs_dpOverp_num")

        heff_rad.Divide(h_ntot_abs)
        heff_x.Divide(h_ntot_abs)
        heff_y.Divide(h_ntot_abs)
        heff_dpop.Divide(h_ntot_abs_dpop)

        for i in range(heff_rad.GetNbinsX()):
            if h_ntot_abs.GetBinContent(i) > 0:
                heff_rad.SetBinError(i, sqrt(heff_rad.GetBinContent(i)*(1-heff_rad.GetBinContent(i))/h_ntot_abs.GetBinContent(i) )  )
                heff_x.SetBinError(i, sqrt(heff_x.GetBinContent(i)*(1-heff_x.GetBinContent(i))/h_ntot_abs.GetBinContent(i) )  )
                heff_y.SetBinError(i, sqrt(heff_y.GetBinContent(i)*(1-heff_y.GetBinContent(i))/h_ntot_abs.GetBinContent(i) )  )

        for i in range(heff_dpop.GetNbinsX()):
           if h_ntot_abs_dpop.GetBinContent(i) > 0:
                if heff_dpop.GetBinContent(i) >= 1.:
                    error = 0.
                else:
                    error = sqrt(heff_dpop.GetBinContent(i)*(1-heff_dpop.GetBinContent(i))/h_ntot_abs_dpop.GetBinContent(i))
                heff_dpop.SetBinError(i, error)  

        fout = TFile(self.Directory + "plots/Efficiency.root" ,"recreate")
        fout.cd()

        heff_rad.SetMarkerStyle(20)
        heff_x.SetMarkerStyle(20)
        heff_y.SetMarkerStyle(20)
        heff_rad_num.SetMarkerStyle(20)
        heff_x_num.SetMarkerStyle(20)
        heff_y_num.SetMarkerStyle(20)
        h_ntot_abs.SetMarkerStyle(20)
        heff_dpop.SetMarkerStyle(20)
        h_ntot_abs_dpop.SetMarkerStyle(20)

        heff_rad.Write()
        heff_x.Write()
        heff_y.Write()
        heff_rad_num.Write()
        heff_x_num.Write()
        heff_y_num.Write()
        h_ntot_abs.Write()
        heff_dpop.Write()
        h_ntot_abs_dpop.Write()
        heff_dpop_num.Write()

        #plot for Ineff vs amplit
        c = TCanvas("Ineff_vs_amplit","c")
        c.cd()
        c.SetLogy()
        c.SetGridy()
        heff_rad.GetXaxis().SetTitle("Radial Aperture, A_{0} [#sigma]")
        #heff_rad.GetXaxis().SetRangeUser(6.,20.)
        heff_rad.GetXaxis().SetRangeUser(7.5,18.)
        heff_rad.GetYaxis().SetTitle("Cleaning inefficiency, #eta (A_{0})")
        heff_rad.GetYaxis().SetRangeUser(1e-5,1.)
        heff_rad.Draw()
        c.Write()
        c.Print(self.Directory + "plots/Efficiency_vs_amplitude.pdf")
        c.Print(self.Directory + "plots/Efficiency_vs_amplitude.png")

        #plot for Ineff vs Doverp
        c = TCanvas("Ineff_vs_dpOverp","c")
        c.cd()
        c.SetLogy()
        #c.SetGridy()
        #c.SetLogx()
        heff_dpop.GetXaxis().SetTitle("#Deltap/p (%)")
        heff_dpop.GetXaxis().SetRangeUser(0.01,1.)
        heff_dpop.GetYaxis().SetTitle("Cleaning inefficiency, #eta (#Deltap/p)")
        heff_dpop.GetYaxis().SetRangeUser(1e-5,5e-3)
        heff_dpop.Draw()
        c.Write()
        c.Print(self.Directory + "plots/Efficiency_vs_dOverp.pdf")
        c.Print(self.Directory + "plots/Efficiency_vs_dOverp.png")
        fout.Close()

        return

    def dispersion(self):
        
        self.g_dispx = TGraph()
        self.g_dispx.SetName("dispersion_x")
        self.g_dispy = TGraph()
        self.g_dispy.SetName("dispersion_y")
        #h_disp_x = TH1F("h_dispersion_b%i_x" %self.Beam,"h_dispersion_b%i_x"%self.Beam,int(self.ring/self.deltaS),0.,self.ring)
        #h_disp_y = TH1F("h_dispersion_b%i_y" %self.Beam,"h_dispersion_b%i_y"%self.Beam,int(self.ring/self.deltaS),0.,self.ring)
        h_disp_x = TH1F("h_dispersion_b%i_x" %self.Beam,"h_dispersion_b%i_x"%self.Beam,int(self.ring/1),0.,self.ring)
        h_disp_y = TH1F("h_dispersion_b%i_y" %self.Beam,"h_dispersion_b%i_y"%self.Beam,int(self.ring/1),0.,self.ring)

        # From CollPositions files get location of collimators
        inputfile = self.baseDirectory + "amplitude.dat"
        f = open(inputfile)
        lines = f.readlines()
        f.close()
        for l in lines:
            if l.find("ielem")>=0:
                continue
            parts = l.split()
            if len(parts) < 15:
                continue
            if float(parts[2])==0.0:
                continue
            #print "Checking element %s at position %2.1f" %(parts[1],float(parts[2]))
            ibin = h_disp_x.FindBin(float(parts[2]))
            h_disp_x.SetBinContent(ibin,float(parts[13]))
            h_disp_y.SetBinContent(ibin,float(parts[14]))
            self.g_dispx.SetPoint(self.g_dispx.GetN(),float(parts[2]),float(parts[13]))
            self.g_dispy.SetPoint(self.g_dispy.GetN(),float(parts[2]),float(parts[14]))

        GraphProperties( self.g_dispx, "s [m]", "Dispersion x [m]", kBlue, 1, kBlue, 20, False)
        GraphProperties( self.g_dispy, "s [m]", "Dispersion x [m]", kRed, 1, kRed, 20, False)        


        h_disp_x.SetLineColor(kRed)
        h_disp_x.SetMarkerColor(kRed)
        h_disp_x.SetLineStyle(1)
        h_disp_x.SetMarkerStyle(20)
        h_disp_y.SetLineColor(kBlue)
        h_disp_y.SetMarkerColor(kBlue)
        h_disp_y.SetLineStyle(1)
        h_disp_y.SetMarkerStyle(20)

        c = TCanvas("Dispersion_B%i"%self.Beam, "Dispersion_B%i"%self.Beam)
        c.cd()
        h_disp_x.GetXaxis().SetTitle("s(m)")
        h_disp_x.GetYaxis().SetTitle("Dispersion")
        h_disp_x.Draw("L")
        h_disp_y.Draw("sameL")
        c.Print(self.Directory+"plots/Dispersion.png")
        c.Print(self.Directory+"plots/Dispersion.pdf")
 
        cg = TCanvas("Graph_Dispersion_B%i"%self.Beam, "Graph_Dispersion_B%i"%self.Beam)
        cg.cd()
        self.g_betax.GetXaxis().SetTitle("s(m)")
        self.g_betax.GetYaxis().SetTitle("Dispersion")
        self.g_betax.Draw("AL")
        self.g_betay.Draw("L")
        c.Print(self.Directory+"plots/Dispersion_graph.png")
        c.Print(self.Directory+"plots/Dispersion_graph.pdf")
 
        self.g_coll_dispx = TGraph()
        self.g_coll_dispx.SetName("coll_dispersion_x")
        for key in self.collimator_id.keys():
            self.g_coll_dispx.SetPoint( self.g_coll_dispx.GetN(), self.collimator_spos[key], self.collimator_dispx[key])
        GraphProperties( self.g_coll_dispx, "s [m]", "Dispersion [m]", kBlue, 1, kBlue, 20, False)
        self.g_coll_dispx.SetTitle("B%i"%self.Beam+"  "+self.Plane)


        f = TFile(self.Directory+"plots/Dispersion.root","recreate")
        f.cd()
        h_disp_x.Write()
        h_disp_y.Write()
        self.g_dispx.Write()
        self.g_dispy.Write()
        self.g_coll_dispx.Write()
        f.Close()

        return

    def makeTransverseDist0(self, redoInput=False):

        infileName = self.Directory + "plots/TransverseDist0.root"
        if not os.path.isfile(infileName) or redoInput:
            self._read_dist0()

        infile=TFile.Open(infileName)
        self.h_x_y_d = infile.Get("x_y_d")
        self.h_x_xp_d = infile.Get("x_xp_d")
        self.h_y_yp_d = infile.Get("y_yp_d") 

        GraphProperties( self.h_x_y_d, "x/#sigma", "y/#sigma", kBlack, 1, kBlack, 1, False )
        GraphProperties( self.h_x_xp_d, "x/#sigma", "x' [mrad]", kBlack, 1, kBlack, 1, False )
        GraphProperties( self.h_y_yp_d, "y/#sigma", "y' [mrad]", kBlack, 1, kBlack, 1, False )

        draw_style="COLZ"

        c6=TCanvas("c6","Dist0 distributions",1750,600)
        c6.Divide(3,1)
        c6.cd(1)
        self.h_x_y_d.Draw(draw_style)
        gPad.SetBottomMargin(0.2)
        gPad.SetRightMargin(0.15)
        self.h_x_y_d.SetLabelSize(0.04)
        self.h_x_y_d.SetLabelSize(0.04,"Y")
        self.h_x_y_d.SetTitleSize(0.04,"Y")
        self.h_x_y_d.SetTitleSize(0.04,"X")
        c6.cd(2)
        gPad.SetBottomMargin(0.2)
        gPad.SetRightMargin(0.15)
        self.h_x_xp_d.Draw(draw_style)
        self.h_x_xp_d.SetLabelSize(0.04,"Y")
        self.h_x_xp_d.SetLabelSize(0.04)
        self.h_x_xp_d.SetTitleSize(0.04,"X")
        self.h_x_xp_d.SetTitleSize(0.04,"Y")
        c6.cd(3)
        self.h_y_yp_d.Draw(draw_style)
        gPad.SetRightMargin(0.15)
        self.h_y_yp_d.SetLabelSize(0.04,"X")
        self.h_y_yp_d.SetLabelSize(0.04,"Y")
        self.h_y_yp_d.SetTitleSize(0.04,"X")
        self.h_y_yp_d.SetTitleSize(0.04,"Y")
        self.h_x_y_d.SetStats(0)
        self.h_x_xp_d.SetStats(0)
        self.h_y_yp_d.SetStats(0)
        gPad.SetBottomMargin(0.2)

        c7=TCanvas("c7","Projections Dist0",1700,600)
        c7.Divide(2,1)
        c7.cd(1)
        gPad.SetLeftMargin(0.18)
        tmp13=self.h_x_y_d.ProjectionX("px150")
        #tmp13.SetXTitle("position in #sigma_{coll}")
        tmp14=self.h_x_y_d.ProjectionY("py151")
        tmp13.SetTitle("X-Y Projections")
        tmp13.SetTitleOffset(0.9,"Y")
        tmp13.SetXTitle("Position in #sigma")
        tmp13.SetYTitle("Counts")
        gPad.SetRightMargin(0.15)
        gPad.SetTopMargin(0.15)
    
        tmp13.Draw()
        #tmp13.SetFillStyle(1001)
        
        tmp13.SetStats(0) 
        tmp14.Draw("SAME")
        #tmp14.SetFillStyle(1001)
        tmp14.SetLineColor(2)
        tmp13.SetLineColor(4)
    
        legend1 = TLegend(0.59,0.63,0.72,0.71);
        legend1.AddEntry(tmp13,"x position","l")
        legend1.AddEntry(tmp14,"y position","l")
        legend1.SetFillStyle(0)
        legend1.Draw()

        c7.cd(2)
        gPad.SetLeftMargin(0.18)
        gPad.SetRightMargin(0.15)
        gPad.SetTopMargin(0.15)
        tmp20=self.h_x_xp_d.ProjectionY("px132")
        #tmp20.SetXTitle("position in #sigma_{coll}")
        tmp21=self.h_y_yp_d.ProjectionY("py15my3")
        tmp20.SetStats(0)
        tmp20.SetTitle("X'-Y' Projections") 
        tmp20.SetXTitle("angle [mrad]")
        tmp20.SetYTitle("Counts")
        tmp20.SetTitleOffset(0.9,"Y")
        tmp20.Draw()
   
        # tmp20.SetXTitle("Angle")
        tmp21.Draw("SAME")
        tmp20.SetLineColor(4)
        tmp21.SetLineColor(2)
        
        legend2 = TLegend(0.6,0.64,0.71,0.71)
        legend2.AddEntry(tmp20,"x'angle","l")
        legend2.AddEntry(tmp21,"y'angle","l")
        legend2.SetFillStyle(0)
        legend2.Draw()
    
        c6.SaveAs(self.Directory+"plots/transverseDist0.png")
        c6.SaveAs(self.Directory+"plots/tranverseDist0.pdf")
        c7.SaveAs(self.Directory+"plots/tranverseDist0_X_Y_XP_YP_projections.pdf")
        c7.SaveAs(self.Directory+"plots/tranverseDist0_X_Y_XP_YP_projections.png")

        return

    def makeFirstImpacts(self, redoInput=False):

        fileName = self.Directory + "plots/FirstImpacts.root"
        if not os.path.isfile(fileName) or redoInput:
            self._read_firstImpacts()
        
        h_x_y_first_imp = {}
        h_x_y_first_imp_notnorm = {}
        infile = TFile.Open(fileName)
        h_x_y_first_imp["TCP.C"] = infile.Get("x_y_f_imp_TCP.C")
        h_x_y_first_imp["TCP.B"] = infile.Get("x_y_f_imp_TCP.B")
        h_x_y_first_imp["TCP.D"] = infile.Get("x_y_f_imp_TCP.D")
        h_x_y_first_imp_notnorm["TCP.C"] = infile.Get("x_y_f_imp_notnorm_TCP.C") 
        h_x_y_first_imp_notnorm["TCP.B"] = infile.Get("x_y_f_imp_notnorm_TCP.B") 
        h_x_y_first_imp_notnorm["TCP.D"] = infile.Get("x_y_f_imp_notnorm_TCP.D") 
        y_yp_f_imp1 = infile.Get("y_yp_f_TCP.B")
        y_yp_f_imp2 = infile.Get("y_yp_f_TCP.C")
        y_yp_f_imp3 = infile.Get("y_yp_f_TCP.D")
        x_xp_f_imp1 = infile.Get("x_xp_f_TCP.B")
        x_xp_f_imp2 = infile.Get("x_xp_f_TCP.C")
        x_xp_f_imp3 = infile.Get("x_xp_f_TCP.D")

        for h in h_x_y_first_imp:
            GraphProperties( h_x_y_first_imp[h], "b/\sigma_{x}", "y/\sigma_{y}", kBlack, 1, kBlack, 1, False )
        for h in h_x_y_first_imp_notnorm:
            GraphProperties( h_x_y_first_imp_notnorm[h], "b", "y", kBlack, 1, kBlack, 1, False )

        c4=TCanvas("c4","Transverse Distribution first_impacts",1750,600)
        c4.Divide(3,1)
        count = 1
        for h in h_x_y_first_imp:
            c4.cd(count)
            gPad.SetRightMargin(0.17)
            h_x_y_first_imp[h].Draw("COLZ")
            h_x_y_first_imp[h].SetStats(0)
            h_x_y_first_imp[h].SetTitleOffset(1,"Y")
            h_x_y_first_imp[h].SetTitleOffset(1,"X")
            h_x_y_first_imp[h].SetLabelSize(0.04)
            h_x_y_first_imp[h].SetLabelSize(0.04,"Y")
            rs.myText(0.45,0.95,kBlack,"%s"%h)
            count +=1

        c5=TCanvas("c5","X-Y projections (TCP.C)",1750,600) 
        c5.Divide(2,1)
        c5.cd(1)
        proj1=h_x_y_first_imp["TCP.C"].ProjectionX("x1")
        proj1.SetYTitle("# of particles")
        proj1.SetTitleOffset(1.1,"Y")
        proj1.GetXaxis().SetRangeUser(-0.1,0.35)
        proj1.Draw()
        proj1.SetStats(0)
        proj1.SetLineColor(4)
        proj1.SetFillColor(4)
        c5.cd(2)
        proj2=h_x_y_first_imp["TCP.C"].ProjectionY("y1")
        proj2.SetYTitle("# of particles")
        proj2.SetTitleOffset(1.1,"Y")
        proj2.Draw()
        proj2.SetStats(0)
        proj2.SetLineColor(2)
        proj2.SetFillColor(2)
        c5.Update()

        c6=TCanvas("c6","X-Yprojections (TCP.B)",1750,600)
        c6.Divide(2,1)
        c6.cd(1)
        proj3=h_x_y_first_imp["TCP.B"].ProjectionX("x2")
        proj3.SetYTitle("# of particles")
        proj3.SetTitleOffset(1,"Y")
        proj3.Draw()
        proj3.SetStats(0)
        proj3.SetLineColor(4)
        proj3.SetFillColor(4)
        gPad.SetRightMargin(0.17)
        c6.cd(2)
        proj4=h_x_y_first_imp["TCP.B"].ProjectionY("y2")
        proj4.SetYTitle("# of particles")
        proj4.SetTitleOffset(1,"Y")
        proj4.Draw()
        proj4.SetStats(0)
        proj4.SetLineColor(2)
        proj4.SetFillColor(2)
        gPad.SetRightMargin(0.17)
        c6.Update()

        c7=TCanvas("c7","X-Y projections (TCP.D)",1750,600)
        c7.Divide(2,1)
        c7.cd(1)
        # gPad.SetRightMargin(0.17)
        c7.cd(1)
        proj3=h_x_y_first_imp["TCP.D"].ProjectionX("x3")
        #  proj3.SetXTitle(" position in #sigma")
        proj3.GetXaxis().SetRangeUser(-0.1,0.35)
        proj3.SetYTitle("# of particles")
        proj3.SetTitleOffset(1,"Y")
        proj3.Draw()
        proj3.SetStats(0)
        proj3.SetLineColor(4)
        proj3.SetFillColor(4)
        gPad.SetRightMargin(0.17)
        c7.cd(2)
        proj4=h_x_y_first_imp["TCP.D"].ProjectionY("y3")
        proj4.SetYTitle("# of particles")
        # proj4.SetTitleOffset(1,"Y")
        proj4.Draw()
        proj4.SetStats(0)
        proj4.SetLineColor(2)
        proj4.SetFillColor(2)
        gPad.SetRightMargin(0.17)
        c7.Update()

        c4.SaveAs(self.Directory +"plots/transverseDist_first_impacts.png")
        c5.SaveAs(self.Directory +"plots/X_Y_TCP_C_projections_first_impacts.png")
        c6.SaveAs(self.Directory +"plots/X_Y_TCP_B_projections_first_impacts.png")
        c7.SaveAs(self.Directory +"plots/X_Y_TCP_D_projections_first_impacts.png")

        c4p=TCanvas("c4p","Transverse Distribution first_impacts",1750,600)
        c4p.Divide(3,1)
        count = 1
        for h in h_x_y_first_imp_notnorm:
            c4p.cd(count)
            gPad.SetRightMargin(0.17)
            h_x_y_first_imp_notnorm[h].Draw("COLZ")
            h_x_y_first_imp_notnorm[h].SetStats(0)
            h_x_y_first_imp_notnorm[h].SetTitleOffset(1,"Y")
            h_x_y_first_imp_notnorm[h].SetTitleOffset(1,"X")
            h_x_y_first_imp_notnorm[h].SetLabelSize(0.04)
            h_x_y_first_imp_notnorm[h].SetLabelSize(0.04,"Y")
            rs.myText(0.45,0.95,kBlack,"%s"%h)
            count +=1

        c5p=TCanvas("c5p","X-Y projections (TCP.C)",1750,600) 
        c5p.Divide(2,1)
        c5p.cd(1)
        proj1=h_x_y_first_imp_notnorm["TCP.C"].ProjectionX("x1")
        proj1.SetYTitle("# of particles")
        proj1.SetTitleOffset(1.1,"Y")
        proj1.Draw()
        proj1.SetStats(0)
        proj1.SetLineColor(4)
        proj1.SetFillColor(4)
        #proj1.GetXaxis().SetRangeUser(0.,0.1e-3)
        c5p.cd(2)
        proj2=h_x_y_first_imp_notnorm["TCP.C"].ProjectionY("y1")
        proj2.SetYTitle("# of particles")
        proj2.SetTitleOffset(1.1,"Y")
        proj2.Draw()
        proj2.SetStats(0)
        proj2.SetLineColor(2)
        proj2.SetFillColor(2)
        c5p.Update()

        c6p=TCanvas("c6p","X-Yprojections (TCP.B)",1750,600)
        c6p.Divide(2,1)
        c6p.cd(1)
        proj3=h_x_y_first_imp_notnorm["TCP.B"].ProjectionX("x2")
        proj3.SetYTitle("# of particles")
        proj3.SetTitleOffset(1,"Y")
        proj3.Draw()
        proj3.SetStats(0)
        proj3.SetLineColor(4)
        proj3.SetFillColor(4)
        gPad.SetRightMargin(0.17)
        c6p.cd(2)
        proj4=h_x_y_first_imp_notnorm["TCP.B"].ProjectionY("y2")
        proj4.SetYTitle("# of particles")
        proj4.SetTitleOffset(1,"Y")
        proj4.Draw()
        proj4.SetStats(0)
        proj4.SetLineColor(2)
        proj4.SetFillColor(2)
        gPad.SetRightMargin(0.17)
        c6p.Update()

        c7p=TCanvas("c7p","X-Y projections (TCP.D)",1750,600)
        c7p.Divide(2,1)
        c7p.cd(1)
        # gPad.SetRightMargin(0.17)
        c7p.cd(1)
        proj3=h_x_y_first_imp_notnorm["TCP.D"].ProjectionX("x3")
        #  proj3.SetXTitle(" position in #sigma")
        proj3.SetYTitle("# of particles")
        proj3.SetTitleOffset(1,"Y")
        proj3.Draw()
        proj3.SetStats(0)
        proj3.SetLineColor(4)
        proj3.SetFillColor(4)
        gPad.SetRightMargin(0.17)
        c7p.cd(2)
        proj4=h_x_y_first_imp_notnorm["TCP.D"].ProjectionY("y3")
        proj4.SetYTitle("# of particles")
        # proj4.SetTitleOffset(1,"Y")
        proj4.Draw()
        proj4.SetStats(0)
        proj4.SetLineColor(2)
        proj4.SetFillColor(2)
        gPad.SetRightMargin(0.17)
        c7p.Update()

        c4p.SaveAs(self.Directory +"plots/transverseDist_first_impacts_notnorm.png")
        c5p.SaveAs(self.Directory +"plots/X_Y_TCP_C_projections_first_impacts_notnorm.png")
        c6p.SaveAs(self.Directory +"plots/X_Y_TCP_B_projections_first_impacts_notnorm.png")
        c7p.SaveAs(self.Directory +"plots/X_Y_TCP_D_projections_first_impacts_notnorm.png")

        return

    def makeImpacts(self, redoInput=False):

        #first try with impacts_real.root
        infileName = ""
        if redoInput:
            self._read_impacts()
        if os.path.isfile(self.Directory + "plots/impacts_real.root"):
            infileName = self.Directory + "plots/impacts_real.root"
            print "Reading plots/impacts_real.root"
        elif os.path.isfile(self.Directory + "plots/FLUKA_impacts.root"):
            infileName = self.Directory + "plots/FLUKA_impacts.root"
            print "Reading plots/FLUKA_impacts.root"
        else:
            self._read_impacts()
        infile = TFile.Open(infileName)
        
        h_impacts = {}        
        h_impacts["x_y"] = {} 
        h_impacts["x_y"]["TCP.C"] = infile.Get("x_y_impacts_TCP.C") 
        h_impacts["x_y"]["TCP.B"] = infile.Get("x_y_impacts_TCP.B") 
        h_impacts["x_y"]["TCP.D"] = infile.Get("x_y_impacts_TCP.D") 
        h_impacts["x_y"]["TCTH.4L1"] = infile.Get("x_y_impacts_TCTH.4L1")
        h_impacts["x_y"]["TCTH.4L3"] = infile.Get("x_y_impacts_TCTH.4L3")
        h_impacts["x_xp"]={}
        h_impacts["x_xp"]["TCP.C"] = infile.Get("x_xp_impacts_TCP.C") 
        h_impacts["x_xp"]["TCP.B"] = infile.Get("x_xp_impacts_TCP.B") 
        h_impacts["x_xp"]["TCP.D"] = infile.Get ("x_xp_impacts_TCP.D") 
        h_impacts["y_yp"]={}
        h_impacts["y_yp"]["TCP.C"] = infile.Get ("y_yp_impacts_TCP.C") 
        h_impacts["y_yp"]["TCP.B"] = infile.Get("y_yp_impacts_TCP.B") 
        h_impacts["y_yp"]["TCP.D"] = infile.Get ("y_yp_impacts_TCP.D") 

        h_spos_abs = {}
        h_spos_abs["TCP.C"] = infile.Get("s_abs_TCP.C") 
        h_spos_abs["TCP.B"] = infile.Get("s_abs_TCP.B") 
        h_spos_abs["TCP.D"] = infile.Get("s_abs_TCP.D") 

        h_nturn_abs= {}
        h_nturn_abs["TCP.C"] = infile.Get("nturn_abs_TCP.C") 
        h_nturn_abs["TCP.B"] = infile.Get("nturn_abs_TCP.B") 
        h_nturn_abs["TCP.D"] = infile.Get("nturn_abs_TCP.D") 

        for hc in h_impacts:
            c = TCanvas("c_%s"%hc , "c_%s"%hc,1750,600)
            c.Divide(3,1)
            count = 1
            for h in h_impacts[hc]:
                if h.find("TCP") < 0:
                    continue
                print "Plotting impacts on primaries: %s for %s" %(hc,h)
                c.cd(count)
                #gPad.SetRightMargin(0.17)
                h_impacts[hc][h].Draw("COLZ")
                h_impacts[hc][h].SetStats(0)
                h_impacts[hc][h].SetTitleOffset(1,"Y")
                h_impacts[hc][h].SetTitleOffset(1,"X")
                h_impacts[hc][h].SetLabelSize(0.04)
                h_impacts[hc][h].SetLabelSize(0.04,"Y")
                rs.myText(0.45,0.95,kBlack,"%s"%h)
                if hc=="x_y":
                    h_impacts[hc][h].GetXaxis().SetTitle("x/#sigma(x)")
                    h_impacts[hc][h].GetYaxis().SetTitle("y/#sigma(y)")
                if hc=="x_xp":
                    h_impacts[hc][h].GetXaxis().SetTitle("x/#sigma(x)")
                    h_impacts[hc][h].GetYaxis().SetTitle("x'/#sigma(x')")
                if hc=="y_yp":
                    h_impacts[hc][h].GetXaxis().SetTitle("y/#sigma(y)")
                    h_impacts[hc][h].GetYaxis().SetTitle("y'/#sigma(y')")
                count +=1
            c.Update()
            c.Print(self.Directory+"plots/%s_TCP_impacts.png" %hc)

            cTCT = TCanvas("cTCT_%s"%hc , "cTCT_%s"%hc,1750,600)
            cTCT.Divide(2,1)
            count = 1
            for h in h_impacts[hc]:
                if h.find("TCT") < 0:
                    continue
                print "Plotting impacts on tertiaries: %s for %s" %(hc,h)
                cTCT.cd(count)
                #gPad.SetRightMargin(0.17)
                h_impacts[hc][h].Draw("COLZ")
                h_impacts[hc][h].SetStats(0)
                h_impacts[hc][h].SetTitleOffset(1,"Y")
                h_impacts[hc][h].SetTitleOffset(1,"X")
                h_impacts[hc][h].SetLabelSize(0.04)
                h_impacts[hc][h].SetLabelSize(0.04,"Y")
                rs.myText(0.45,0.95,kBlack,"%s"%h)
                if hc=="x_y":
                    h_impacts[hc][h].GetXaxis().SetTitle("x/#sigma(x)")
                    h_impacts[hc][h].GetYaxis().SetTitle("y/#sigma(y)")
                if hc=="x_xp":
                    h_impacts[hc][h].GetXaxis().SetTitle("x/#sigma(x)")
                    h_impacts[hc][h].GetYaxis().SetTitle("x'/#sigma(x')")
                if hc=="y_yp":
                    h_impacts[hc][h].GetXaxis().SetTitle("y/#sigma(y)")
                    h_impacts[hc][h].GetYaxis().SetTitle("y'/#sigma(y')")
                count +=1
            cTCT.Update()
            cTCT.Print(self.Directory+"plots/%s_TCT_impacts.png" %hc)
 
            
        c_x_y_proj = TCanvas("c_x_y_proj","c_x_y_proj",1750,600)
        c_x_y_proj.Divide(3,1)
        count = 1 
        for h in h_impacts["x_y"]:
            if h.find("TCP") < 0:
                continue
            c_x_y_proj.cd(count)
            gPad.SetLogy()
            projx=h_impacts["x_y"][h].ProjectionX()
            projy=h_impacts["x_y"][h].ProjectionY()
            maxim = max(projx.GetMaximum(),projy.GetMaximum())
            projx.GetXaxis().SetTitle("x,y/#sigma")
            projx.GetXaxis().SetRangeUser(-10,10)
            projx.GetYaxis().SetRangeUser(1,maxim*10.)
            projx.GetYaxis().SetTitle("#n impacts")
            projx.SetLineColor(kBlue)
            projx.SetFillColor(kBlue)
            projy.SetLineColor(kRed)
            projy.SetFillColor(kRed)
            projx.Draw()
            projy.Draw("same")
            rs.myText(0.45,0.95,kBlack,"%s"%h)
            rs.myBoxText(x=0.45,y=0.85,boxsizeH=0.05,mcolor=kBlue,text="x/#sigma(x)",drawLine=False)
            rs.myBoxText(x=0.45,y=0.8,boxsizeH=0.05,mcolor=kRed,text="y/#sigma(y)",drawLine=False)            
            count+=1
        c_x_y_proj.Print(self.Directory+"plots/x_y_impacts_TCPs_projections.png" )

        cTCT_x_y_proj = TCanvas("cTCT_x_y_proj","cTCT_x_y_proj",1750,600)
        cTCT_x_y_proj.Divide(2,1)
        count = 1 
        for h in h_impacts["x_y"]:
            if h.find("TCT") < 0:
                continue
            cTCT_x_y_proj.cd(count)
            gPad.SetLogy()
            projx=h_impacts["x_y"][h].ProjectionX()
            projy=h_impacts["x_y"][h].ProjectionY()
            maxim = max(projx.GetMaximum(),projy.GetMaximum())
            projx.GetXaxis().SetTitle("x,y/#sigma")
            projx.GetXaxis().SetRangeUser(-20,20)
            projx.GetYaxis().SetRangeUser(1,maxim*10.)
            projx.GetYaxis().SetTitle("#n impacts")
            projx.SetLineColor(kBlue)
            projx.SetFillColor(kBlue)
            projy.SetLineColor(kRed)
            projy.SetFillColor(kRed)
            projx.Draw()
            projy.Draw("same")
            rs.myText(0.45,0.95,kBlack,"%s"%h)
            rs.myBoxText(x=0.45,y=0.85,boxsizeH=0.05,mcolor=kBlue,text="x/#sigma(x)",drawLine=False)
            rs.myBoxText(x=0.45,y=0.8,boxsizeH=0.05,mcolor=kRed,text="y/#sigma(y)",drawLine=False)            
            count+=1
        cTCT_x_y_proj.Print(self.Directory+"plots/x_y_impacts_TCTs_projections.png" )

        c_spos = TCanvas("Impacts_abs_spos","Impacts_abs_spos",1750,600)
        c_spos.Divide(3,1)
        count = 1
        for h in h_spos_abs:
            c_spos.cd(count)
            gPad.SetRightMargin(0.17)
            rs.myText(0.4,1.,1,h)
            h_spos_abs[h].Draw()
            h_spos_abs[h].GetXaxis().SetTitle("s (m)")
            h_spos_abs[h].GetYaxis().SetTitle("# abs")
            rs.myText(0.45,0.95,kBlack,"%s"%h)
            count +=1
        c_spos.Update()
        c_spos.Print(self.Directory+"plots/Impacts_abs_spos.png")

        c_nturn = TCanvas("Impacts_abs_nturn","Impacts_abs_nturn",1750,600)
        c_nturn.Divide(3,1)
        count = 1
        for h in h_nturn_abs:
            c_nturn.cd(count)
            gPad.SetRightMargin(0.17)
            rs.myText(0.4,1.,1,h)
            h_nturn_abs[h].Draw()
            h_nturn_abs[h].GetXaxis().SetTitle("n turn")
            h_nturn_abs[h].GetYaxis().SetTitle("# abs")
            rs.myText(0.45,0.95,kBlack,"%s"%h)
            count +=1
        c_nturn.Update()
        c_nturn.Print(self.Directory+"plots/Impacts_abs_nturn.png")

        return

    def trajectory(self, partnum=1):

        if not os.path.isfile(self.baseDirectory+"tracks2.dat"):
            return
        
        infile = open(self.baseDirectory+"tracks2.dat","r")
        lines = infile.readlines()
        line1 = lines[partnum]
        #only plot tracking for one particle - here chosen to be the first one
        ipart = int(line1.split()[0])
        nturns = int(lines[len(lines)-1].split()[1])
        print "Going to track particle %i for %i turns" %(ipart,nturns)

        #For point 100, 200, 300, 400 plot also the phase-space
        #x_xp_point100 = TH2F("x_xp_point100","x_xp_point100",)

        #initialize Tgraph: one per turn
        x_graph_turns = []
        y_graph_turns = []
        x_xp_graph_turns = []
        y_yp_graph_turns = []
        for n in range(nturns):
            x_graph_turns += [ TGraph() ]
            y_graph_turns += [ TGraph() ]
            x_xp_graph_turns += [ TGraph2D() ]
            y_yp_graph_turns += [ TGraph2D() ]
            GraphProperties( x_graph_turns[n], "s [m]", "x [m]", kBlue, 1, kBlue, -1)
            GraphProperties( y_graph_turns[n], "s [m]", "y [m]", kRed, 1, kRed, -1)
            x_graph_turns[n].SetName("x_trajectory_turn%s" %(n+1))
            y_graph_turns[n].SetName("y_trajectory_turn%s" %(n+1))
            #Graph2DProperties( x_xp_graph_turns[n], "s [m]","x [m]",  "xp [rad]", kBlue, 1, kBlue, -1)
            #Graph2DProperties( y_yp_graph_turns[n], "s [m]", "y [m]","yp [rad]", kRed, 1, kRed, -1)
            x_xp_graph_turns[n].SetName("x_xp_trajectory_turn%s" %(n+1))
            y_yp_graph_turns[n].SetName("x_yp_trajectory_turn%s" %(n+1))

        for i in range(1,len(lines)-1):
            elem = lines[i].split()
            if int(elem[0])!=ipart:
                continue
            spos = float(elem[2])
            iturn = int(elem[1])
            x = float(elem[3])
            y = float(elem[5])
            xp = float(elem[4])
            yp = float(elem[6])
            x_graph_turns[iturn-1].SetPoint(x_graph_turns[iturn-1].GetN(),spos,x)
            y_graph_turns[iturn-1].SetPoint(y_graph_turns[iturn-1].GetN(),spos,y)
            x_xp_graph_turns[iturn-1].SetPoint(x_xp_graph_turns[iturn-1].GetN(),spos,x,xp)
            y_yp_graph_turns[iturn-1].SetPoint(y_yp_graph_turns[iturn-1].GetN(),spos,y,yp)

        #make RMS of each point

        canx = TCanvas("can_x_trajectory_%s_turns" %nturns,"x_trajectory_%s_turns" %nturns)
        canx.cd()
        for n in range(nturns):
            if n==0:
                x_graph_turns[n].Draw("AL")
            else:
                x_graph_turns[n].Draw("L")

        cany = TCanvas("can_y_trajectory_%s_turns" %nturns,"y_trajectory_%s_turns" %nturns)
        for n in range(nturns):
            if n==0:
                y_graph_turns[n].Draw("AL")
            else:
                y_graph_turns[n].Draw("L")
       
        fout = TFile(self.Directory + "plots/Tracks2_part%s.root" %ipart,"recreate")
        fout.cd()
        for n in range(nturns):
            x_graph_turns[n].Write()
            y_graph_turns[n].Write()
            x_xp_graph_turns[n].Write()
            y_yp_graph_turns[n].Write()
        canx.Write()
        cany.Write()
        canx.Print(self.Directory + "plots/x_trajectory_%s_turns.png" %nturns)
        cany.Print(self.Directory + "plots/y_trajectory_%s_turns.png" %nturns)
        fout.Close()

        return

    def studyHalo(self):

        if not os.path.isfile(self.Directory + "coll_ellipse.root"):
            return

        #first find collimator studied (see fort.3)
        fort3 = open(self.Directory + "clean_input/fort.3","r")
        iline = fort3.readlines()[55].split()
        coll_name = iline[4]
        sigx = self.collimator_sigx[coll_name]
        sigy = self.collimator_sigy[coll_name]
        alfax = self.collimator_alfax[coll_name]
        alfay = self.collimator_alfay[coll_name]
        betax = self.collimator_betax[coll_name]
        betay = self.collimator_betay[coll_name]
        coll_id =  self.collimator_id[coll_name]
        print "In Study Halo: selected collimator ", coll_name, " with ID ", coll_id
        print "Sigx = ", sigx, ", betax = ", betax, ", alfax = ", alfax
        print "Sigy = ", sigy, ", betay = ", betay, ", alfay = ", alfay

        bins = [1e-11,0.01e-2, 0.04e-2, 0.08e-2, 0.12e-2, 0.16e-2, 0.2e-2, 0.24e-2, 0.28e-2, 0.32e-2, 0.36e-2, 0.4e-2, 0.44e-2, 0.48e-2, 0.52e-2, 0.56e-2, 0.6e-2, 0.64e-2, 0.68e-2, 0.72e-2, 0.76e-2, 0.8e-2, 0.84e-2, 0.88e-2, 0.92e-2, 0.96e-2, 1.0e-2, 1.1e-2,1.2e-2,1.3e-2,1.4e-2,1.5e-2,1.6e-2,1.8e-2,2.0e-2,3.0e-2,4.0e-2,5.0e-2,6.0e-2,7.0e-2,8.0e-2,9.0e-2,10.0e-2,12.0e-2,14.0e-2,16.0e-2,18.0e-2,20.0e-2]
        my_bins = array('d',bins)

        h_A_vs_dpop = {}
        h_A_vs_dpop['h_secondary_A_vs_dpop'] = TH2F("h_secondary_A_vs_dpop","h_secondary_A_vs_dpop",1000,0.,0.2,150,5.,20.)
        h_A_vs_dpop['h_tertiary_A_vs_dpop'] = TH2F("h_tertiary_A_vs_dpop","h_tertiary_A_vs_dpop",1000,0.,0.2,150,5.,20.)
        h_A_vs_dpop['h_other_A_vs_dpop'] = TH2F("h_other_A_vs_dpop","h_other_A_vs_dpop",1000,0.,0.2,150,5.,20.)
        h_A_vs_dpop['h_secondary_A_vs_dpop_impactOnTCT'] = TH2F("h_secondary_A_vs_dpop_impactOnTCT","h_secondary_A_vs_dpop_impactOnTCT",1000,0.,0.2,125,5.,30.)
        h_A_vs_dpop['h_tertiary_A_vs_dpop_impactOnTCT'] = TH2F("h_tertiary_A_vs_dpop_impactOnTCT","h_tertiary_A_vs_dpop_impactOnTCT",1000,0.,0.2,125,5.,30.)
        h_A_vs_dpop['h_other_A_vs_dpop_impactOnTCT'] = TH2F("h_other_A_vs_dpop_impactOnTCT","h_other_A_vs_dpop_impactOnTCT",1000,0.,0.2,125,5.,30.)
        h_Ax_vs_Ay = {}
        h_Ax_vs_Ay['h_secondary_Ax_vs_Ay'] = TH2F("h_secondary_Ax_vs_Ay","h_secondary_Ax_vs_Ay",100,0.,10,100,0.,10.)
        h_Ax_vs_Ay['h_tertiary_Ax_vs_Ay'] = TH2F("h_tertiary_Ax_vs_Ay","h_tertiary_Ax_vs_Ay",100,0.,10,100,0.,10.)
        h_secondary_dpoverp = TH1F("h_secondary_dpOverp","h_secondary_dpOverp",len(bins)-1,my_bins)
        h_tertiary_dpoverp = TH1F("h_tertiary_dpOverp","h_tertiary_dpOverp",len(bins)-1,my_bins)
        h_other_dpoverp = TH1F("h_other_dpOverp","h_other_dpOverp",len(bins)-1,my_bins)

        infile = TFile.Open(self.Directory + "coll_ellipse.root")
        t = infile.Get("ntuple")
        nEn = t.GetEntries()
        print "Going to process %i entries from coll_ellipse.root" %(nEn)

        ijob = 1
        p_id_old = -1
        nturn_old = -1
        ijob_cs = 1
        p_id_old_cs = -1
        nturn_old_cs = -1
        lastEntry_cs = 0

        for i in range(nEn):
            #if i%5000==0:
                #print "Job ", ijob,  ", Entry ",i
            t.GetEntry(i)
            p_id = t.name
            if (p_id < p_id_old) and (t.iturn < nturn_old ):
                #print "New job - ijob %i" %ijob
                ijob +=1 
            p_id_old = p_id
            nturn_old = t.iturn
            #if t.name > 11000:
            #    continue
            if t.halo ==0:  
                continue
            #print "Looking at coll_ellipse particle %i, turn %i, job %i" %(p_id, t.iturn, ijob)
            amplx = sqrt((t.x*1e-3/sigx)**2 + ( (alfax*t.x*1e-3+ betax*t.xp*1e-3)/sigx )**2)
            amply = sqrt((t.y*1e-3/sigy)**2 + ( (alfay*t.y*1e-3+ betay*t.yp*1e-3)/sigy )**2 )
            amplit = sqrt(amplx**2 + amply**2)
            print "First loop on collellispe: x %f, y %f, xp %f, yp %f, amplit %f, halo %i" %(t.x, t.y, t.xp, t.yp, amplit,t.halo)
            if t.halo ==1:
                h_A_vs_dpop['h_secondary_A_vs_dpop'].Fill(fabs(t.dEoverE),amplit)
                h_secondary_dpoverp.Fill(fabs(t.dEoverE)) 
                h_Ax_vs_Ay['h_secondary_Ax_vs_Ay'].Fill(amplx,amply)
            if t.halo ==3:
                h_A_vs_dpop['h_tertiary_A_vs_dpop'].Fill(fabs(t.dEoverE),amplit)
                h_tertiary_dpoverp.Fill(fabs(t.dEoverE))
                h_Ax_vs_Ay['h_tertiary_Ax_vs_Ay'].Fill(amplx,amply)
            if t.halo >3:
                h_A_vs_dpop['h_other_A_vs_dpop'].Fill(fabs(t.dEoverE),amplit)
                h_other_dpoverp.Fill(fabs(t.dEoverE))
            #print "Start looking at Coll_scatter entry %i" %lastEntry_cs
        
        csfile = TFile.Open(self.Directory + "Coll_Scatter.root")
        tcs = csfile.Get("ntuple")
        ijob = 1
        p_id_old = -1
        nturn_old = -1
        lastEntry = 0
        amplit_old = 0.0
        print "Loop on coll_scatter"
        for ics in range(tcs.GetEntries()):
            tcs.GetEntry(ics)
            if (tcs.np < p_id_old_cs) and (tcs.iturn < nturn_old_cs ):
                ijob_cs +=1
            p_id_old_cs = tcs.np
            nturn_old_cs = tcs.iturn
            if tcs.icoll != coll_id:
                continue
            #print "Found particle hitting icoll %i: np %i, nturn %i, ijob %i" %(coll_id, tcs.np, tcs.iturn, ijob_cs)
            for i in range(lastEntry, lastEntry + 640000):
                t.GetEntry(i)
                p_id = t.name
                if i==lastEntry:
                    nturn_old = t.iturn
                    p_id_old = p_id
                if (p_id < p_id_old) and (t.iturn < nturn_old ):
                    ijob +=1 
                    print "New job - ijob %i, entry %i" %(ijob,i)
                    lastEntry = i
                nturn_old = t.iturn
                p_id_old = p_id
                if t.name != tcs.np:
                    continue
                #print "Coll_ellipse: particle %i, turn %i, entry %i" %(t.name,t.iturn,i)

                if ijob > ijob_cs or (ijob==ijob_cs and p_id > tcs.np) or (ijob==ijob_cs and tcs.np==p_id and t.iturn > tcs.iturn):
                    print "hit limit, particle np %i, nturn %i, ijob %i not found setting lastEntry to in job %i" %(tcs.np, tcs.iturn, ijob_cs, ijob)
                    break
                if ijob!=ijob_cs or tcs.iturn!=t.iturn:
                    continue
                #print "FOUND PARTICLE at Coll ellipse particle %i, job %i, entry %i" %(p_id, ijob, i)
                amplx = sqrt((t.x*1e-3/sigx)**2 + ( (alfax*t.x*1e-3+ betax*t.xp*1e-3)/sigx )**2)
                amply = sqrt((t.y*1e-3/sigy)**2 + ( (alfay*t.y*1e-3+ betay*t.yp*1e-3)/sigy )**2 )
                amplit = sqrt(amplx**2 + amply**2)
                if amplit==amplit_old:
                    continue
                amplit_old = amplit
                print "Particle impacting on TCT: x %f, y %f, xp %f, yp %f, amplit %f, halo %i" %(t.x, t.y, t.xp, t.yp, amplit,t.halo)

                if t.halo ==1: 
                    h_A_vs_dpop['h_secondary_A_vs_dpop_impactOnTCT'].Fill(fabs(t.dEoverE),amplit)
                if t.halo ==3:
                    h_A_vs_dpop['h_tertiary_A_vs_dpop_impactOnTCT'].Fill(fabs(t.dEoverE),amplit)
                if t.halo >3:
                    h_A_vs_dpop['h_other_A_vs_dpop_impactOnTCT'].Fill(fabs(t.dEoverE),amplit)
                #print "Will start looking at coll_ellipse entry %i for job %i" %(lastEntry, ijob)
                #print ""
                break
 

#            for ics in range (lastEntry_cs, tcs.GetEntries()):
#                tcs.GetEntry(ics)
#                if (tcs.np < p_id_old_cs) and (tcs.iturn < nturn_old_cs ):
#                    ijob_cs +=1
#                p_id_old_cs = tcs.np
#                nturn_old_cs = tcs.iturn
#                if ijob > ijob_cs or (ijob==ijob_cs and tcs.np > p_id) or (ijob==ijob_cs and tcs.np==p_id and tcs.iturn > t.iturn):
#                    lastEntry_cs = ics-1
#                    print ""
#                    break
#                if p_id != tcs.np or ijob!=ijob_cs or tcs.iturn!=t.iturn:
#                    continue
#                print "Looking at Coll Scatter particle %i, job %i, entry %i" %(tcs.np, ijob_cs, ics)
#                if tcs.icoll == coll_id:
#                    if t.halo ==1: 
#                        h_A_vs_dpop['h_secondary_A_vs_dpop_impactOnTCT'].Fill(fabs(t.dEoverE),amplit)
#                    if t.halo ==3:
#                        h_A_vs_dpop['h_tertiary_A_vs_dpop_impactOnTCT'].Fill(fabs(t.dEoverE),amplit)
#                    if t.halo >3:
#                        h_A_vs_dpop['h_other_A_vs_dpop_impactOnTCT'].Fill(fabs(t.dEoverE),amplit)
#                    lastEntry_cs = ics
#                    break

        outfile = TFile(self.Directory +"plots/HaloStudies_test_bis.root","recreate")
        outfile.cd()
        for h in h_A_vs_dpop:
            h_A_vs_dpop[h].Write()
            h_A = h_A_vs_dpop[h].ProjectionY().Clone(h_A_vs_dpop[h].GetName().replace("A_vs_dpop","A"))
            h_dpop = h_A_vs_dpop[h].ProjectionX().Clone(h_A_vs_dpop[h].GetName().replace("A_vs_dpop","dpop"))
            h_A.Write()
            h_dpop.Write()
        for h in h_Ax_vs_Ay:
            h_Ax_vs_Ay[h].Write()
        h_secondary_dpoverp.Write()
        h_tertiary_dpoverp.Write()
        h_other_dpoverp.Write()
        outfile.Close()
        return

    def makeAll(self):

        print "Going to produce all plots"
        
        self._print()
        self._print_betafunctions()
        self.nsigmaColl()
        #self._makeLayout_()
        self.npartColl()
        if not self.isFCC:
            self.makeLossPlots()
        self.efficiency()
        self.dispersion()
        #self.studyHalo()
        self.makeTransverseDist0()
        self.makeFirstImpacts()
        self.makeImpacts()
        return
