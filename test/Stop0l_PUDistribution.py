#!/usr/bin/env python 
# encoding: utf-8

# File        : test_processor.py
# Author      : Ben Wu
# Contact     : benwu@fnal.gov
# Date        : 2019 Mar 06
#
# Description :

import sys
import os
sys.path.insert(1, "%s/../.." % os.path.dirname(os.path.abspath(__file__)))

from NanoUpTools.framework import processor
from NanoUpTools.framework.module import Module
from NanoUpTools.modules.QCD_HEMStudy import QCDHEMVeto


class temp(Module):
    def analyze(self, events):
        self.th1("pu_mc"      , events["Pileup_nTrueInt"] , 100 , 0 , 100)

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description='Process some integers.')
    parser.add_argument('--inputFiles', default="./TTbarInc.txt", help='an integer for the accumulator')
    parser.add_argument('--outputFile', default="out.root")
    args = parser.parse_args()

    g = processor(args.outputFile, args.inputFiles, [temp("temp")], branches=["Pileup_nTrueInt"])
    g.run()
