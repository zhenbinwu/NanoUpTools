#!/usr/bin/env python
# encoding: utf-8


# File        : test.py
# Author      : Ben Wu
# Contact     : benwu@fnal.gov
# Date        : 2019 Mar 03
#
# Description :

import os
import sys
import time
## uproot
import uproot
import awkward
import uproot.cache
import uproot_methods.classes.TLorentzVector
## rootpy
import rootpy
from rootpy.io import root_open

class processor :
    def __init__(self, outputfile, inputFiles, modules=[], nbatches=None, treename="Events", decode="utf8"):
        self.outputfile = outputfile
        self.inputFiles=inputFiles
        self.nbatches = nbatches
        with open(self.inputFiles) as filelist:
            lines = [l.strip() for l in filelist.readlines()]
        # self.cache = uproot.cache.ArrayCache(1024**3)
        # self.it = uproot.iterate(lines, treename, namedecode=decode, cache=self.cache, xrootdsource=dict(chunkbytes=80*1024, limitbytes=100*1024**2))
        self.it = uproot.iterate(lines, treename, namedecode=decode, xrootdsource=dict(chunkbytes=80*1024, limitbytes=100*1024**2))
        self.modules = modules
        ## Tracking the performance
        self.totalevents = 0
        self.startime = 0
        self.loadingtime = 0
        self.analyzingtime = 0
        self.totaltime  = 0

    def CalTimeLasted(self, totsec):
        h = int(totsec/3600)
        m = int((totsec % 3600)/60)
        s = (totsec % 3600)%60
        if h == 0:
            return "%d:%d minutes" % (m, s)
        else:
            return "%d:%d hours" % (h, m)

    def run(self):
        nbatch = 0
        self.startime = time.time()
        while True:
            try:
                t0 = time.time()
                self.events = next(self.it)
                t1 = time.time()
                nEvents = len(self.events["run"])
                self.totalevents += nEvents
                self.loadingtime += t1-t0
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ Running Modules ~~~~~
                for m in self.modules:
                    m.analyze(self.events)
                t2 = time.time()
                self.analyzingtime += t2-t1
                print("Loaded %d events for %.2f second, analyzed with %.2f kHz" % (nEvents, t1-t0, nEvents/(1000*(t2-t1))))
                nbatch += 1
                if self.nbatches is not None and nbatch == self.nbatches:
                    print("Finished run with %d batches" % nbatch)
                    self.EndRun()
                    break
            except StopIteration:
                print("End of the loop", sys.exc_info()[0])
                self.EndRun()
                break

    def EndRun(self):
        self.totaltime  = time.time() - self.startime
        print("Run over %d events with %s ( %.1f%% loading, %.1f%% analyzing )" % \
                (self.totalevents, self.CalTimeLasted(self.totaltime), self.loadingtime/self.totaltime*100,\
                 self.analyzingtime/self.totaltime*100))
        print("Saving output to %s" % self.outputfile)
        outfile = root_open(self.outputfile, "RECREATE")
        for m in self.modules:
            m.SaveHist(outfile)
