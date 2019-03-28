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
import ROOT
sys.path.insert(1, "%s/../.." % os.path.dirname(os.path.abspath(__file__)))


from NanoUpTools.framework.module import Module
from NanoUpTools.framework.datamodel import Object

style = {
    "FJak4"  : (ROOT.kBlack,    20, 1.5),
    "ktE4"   : (ROOT.kGray+1,   21, 1.5),
    "dRE4"   : (ROOT.kGreen+2,  22, 1.5),
    "dRWTA4" : (ROOT.kViolet+2, 23, 1.5),
    "ktWTA4" : (ROOT.kOrange+7, 24, 1.5),
    "seed4"  : (ROOT.kBlue+1,   25, 1.5),
}

class P2L1Jet(Module):
    def __init__(self, name, jetlabel = "AK4", jetID = "al4L1PuppiJets"):
        Module.__init__(self, name)
        self.jetID = jetID
        self.jetlabel = jetlabel
        self.ptrange = [0, 10,20,25,30,35,40,45,50,55,60,70,80,90,100,120,140,160,200,250,300, 600]
        self.color=ROOT.kBlack
        self.markerstyle=20
        self.markersize=1.5
        for k, v in style.items():
            if k in jetlabel:
                self.color, self.markerstyle, self.markersize = v
                break


    def FillJetRate(self, jet):
        self.th1("RatePT", jet.pt.max(), 100, 0, 500, trigRate=True, title="JetPt Rate;Jet Pt;Rate [kHz]")
        self.th1("RatePTEta24", jet.pt[abs(jet.eta)<=2.4].max(), 100, 0, 500,
                 trigRate=True, title="JetPt Rate;Jet Pt (#eta < 2.4);Rate [kHz]")
        self.th1("RatePTEta30", jet.pt[abs(jet.eta)<=3].max(), 100, 0, 500,
                 trigRate=True, title="JetPt Rate;Jet Pt (#eta <3);Rate [kHz]")
        self.th1("DoubleJetRatePT", jet.pt.pad(2).fillna(0)[:, 1], 100, 0, 500,
                 trigRate=True, title="JetPt DoubleJetRate;Jet Pt;DoubleJetRate [kHz]")
        self.th1("DoubleJetRatePTEta24",
                 jet.pt[abs(jet.eta)<=2.4].pad(2).fillna(0)[:, 1], 100, 0, 500,
                 trigRate=True, title="JetPt DoubleJetRate;Jet Pt (#eta < 2.4);DoubleJetRate [kHz]")
        self.th1("DoubleJetRatePTEta30",
                 jet.pt[abs(jet.eta)<=3].pad(2).fillna(0)[:, 1], 100, 0, 500,
                 trigRate=True, title="JetPt DoubleJetRate;Jet Pt (#eta <3);DoubleJetRate [kHz]")
        self.th1("TriJetRatePT", jet.pt.pad(3).fillna(0)[:, 2], 100, 0, 400,
                 trigRate=True, title="JetPt TriJetRate;Jet Pt;TriJetRate [kHz]")
        self.th1("TriJetRatePTEta24",
                 jet.pt[abs(jet.eta)<=2.4].pad(3).fillna(0)[:, 2], 100, 0, 400,
                 trigRate=True, title="JetPt TriJetRate;Jet Pt (#eta < 2.4);TriJetRate [kHz]")
        self.th1("TriJetRatePTEta30",
                 jet.pt[abs(jet.eta)<=3].pad(3).fillna(0)[:, 2], 100, 0, 400,
                 trigRate=True, title="JetPt TriJetRate;Jet Pt (#eta <3);TriJetRate [kHz]")
        self.th1("QuadJetRatePT", jet.pt.pad(4).fillna(0)[:, 3], 100, 0, 200,
                 trigRate=True, title="JetPt QuadJetRate;Jet Pt;QuadJetRate [kHz]")
        self.th1("QuadJetRatePTEta24", jet.pt[abs(jet.eta)<=2.4].pad(4).fillna(0)[:, 3], 100, 0, 200,
                 trigRate=True, title="JetPt QuadJetRate;Jet Pt (#eta < 2.4);QuadJetRate [kHz]")
        self.th1("QuadJetRatePTEta30", jet.pt[abs(jet.eta)<=3].pad(4).fillna(0)[:, 3], 100, 0, 200,
                 trigRate=True, title="JetPt QuadJetRate;Jet Pt (#eta <3);QuadJetRate [kHz]")

    def analyze(self, events):
        gen = Object(events, "GenJets")
        fj = Object(events, "al4L1"+self.jetID.split("L1")[-1])
        jet = Object(events, self.jetID)
        if jet is None:
            print(self.jetID, self.jetlabel)


        self.FillJetRate(jet)

        x = jet.cross(gen)
        matched = x.i0.delta_r(x.i1) < 0.4
        response = x[matched].i0.pt / x[matched].i1.pt
        self.th1("localJetResponse", response, 40, 0, 2, title = "Jet Response",
                 xlabel="JetResponse", ylabel="Events", color=self.color)

        jet30 = jet[jet.pt >30]
        matchjet = jet[jet.gendr < 0.4]
        self.resolution= self.th1("PerfResolution", None, self.ptrange)
        self.response= self.th1("PerfResponse", None, self.ptrange)
        self.th2("GenJetetaphi", gen.eta, gen.phi,
                 (10, -5, 5   , 10, -5, 5 )  , title = "Gen Jet counts" )
        self.th2("recoJetetaphi", jet.eta, jet.phi,
                 (10, -5, 5   , 10, -5, 5  ) , title = "Jet 2D" )

        self.th1("nGenJet", gen.counts, 20, 0, 20,
                 title = "Gen Jet counts" , xlabel="NO of GenJet", ylabel="Events")
        self.th1("GenJetPt", gen.pt, self.ptrange , title = "Gen Jet pt", xlabel="GenJet p_{T} [GeV]", ylabel="Events")
        self.th1("RecoJetPt", jet.pt, 200, 0, 600 , title = "Reco Jet pt", xlabel="RecoJet p_{T} [GeV]", ylabel="Events")
        self.th1("LeadingRecoJetPt", jet.pt.max(), 200, 0, 600   , title = "Leading Reco Jet pt", xlabel="Leading RecoJet p_{T} [GeV]", ylabel="Events")
        self.th1("LeadingRecoJetEta", jet.eta[jet.pt.argmax()], 10, -10, 10   , title = "Leading Reco Jet eta", xlabel="Leading RecoJet #eta", ylabel="Events")
        self.th1("nRecoJet", jet.counts, 20, 0, 20   , title = "Reco Jet counts", xlabel="NO of RecoJet", ylabel="Events")
        self.th1("nRecoJet30", jet30.counts, 20, 0, 20   , title = "Reco Jet counts >30", xlabel="NO of RecoJet (p_{T}>30)", ylabel="Events")
        self.th1("matchGenJetPt", jet[jet.gendr < 0.4].genpt, self.ptrange, title = "match Gen Jet pt" , xlabel="Matched GenJet p_{T} [GeV]", ylabel="Events")
        self.th1("matchGenJetdR", jet[jet.gendr < 0.4].gendr, 40, 0, 0.4   , title = "match Gen Jet dR", xlabel="Matched GenJet dR", ylabel="Events")
        self.th1("JetResponse", matchjet.pt / matchjet.genpt, 40, 0, 2  , title = "Jet Response", xlabel="JetResponse", ylabel="Events")


        for i in range(len(self.ptrange)-1):
            lowpt = self.ptrange[i]
            highpt = self.ptrange[i+1]
            selmatch = matchjet [(matchjet.genpt > lowpt) & (matchjet.genpt < highpt) ]
            self.th1("JetResponse_pt%d_%d" % (lowpt, highpt), selmatch.pt / selmatch.genpt, 40, 0, 2  , title = "Jet Response" )
        self.eff = self.get_hist("matchGenJetPt").Clone("eff")

    def endJob(self, totalevents):
        ## Scale up rate plot
        for k, v in self.hist.items():
            if "Rate" in k :
                v.Scale((11246 * 2808.0) / (totalevents*1000.0))

        ## Jet EFFciciency
        self.eff.Divide(self.get_hist("GenJetPt"))
        self.set_hist("JetEfficiency", self.eff)

        # ## Jet Response and resolution
        means = []
        RMSs  = []

        for i in range(len(self.ptrange)-1):
            lowpt = self.ptrange[i]
            highpt = self.ptrange[i+1]
            means.append(self.get_hist("JetResponse_pt%d_%d" % (lowpt, highpt)).GetMean())
            RMSs.append(self.get_hist("JetResponse_pt%d_%d" % (lowpt, highpt)).GetStdDev())

        for i in range(len(self.ptrange)-1):
            self.response.SetBinContent(i+1, means[i])
            if means[i] != 0:
                self.resolution.SetBinContent(i+1, RMSs[i]/means[i])
            else:
                self.resolution.SetBinContent(i+1, 0)

        return True
