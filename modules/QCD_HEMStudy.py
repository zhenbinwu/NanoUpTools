#!/usr/bin/env python
# encoding: utf-8

# File        : QCD_HEMStudy.py
# Author      : Ben Wu
# Contact     : benwu@fnal.gov
# Date        : 2019 Mar 07
#
# Description :

import sys
import os
import numpy as np
sys.path.insert(1, "%s/../.." % os.path.dirname(os.path.abspath(__file__)))


from NanoUpTools.framework.module import Module
from NanoUpTools.framework.datamodel import Object

class QCDHEMVeto(Module):
    def __init__(self, name):
        Module.__init__(self, name)
        pass

    def analyze(self, events):
        stop = Object(events, "Stop0l")
        pas = Object(events, "Pass")
        met = Object(events, "MET")
        jet = Object(events, "Jet", events["Jet_Stop0l"])

        HEMJets = (jet.eta > -3.0) & (jet.eta<-1.4) & (jet.phi > -1.57) & (jet.phi<-0.87)
        PassHEMVeto = [~np.any(k) for k in HEMJets]

        HEMJets2 = (jet.pt > 30) & HEMJets
        PassHEMVeto2 = [~np.any(k) for k in HEMJets2]

        HEMJets3 = (jet.eta > -3.2) & (jet.eta<-1.2) & (jet.phi > -1.77) & (jet.phi<-0.67)
        PassHEMVeto3 = [~np.any(k) for k in HEMJets3]

        HEMJets4 = (jet.pt > 30) & HEMJets3
        PassHEMVeto4 = [~np.any(k) for k in HEMJets4]

        BaseHEMVeto = PassHEMVeto & pas.Baseline
        BaseHEMVeto2 = PassHEMVeto2 & pas.Baseline
        BaseHEMVeto3 = PassHEMVeto3 & pas.Baseline
        BaseHEMVeto4 = PassHEMVeto4 & pas.Baseline

        cutdict = {
            "NoCut" : np.ones(BaseHEMVeto.shape, dtype=bool),
            "Baseline" : pas.Baseline,
            "BaseHEMVeto" : BaseHEMVeto,
            "BaseHEMVeto2" : BaseHEMVeto2,
            "BaseHEMVeto3" : BaseHEMVeto3,
            "BaseHEMVeto4" : BaseHEMVeto4,
        }
        self.th1("nPDF"       , events["nLHEPdfWeight"]                       , 200 , 0 , 200 )
        self.th1("orgPU"      , events["Pileup_nTrueInt"]                     , 200 , 0 , 200)
        self.th1("weightedPU" , events["Pileup_nTrueInt"]* events["puWeight"] , 200 , 0 , 200)
        self.th1("orgPV"      , events["PV_npvsGood"]                         , 200 , 0 , 200)
        self.th1("weightedPV" , events["PV_npvsGood"]* events["puWeight"]     , 200 , 0 , 200)

        for k, v in cutdict.items():
            self.th1("MET_" + k        , met.pt[v]        , 100 , 0 , 1000 ,
                     title = "MET Passing %s " % k                    , xlabel="#slash{E}_{T} [GeV]"      , ylabel="Events")
            self.th1("METSig_" + k     , stop.METSig[v]   , 10  , 0 , 10   ,
                     title = "METSig Passing %s " % k                 , xlabel="Sig. #slash{E}_{T} [GeV]" , ylabel="Events")
            self.th1("NJets_" + k      , stop.nJets[v]    , 10  , 0 , 10   ,
                     title = "Number of Jets Passing %s " % k         , xlabel="Number of Jets"           , ylabel="Events")
            self.th1("NBJets_" + k     , stop.nbtags[v]   , 5   , 0 , 5    ,
                     title = "Number of b-Jets Passing %s " % k       , xlabel="Number of b-Jets"         , ylabel="Events")
            self.th1("NTops_" + k      , stop.nTop[v]     , 5   , 0 , 5    ,
                     title = "Number of Boosted Top Passing %s " % k  , xlabel="Number of Boosted Top"    , ylabel="Events")
            self.th1("NWs_" + k        , stop.nW[v]       , 5   , 0 , 5    ,
                     title = "Number of Boosted W Passing %s " % k    , xlabel="Number of Boosted W"      , ylabel="Events")
            self.th1("NResolveds_" + k , stop.nW[v]       , 5   , 0 , 5    ,
                     title = "Number of Resolved Top Passing %s " % k , xlabel="Number of Resolved Top"   , ylabel="Events")
            self.th1("NSoftb_" + k     , stop.nSoftb[v]   , 5   , 0 , 5    ,
                     title = "Number of Soft-b Passing %s " % k       , xlabel="Number of Soft-b"         , ylabel="Events")
            self.th1("HT_" + k         , stop.HT[v]       , 150 , 0 , 1500 ,
                     title = "HT Passing %s " % k                     , xlabel="HT"                       , ylabel="Events")
            self.th1("Mtb_" + k        , stop.Mtb[v]      , 100 , 0 , 500  ,
                     title = "Mtb Passing %s " % k                    , xlabel="Mtb"                      , ylabel="Events")
            self.th1("Ptb_" + k        , stop.Ptb[v]      , 100 , 0 , 500  ,
                     title = "Ptb Passing %s " % k                    , xlabel="Ptb"                      , ylabel="Events")
            self.th1("ISRJetPt_" + k   , stop.ISRJetPt[v] , 100 , 0 , 1000 ,
                     title = "ISRJetPt Passing %s " % k               , xlabel="ISRJetPt"                 , ylabel="Events")

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ All Jets ~~~~~
            self.th1("jeteta_" + k, jet.eta[v], 100, -5, 5    , title = "Jet eta" , xlabel ="Jet #eta", ylabel="NO. of Jets", color='blue')
            self.th1("jetphi_" + k, jet.phi[v], 100, -5, 5    , title = "Jet phi" , xlabel ="Jet #phi", ylabel="NO. of Jets", color='blue')
            self.th1("jetpt_"  + k, jet.pt[v], 100,  0, 1000 ,  title = "Jet Pt", xlabel ="Jet p_{T} [GeV]", ylabel="NO. of Jets", color='blue')

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ Leading Jets ~~~~~
            self.th1("jet1eta_" + k, jet.eta[v][0], 100, -5, 5    , title = "jet1 eta" , xlabel ="jet1 #eta", ylabel="Events", color='blue')
            self.th1("jet1phi_" + k, jet.phi[v][0], 100, -5, 5    , title = "jet1 phi" , xlabel ="jet1 #phi", ylabel="Events", color='blue')
            self.th1("jet1pt_"  + k, jet.pt[v][0], 100,  0, 1000 ,  title = "jet1 Pt", xlabel ="jet1 p_{T} [GeV]", ylabel="Events", color='blue')
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ 2nd Leading Jets ~~~~~
            self.th1("jet2eta_" + k, jet.eta[v][1], 100, -5, 5    , title = "jet2 eta" , xlabel ="jet2 #eta", ylabel="Events", color='blue')
            self.th1("jet2phi_" + k, jet.phi[v][1], 100, -5, 5    , title = "jet2 phi" , xlabel ="jet2 #phi", ylabel="Events", color='blue')
            self.th1("jet2pt_"  + k, jet.pt[v][1], 100,  0, 1000 ,  title = "jet2 Pt", xlabel ="jet2 p_{T} [GeV]", ylabel="Events", color='blue')
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ 3rd Leading Jets ~~~~~
            self.th1("jet3eta_" + k, jet.eta[v][2], 100, -5, 5    , title = "jet3 eta" , xlabel ="jet3 #eta", ylabel="Events", color='blue')
            self.th1("jet3phi_" + k, jet.phi[v][2], 100, -5, 5    , title = "jet3 phi" , xlabel ="jet3 #phi", ylabel="Events", color='blue')
            self.th1("jet3pt_"  + k, jet.pt[v][2], 100,  0, 1000 ,  title = "jet3 Pt", xlabel ="jet3 p_{T} [GeV]", ylabel="Events", color='blue')
        return True

