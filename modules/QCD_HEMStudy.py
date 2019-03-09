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

        HEMJets = (jet.eta > -2.8) & (jet.eta<-1.6) & (jet.phi > -1.37) & (jet.phi<-1.07)
        PassHEMVeto = [~np.any(k) for k in HEMJets]
        BaseHEMVeto = PassHEMVeto & pas.Baseline

        cutdict = {
            "NoCut" : np.ones(BaseHEMVeto.shape, dtype=bool),
            "Baseline" : pas.Baseline,
            "BaseHEMVeto" : BaseHEMVeto,
        }

        for k, v in cutdict.items():
            self.th1("MET_" + k   , 100, 0 , 500, met.pt[v],
                     title = "MET Passing %s " % k, xlabel="MET", ylabel="Events")
            self.th1("jeteta_" + k, 100, -5, 5  , jet.eta[v], color='blue')
            # self.th1("MET_Base"    , 100 , 0  , 500  , met.pt[pas.Baseline ])
            # self.th1("MET_BaseHEM" , 100 , 0  , 500  , met.pt[PassHEMVeto and pas.Baseline])
        # self.th1("METPhi"      , 100 , -5 , 5    , met.phi[pas.Baseline])
        # self.th1("jetpt"       , 100 , 0  , 1000 , jet.pt)
        # # self.th1("jetptsel", 100, 0, 1000, jet.pt[pas.Baseline], color='blue')
        return True

