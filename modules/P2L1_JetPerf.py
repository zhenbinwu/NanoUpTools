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

    def analyze(self, events):
        gen = Object(events, "GenJets")
        fj = Object(events, "al4L1"+self.jetID.split("L1")[-1])
        jet = Object(events, self.jetID)

        x = jet.cross(gen)
        matched = x.i0.delta_r(x.i1) < 0.4
        response = x[matched].i0.pt / x[matched].i1.pt
        self.th1("localJetResponse", response, 40, 0, 2, title = "Jet Response",
                 xlabel="JetResponse", ylabel="Events", color=self.color)

        if jet is None:
            print(self.jetID, self.jetlabel)
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
        self.th1("RecoJetPt", jet.pt, self.ptrange , title = "Reco Jet pt", xlabel="RecoJet p_{T} [GeV]", ylabel="Events")
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

    def endJob(self):
        ## Jet EFFciciency
        eff = self.get_hist("matchGenJetPt").Clone("eff")
        eff.Divide(self.gethist("GenJetPt"))
        self.set_hist("JetEfficiency", eff)

        # ## Jet Response and resolution
        means = []
        RMSs  = []

        for i in range(len(self.ptrange)-1):
            lowpt = self.ptrange[i]
            highpt = self.ptrange[i+1]
            means.append(self.gethist("JetResponse_pt%d_%d" % (lowpt, highpt)).GetMean())
            RMSs.append(self.gethist("JetResponse_pt%d_%d" % (lowpt, highpt)).GetStdDev())

        for i in range(len(self.ptrange)-1):
            self.response.SetBinContent(i+1, means[i])
            self.resolution.SetBinContent(i+1, RMSs[i]/means[i])

        return True

