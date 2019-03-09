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

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description='Process some integers.')
    parser.add_argument('--inputFiles', default="./TTbarInc.txt", help='an integer for the accumulator')
    parser.add_argument('--outputFile', default="out.root")
    args = parser.parse_args()

    g = processor(args.outputFile, args.inputFiles, [QCDHEMVeto("Testing")])
    g.run()
