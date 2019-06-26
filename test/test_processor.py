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

from NanoUpTools.framework import processor, module
from NanoUpTools.modules.QCD_HEMStudy import QCDHEMVeto
from NanoUpTools.modules.Stop_TTZ import StopTTZ

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description='Process some integers.')
    parser.add_argument('-i', '--inputFiles', default="./TTbarInc.txt", help='an integer for the accumulator')
    parser.add_argument('-o', '--outputFile', default="out.root")
    args = parser.parse_args()

    mods = [
        QCDHEMVeto("Stop"),
        # StopTTZ("TTZ")
    ]

    g = processor(args.outputFile, args.inputFiles, mods, entrysteps="100 MB",
                  nbatches=2
                 )
    g.run()
