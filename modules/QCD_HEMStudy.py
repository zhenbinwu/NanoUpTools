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
sys.path.insert(1, "%s/.." % os.path.dirname(os.path.abspath(__file__)))

from framework.module import Module
from framework.datamodel import Object

class QCDHEMVeto(Module):
    def __init__(self, name):
        Module.__init__(self, name)
        pass

    def analyze(self, events):
        # stop = Object(events, "Stop0l")

        ## ISSUE: Not form from p4, doesn't work for now
        ## Attribute lost from passing the argument
        # pas = Object(events, "Pass")

        jet = Object(events, "Jet")
        ## ISSUE: TypeError: jagged index must be boolean (ask) or integer (ancy indexing)
        ## print(jet[jet.pt> 100])
        ## print(jet[jet.pt.min() > 100]) Working fine.

        self.th1("jetpt", 100, 0, 1000, jet.pt)
        self.th1("jetptsel", 100, 0, 1000, jet.pt[jet.pt.min() > 100], color='black')
        return True

