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
from rootpy.plotting import Hist, Profile

class processor :
    def __init__(self, outputfile, inputFiles, modules=[], nbatches=None, treename="Events", decode="utf8"):
        self.outputfile = outputfile
        self.inputFiles = inputFiles
        self.nbatches   = nbatches
        self.modules    = modules
        self.decode     = decode
        ## Tracking the process information
        self.isData = False
        self.isFastsim = False
        self.CrossSection = 0
        self.Lumi = 0
        self.ExpectedNEvent = 0
        ## Tracking the global histogram
        self.BookGlobalHist()
        ## Tracking the reading
        self.FirstEvent=True
        self.curfilename = None
        self.curTFile = None
        ## Tracking the performance
        self.totalevents = 0
        self.startime = 0
        self.loadingtime = 0
        self.analyzingtime = 0
        self.totaltime  = 0

        ## Iterate the file
        print("Hello! Start to read files...")
        if self.inputFiles.endswith(".root"):
            lines=[self.inputFiles]
        else:
            with open(self.inputFiles) as filelist:
                lines = [l.strip() for l in filelist.readlines()]
        # self.cache = uproot.cache.ArrayCache(1024**3)
        self.it = uproot.iterate(lines, treename, namedecode=decode, reportpath=True, reportfile=True, reportentries=True,
                                 xrootdsource=dict(chunkbytes=80*1024, limitbytes=100*1024**2))

    def BookGlobalHist(self):
        self.hEvents = Hist(4, 0, 4, name = "NEvent", title="Number of Events")
        InfoLabels = ["isData", "isFastsim", "Lumi", "CrossSection", "GeneratedNEvent"]
        self.hInfo = Profile(len(InfoLabels), 0, len(InfoLabels), name="Info", title="Information of the process")
        [ self.hInfo.GetXaxis().SetBinLabel(i+1, n) for i, n in enumerate(InfoLabels) ]

    def FillNEvent(self, events):
        if "genWeight" not in events:
            return False
        genW = events["genWeight"]
        posW = genW[genW > 0].sum()
        negW = len(genW) - posW
        self.hEvents.Fill(2, posW )
        self.hEvents.Fill(3, negW)
        self.hEvents.Fill(4, posW - negW )

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
                curfilename, self.curTFile, start, end, self.events = next(self.it)
                t1 = time.time()
                nEvents = end -start
                self.totalevents = end
                self.loadingtime += t1-t0
                self.GetFileInformation()
                self.FillNEvent(self.events)
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
        for m in self.modules:
            m.endJob()
        outfile = root_open(self.outputfile, "RECREATE")
        outfile.cd()
        self.hEvents.Fill(0, self.totalevents)
        self.hEvents.Write()
        self.hInfo.Fill(2, self.Lumi)
        self.hInfo.Fill(3, self.CrossSection)
        self.hInfo.Fill(4, self.ExpectedNEvent)
        self.hInfo.Write()

        for m in self.modules:
            m.SaveHist(outfile)

    def GetFileInformation(self):
        if not self.FirstEvent:
            return False
        self.FirstEvent = False

        Eventbranch = self.curTFile.get("Events")
        if "Stop0l_evtWeight" in Eventbranch:
            import re
            infostr = Eventbranch.get("Stop0l_evtWeight").title.decode(self.decode)
            mat =re.match(".*\(Lumi=([0-9]*[.]?[0-9]+)\)", infostr)
            if mat is not None:
                self.Lumi = float(mat.group(1))
                return True
            mat =re.match(".*\(CrossSection=([0-9]*[.]?[0-9]+),\s+nEvent=([0-9]*[.]?[0-9]+)\)", infostr)
            if mat is not None:
                self.CrossSection = float(mat.group(1))
                self.ExpectedNEvent = float(mat.group(1))
                return True
        return False

