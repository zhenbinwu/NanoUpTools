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
sys.path.insert(1, "%s/../../" % os.path.dirname(os.path.abspath(__file__)))
# print(sys.path)

from NanoUpTools.framework import processor, module
from NanoUpTools.modules.P2L1_JetPerf import P2L1Jet

jetalgos = {
    "FJak4"       : "al4",
    # "dRE4"        : "dRE4",
    "dRE4Group"   : "dRE4Group",
    "dRE4Tile"    : "dRE4Tile",
    # "dRWTA4"      : "dRWTA4",
    "dRWTA4Group" : "dRWTA4Group",
    "dRWTA4Tile"  : "dRWTA4Title",
    # "ktWTA4"      : "ktWTA4",
    "ktWTA4Group" : "ktWTA4Group",
    "ktWTA4Tile"  : "ktWTA4Tile",
    # "ktE4"        : "ktE4",
    "ktE4Group"   : "ktE4Group",
    "ktE4Tile"    : "ktE4Tile",
}

mods = []


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description='Process some integers.')
    parser.add_argument('--inputFiles', default="./TTbarInc.txt", help='an integer for the accumulator')
    parser.add_argument('--outputFile', default="out.root")
    parser.add_argument('--jettype', default="L1PuppiJets")
    args = parser.parse_args()

    for k, v in jetalgos.items():
        mods.append(P2L1Jet(k, jetlabel=k, jetID=v+args.jettype))
    g = processor(args.outputFile, args.inputFiles, mods)
    # g = processor(args.outputFile, args.inputFiles, mods, nbatches=2 )
    g.run()
