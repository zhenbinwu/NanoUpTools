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

class P2L1Jet(Module):
    def __init__(self, name, jetlabel = "AK4", jetID = "al4L1PuppiJets"):
        self.jetID = jetID
        self.jetlabel = jetlabel
        Module.__init__(self, name)
        self.ptrange = [0, 20, 50, 100, 300, 600]
        pass

    def analyze(self, events):
        gen = Object(events, "GenJets")
        jet = Object(events, self.jetID)
        if jet is None:
            print(self.jetID, self.jetlabel)
        matchjet = jet[jet.gendr < 0.4]

        self.resolution= self.th1("PerfResolution", 200, 0, 600, None)
        self.response= self.th1("PerfResponse", 200, 0, 600, None)
        self.th1("nGenJet", 20, 0, 20   , gen.counts, title = "Gen Jet counts" )
        self.th1("GenJetPt", 200, 0, 600   , gen.pt, title = "Gen Jet pt" )
        self.th1("nRecoJet", 20, 0, 20   , jet.counts, title = "Reco Jet counts")
        self.th1("matchGenJetPt", 200, 0, 600   , jet[jet.gendr < 0.4].genpt,
                 title = "match Gen Jet pt" )
        self.th1("matchGenJetdR", 40, 0, 0.4   , jet[jet.gendr < 0.4].gendr,
                 title = "match Gen Jet pt" )
        self.th1("JetResponse", 40, 0, 2  , matchjet.pt / matchjet.genpt,
                 title = "Jet Response" ) 



        for i in range(len(self.ptrange)-1):
            lowpt = self.ptrange[i]
            highpt = self.ptrange[i+1]
            selmatch = matchjet [(matchjet.genpt > lowpt) & (matchjet.genpt < highpt) ]
            self.th1("JetResponse_pt%d_%d" % (lowpt, highpt), 40, 0, 2  ,
                     selmatch.pt / selmatch.genpt, title = "Jet Response" ) 

    def endJob(self):
        ## Jet EFFciciency
        eff = self.getth1("matchGenJetPt").Clone("eff")
        eff.Divide(self.getth1("GenJetPt"))
        self.setth1("JetEfficiency", eff)
        # self.rebinth1("JetEfficiency", self.ptrange)

        # ## Jet Response and resolution
        # means = []
        # RMSs  = []

        # for i in range(len(self.ptrange)-1):
            # lowpt = self.ptrange[i]
            # highpt = self.ptrange[i+1]
            # means.append(self.getth1("JetResponse_pt%d_%d" % (lowpt, highpt)).GetMean())
            # RMSs.append(self.getth1("JetResponse_pt%d_%d" % (lowpt, highpt)).GetStdDev())

        # response = self.response.rebinned(self.ptrange)
        # resolution = self.resolution.rebinned(self.ptrange)
        # for i in range(len(self.ptrange)-1):
            # response.SetBinContent(i+1, means[i])
            # resolution.SetBinContent(i+1, RMSs[i]/means[i])
        # self.setth1("PerfResponse",response)
        # self.setth1("PerfResolution",resolution)

        return True

