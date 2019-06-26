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
from functools import partial
sys.path.insert(1, "%s/../.." % os.path.dirname(os.path.abspath(__file__)))


from NanoUpTools.framework.module import Module
from NanoUpTools.framework.datamodel import Object, getvar
from uproot_methods.classes.TLorentzVector  import TLorentzVector

class QCDHEMVeto(Module):
    def __init__(self, name):
        Module.__init__(self, name)
        pass

    def FillCut(self, k, v, events,met, stop, jet, weight):
        th1 = partial(self.th1, cut=k, weight=weight[v])
        th1("nElectron", events["Electron_Stop0l"].sum()[v], 5 , 0 , 5)
        th1("nMuon",     events["Muon_Stop0l"].sum()[v],     5 , 0 , 5)
        th1("MET"        , met.pt[v]        , 100 , 0 , 1000 , title = "MET"                    , xlabel="#slash{E}_{T} [GeV]"      , ylabel="Events")
        th1("METSig"     , stop.METSig[v]   , 10  , 0 , 10   , title = "METSig"                 , xlabel="Sig. #slash{E}_{T} [GeV]" , ylabel="Events")
        th1("NJets"      , stop.nJets[v]    , 10  , 0 , 10   , title = "Number of Jets"         , xlabel="Number of Jets"           , ylabel="Events")
        th1("NBJets"     , stop.nbtags[v]   , 5   , 0 , 5    , title = "Number of b-Jets"       , xlabel="Number of b-Jets"         , ylabel="Events")
        th1("NTops"      , stop.nTop[v]     , 5   , 0 , 5    , title = "Number of Boosted Top"  , xlabel="Number of Boosted Top"    , ylabel="Events")
        th1("NWs"        , stop.nW[v]       , 5   , 0 , 5    , title = "Number of Boosted W"    , xlabel="Number of Boosted W"      , ylabel="Events")
        th1("NResolveds" , stop.nW[v]       , 5   , 0 , 5    , title = "Number of Resolved Top" , xlabel="Number of Resolved Top"   , ylabel="Events")
        th1("NSoftb"     , stop.nSoftb[v]   , 5   , 0 , 5    , title = "Number of Soft-b"       , xlabel="Number of Soft-b"         , ylabel="Events")
        th1("HT"         , stop.HT[v]       , 150 , 0 , 1500 , title = "HT"                     , xlabel="HT"                       , ylabel="Events")
        th1("Mtb"        , stop.Mtb[v]      , 100 , 0 , 500  , title = "Mtb"                    , xlabel="Mtb"                      , ylabel="Events")
        th1("Ptb"        , stop.Ptb[v]      , 100 , 0 , 500  , title = "Ptb"                    , xlabel="Ptb"                      , ylabel="Events")
        th1("ISRJetPt"   , stop.ISRJetPt[v] , 100 , 0 , 1000 , title = "ISRJetPt"           , xlabel="ISRJetPt"                 , ylabel="Events")

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ All Jets ~~~~~
        NHF                = jet.neHEF                           # pfjet->neutralHadronEnergyFraction();
        NEMF               = jet.neEmEF                          # pfjet->neutralEmEnergyFraction();
        CHF                = jet.chHEF                           # pfjet->chargedHadronEnergyFraction();
        MUF                = jet.muEF                            # pfjet->muonEnergyFraction();
        CEMF               = jet.chEmEF                          # pfjet->chargedEmEnergyFraction();
        CHM                = jet.chHadMult+jet.elMult+jet.muMult # pfjet->chargedMultiplicity();
        NumConst           = jet.nConstituents                   # pfjet->chargedMultiplicity()+pfjet->neutralMultiplicity();

        th1("jeteta"       , jet.eta[v]  , 100 , -5 , 5    ,  title = "Jet eta"                         , xlabel ="Jet #eta"                        , ylabel="NO. of Jets" , color='blue')
        th1("jetphi"       , jet.phi[v]  , 100 , -5 , 5    ,  title = "Jet phi"                         , xlabel ="Jet #phi"                        , ylabel="NO. of Jets" , color='blue')
        th1("jetpt"        , jet.pt[v]   , 100 , 0  , 1000 ,  title = "Jet Pt"                          , xlabel ="Jet p_{T} [GeV]"                 , ylabel="NO. of Jets" , color='blue')
        th1("jet_NHF"      , NHF[v]      , 10  , 0  , 1    ,  title = "Jet neutralHadronEnergyFraction" , xlabel ="Jet neutralHadronEnergyFraction" , ylabel="NO. of Jets" , color='blue')
        th1("jet_NEMF"     , NEMF[v]     , 10  , 0  , 1    ,  title = "Jet neutralEmEnergyFraction"     , xlabel ="Jet neutralEmEnergyFraction"     , ylabel="NO. of Jets" , color='blue')
        th1("jet_CHF"      , CHF[v]      , 10  , 0  , 1    ,  title = "Jet chargedHadronEnergyFraction" , xlabel ="Jet chargedHadronEnergyFraction" , ylabel="NO. of Jets" , color='blue')
        th1("jet_MUF"      , MUF[v]      , 10  , 0  , 1    ,  title = "Jet muonEnergyFraction"          , xlabel ="Jet muonEnergyFraction"          , ylabel="NO. of Jets" , color='blue')
        th1("jet_CEMF"     , CEMF[v]     , 10  , 0  , 1    ,  title = "Jet chargedEmEnergyFraction"     , xlabel ="Jet chargedEmEnergyFraction"     , ylabel="NO. of Jets" , color='blue')
        th1("jet_CHM"      , CHM[v]      , 10  , 0  , 1    ,  title = "Jet chargedMultiplicity"         , xlabel ="Jet chargedMultiplicity"         , ylabel="NO. of Jets" , color='blue')
        th1("jet_NumConst" , NumConst[v] , 10  , 0  , 100  ,  title = "Jet nConstituents"               , xlabel ="Jet nConstituents"               , ylabel="NO. of Jets" , color='blue')

        jetsel = (jet.pt[v] > 20) & (jet.pt[v] < 30)& (abs(jet.eta[v]) < 2.4)
        th1("jet20eta"       , jet.eta[v][jetsel]  , 100 , -5 , 5    ,  title = "Jet eta"                         , xlabel ="Jet #eta"                        , ylabel="NO. of Jets" , color='blue')
        th1("jet20phi"       , jet.phi[v][jetsel]  , 100 , -5 , 5    ,  title = "Jet phi"                         , xlabel ="Jet #phi"                        , ylabel="NO. of Jets" , color='blue')
        th1("jet20pt"        , jet.pt[v][jetsel]    , 100 , 0  , 1000 ,  title = "Jet Pt"                          , xlabel ="Jet p_{T} [GeV]"                 , ylabel="NO. of Jets" , color='blue')
        th1("jet20_NHF"      , NHF[v][jetsel]      , 10  , 0  , 1    ,  title = "Jet neutralHadronEnergyFraction" , xlabel ="Jet neutralHadronEnergyFraction" , ylabel="NO. of Jets" , color='blue')
        th1("jet20_NEMF"     , NEMF[v][jetsel]     , 10  , 0  , 1    ,  title = "Jet neutralEmEnergyFraction"     , xlabel ="Jet neutralEmEnergyFraction"     , ylabel="NO. of Jets" , color='blue')
        th1("jet20_CHF"      , CHF[v][jetsel]       , 10  , 0  , 1    ,  title = "Jet chargedHadronEnergyFraction" , xlabel ="Jet chargedHadronEnergyFraction" , ylabel="NO. of Jets" , color='blue')
        th1("jet20_MUF"      , MUF[v][jetsel]       , 10  , 0  , 1    ,  title = "Jet muonEnergyFraction"          , xlabel ="Jet muonEnergyFraction"          , ylabel="NO. of Jets" , color='blue')
        th1("jet20_CEMF"     , CEMF[v][jetsel]      , 10  , 0  , 1    ,  title = "Jet chargedEmEnergyFraction"     , xlabel ="Jet chargedEmEnergyFraction"     , ylabel="NO. of Jets" , color='blue')
        th1("jet20_CHM"      , CHM[v][jetsel]       , 10  , 0  , 1    ,  title = "Jet chargedMultiplicity"         , xlabel ="Jet chargedMultiplicity"         , ylabel="NO. of Jets" , color='blue')
        th1("jet20_NumConst" , NumConst[v][jetsel]  , 10  , 0  , 100  ,  title = "Jet nConstituents"               , xlabel ="Jet nConstituents"               , ylabel="NO. of Jets" , color='blue')
        th1("jet20_NumConst" , NumConst[v][jetsel] , 10  , 0  , 100  , title = "Jet nConstituents"               , xlabel ="Jet nConstituents"               , ylabel="NO. of Jets" , color='blue')

    def GetEventWeight(self, events):
        weights = np.sign(events["Stop0l_evtWeight"])
        if self.isData:
            return weights
        weights *= getvar(events, "BTagWeight", 1)
        weights *= getvar(events, "puWeight", 1)
        weights *= getvar(events, "PrefireWeight", 1)
        weights *= getvar(events, "ISRWeight", 1)
        # Lepton SF
        # weights *= events["Electron_VetoSF"][events["Electron_Stop0l"]].prod()
        # weights *= events["Muon_LooseSF"][events["Muon_Stop0l"]].prod()
        # weights *= events["Electron_VetoSF"][events["Electron_Stop0l"]]* events["Muon_LooseSF"][events["Muon_Stop0l"]]
        return weights

    def analyze(self, events):
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ Get objects ~~~~~
        stop = Object(events, "Stop0l")
        pas = Object(events, "Pass")
        met = Object(events, "MET")
        jet = Object(events, "Jet", events["Jet_Stop0l"])

        # ## 2016 JetID Tight
        # jetID1 = (np.abs(jet.eta) <=2.7 ) & ( jet.neHEF <0.90 ) & (jet.neEmEF < 0.90) & (jet.nConstituents > 1)  
        # jetID2 = (np.abs(jet.eta) <=2.4 ) & ( jet.neHEF <0.90 ) & (jet.neEmEF < 0.90) & (jet.nConstituents > 1)  & (jet.chHEF > 0) & (jet.chHadMult+jet.elMult+jet.muMult  > 0) & (jet.chEmEF < 0.99)
        # jetID3 = (np.abs(jet.eta) > 2.7 ) & (np.abs(jet.eta) <= 3.0 ) & ( jet.neEmEF > 0.01 ) & (jet.neHEF < 0.98) & (jet.nConstituents - (jet.chHadMult+jet.elMult+jet.muMult) > 2)
        # jetID4 = (np.abs(jet.eta) > 3.0 ) & (jet.neEmEF < 0.90) & (jet.nConstituents - (jet.chHadMult+jet.elMult+jet.muMult) > 10)

        # # ## 2017 JetID Tight
        # # jetID1 = (np.abs(jet.eta) <=2.7 ) & ( jet.neHEF <0.90 ) & (jet.neEmEF < 0.90) & (jet.nConstituents > 1)  
        # # jetID2 = (np.abs(jet.eta) <=2.4 ) & ( jet.neHEF <0.90 ) & (jet.neEmEF < 0.90) & (jet.nConstituents > 1)  & (jet.chHEF > 0) & (jet.chHadMult+jet.elMult+jet.muMult  > 0)
        # # jetID3 = (np.abs(jet.eta) > 2.7 ) & (np.abs(jet.eta) <= 3.0 ) & ( jet.neEmEF > 0.02 ) & (jet.neEmEF < 0.99) & (jet.nConstituents - (jet.chHadMult+jet.elMult+jet.muMult) > 2)
        # # jetID4 = (np.abs(jet.eta) > 3.0 ) & ( jet.neHEF > 0.02 ) & (jet.neEmEF < 0.90) & (jet.nConstituents - (jet.chHadMult+jet.elMult+jet.muMult) > 10)

        # # jetID1 = (jet.pt > 30) & (np.abs(jet.eta) <=2.7 ) & ( jet.neHEF <0.90 ) & (jet.neEmEF < 0.90) & (jet.nConstituents > 1)  
        # # jetID2 = (jet.pt > 30) & (np.abs(jet.eta) <=2.4 ) & ( jet.neHEF <0.90 ) & (jet.neEmEF < 0.90) & (jet.nConstituents > 1)  & (jet.chHEF > 0) & (jet.chHadMult+jet.elMult+jet.muMult  > 0)
        # # jetID3 = (jet.pt > 30) & (np.abs(jet.eta) > 2.7 ) & (np.abs(jet.eta) <= 3.0 ) & ( jet.neEmEF > 0.02 ) & (jet.neEmEF < 0.99) & (jet.nConstituents - (jet.chHadMult+jet.elMult+jet.muMult) > 2)
        # # jetID4 = (jet.pt > 30) & (np.abs(jet.eta) > 3.0 ) & ( jet.neHEF > 0.02 ) & (jet.neEmEF < 0.90) & (jet.nConstituents - (jet.chHadMult+jet.elMult+jet.muMult) > 10)
        # # ## 2018 JetID Tight
        # # jetID1 = (jet.pt > 30) & (np.abs(jet.eta) <=2.6 ) & ( jet.neHEF <0.90 ) & (jet.neEmEF < 0.90) & (jet.nConstituents > 1)  & (jet.chHEF > 0) & (jet.chHadMult+jet.elMult+jet.muMult  > 0)
        # # jetID2 = (jet.pt > 30) & (np.abs(jet.eta) > 2.6 ) & (np.abs(jet.eta) <= 2.7 ) & ( jet.neHEF <0.90 ) & (jet.neEmEF < 0.99) & (jet.chHadMult+jet.elMult+jet.muMult  > 0)
        # # jetID3 = (jet.pt > 30) & (np.abs(jet.eta) > 2.7 ) & (np.abs(jet.eta) <= 3.0 ) & ( jet.neEmEF > 0.02 ) & (jet.neEmEF < 0.99) & (jet.nConstituents - (jet.chHadMult+jet.elMult+jet.muMult) > 2)
        # # jetID4 = (jet.pt > 30) & (np.abs(jet.eta) > 3.0 ) & ( jet.neHEF > 0.2 ) & (jet.neEmEF < 0.90) & (jet.nConstituents - (jet.chHadMult+jet.elMult+jet.muMult) > 10)

    
        # localJetID = (jetID1 | jetID2 | jetID3 | jetID4)
        # nanoJetID = (jet.jetId == 6)
        # # diff = np.where(localJetID != nanoJetID)
        # # print(localJetID[diff], nanoJetID[diff])
        # print(np.unique((localJetID == nanoJetID).flatten()))

        self.th1("nElectron", events["Electron_Stop0l"].sum(), 5 , 0 , 5)
        self.th1("nMuon" , events["Muon_Stop0l"].sum(), 5 , 0 , 5)
        self.th1("nJet30" , jet.pt[(jet.pt>30) & jet.Stop0l], 5 , 0 , 5)
        self.th1("EventFiler" , events["Pass_EventFilter"], 2 , 0 , 2)
        self.th1("JetID" , events["Pass_JetID"], 2 , 0 , 2)

        weight = self.GetEventWeight(events)
        trigger_MET = pas.trigger_MET
        if not self.isData:
            trigger_MET  = np.ones_like(trigger_MET)

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ Selection ~~~~~
        CRdict = {
            "JetID"   : trigger_MET & pas.JetID,
            "QCD"     : trigger_MET & pas.QCDCR,
            "QCDhigh" : trigger_MET & pas.QCDCR_highDM,
            "QCDlow"  : trigger_MET & pas.QCDCR_lowDM,
            "LL"      : trigger_MET & pas.LLCR,
            "LLhigh"  : trigger_MET & pas.LLCR_highDM,
            "LLlow"   : trigger_MET & pas.LLCR_lowDM,
        }

        if not self.isData :
            CRdict["Base"]     = trigger_MET & pas.Baseline
            CRdict["Basehigh"] = trigger_MET & pas.highDM
            CRdict["Baselow"]  = trigger_MET & pas.lowDM

        HEMdict ={
            "HEM20" :  pas.HEMVeto20 ,
            "HEM30" :  pas.HEMVeto30 ,
            "exHEM20" :  pas.exHEMVeto20 ,
            "exHEM30" :  pas.exHEMVeto30 ,
        }

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ Set cuts ~~~~~
        cutdict = {
            "NoCut"          : np.ones(pas.Baseline.shape, dtype=bool),
        }
        cutdict.update(CRdict)
        for kc, vc in CRdict.items():
            for kh, vh  in HEMdict.items():
                cutdict["%s_%s" %( kc, kh )] = vc & vh

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ Plotting ~~~~~
        for k, v in cutdict.items():
            self.FillCut(k, v, events, met, stop, jet, weight)
        return True

