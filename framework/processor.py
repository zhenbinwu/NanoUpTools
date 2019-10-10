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
    def __init__(self, outputfile, inputFiles, modules=[], branches=None, entrysteps=None, nbatches=None, treename="Events", decode="utf8"):
        self.outputfile     = outputfile
        self.inputFiles     = inputFiles
        self.nbatches       = nbatches
        self.modules        = modules
        self.decode         = decode
        ## Tracking the process information
        self.isData         = False
        self.isFastsim      = False
        self.isSUSY         = False
        self.Lumi           = 0
        self.CrossSection   = 0
        self.ExpectedNEvent = 0
        self.era            = 0
        self.process        = None
        self.period         = None
        self.process_full   = None
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
        # self.cache = uproot.cache.ArrayCache(200 *1024**2)
        self.it = uproot.iterate(lines, treename, branches=branches,
                                 # cache=self.cache,  
                                 namedecode=decode,
                                 entrysteps=entrysteps, reportpath=True,
                                 reportfile=True, reportentries=True,
                                 xrootdsource=dict(chunkbytes=80*1024, limitbytes=10*1024**2))

    def BookGlobalHist(self):
        self.hEvents = Hist(5, 0, 5, name = "NEvent", title="Number of Events")
        InfoLabels = ["isData", "isFastsim", "Lumi", "CrossSection", "GeneratedNEvent", "era"]
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
                if self.FirstEvent:
                    self.GetFileInformation()
                    for m in self.modules:
                        m.ObtainInfo(self.isData, self.isFastsim, self.isSUSY, self.Lumi, self.CrossSection, self.era, self.process, self.period)
                    self.FirstEvent = False
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
            m.endJob(self.totalevents)
        outfile = root_open(self.outputfile, "RECREATE")
        outfile.cd()
        self.hEvents.Fill(0, self.totalevents)
        self.hEvents.Write()
        if self.process_full is not None:
            self.hInfo.SetTitle(self.process_full) 
        self.hInfo.Fill(0, self.isData)
        self.hInfo.Fill(1, self.isFastsim)
        self.hInfo.Fill(2, self.Lumi)
        self.hInfo.Fill(3, self.CrossSection)
        self.hInfo.Fill(4, self.ExpectedNEvent)
        self.hInfo.Fill(5, self.era)
        self.hInfo.Write()

        for m in self.modules:
            m.SaveHist(outfile)
        outfile.close()

    def GetFileInformation(self):

        Eventbranch = self.curTFile.get("Events")
        if "Stop0l_evtWeight" in Eventbranch:
            import re
            infostr = Eventbranch.get("Stop0l_evtWeight").title.decode(self.decode)
            mat =re.match(".*\(Lumi=([0-9]*[.]?[0-9]+)\)", infostr)
            if mat is not None:
                self.Lumi = float(mat.group(1))
            mat =re.match(".*\(CrossSection=([0-9]*[.]?[0-9]+),\s+nEvent=([0-9]*[.]?[0-9]+)\)", infostr)
            if mat is not None:
                self.CrossSection = float(mat.group(1))
                self.ExpectedNEvent = float(mat.group(2))
            mat =re.match(".*for(.*)\(.*\)", infostr)
            if mat is not None:
                self.process_full = mat.groups()[0].strip()
                mat2 = re.match("(.*)_(2016|2017|2018)(_Period(\w))?", self.process_full)
                if mat2 is not None:
                    self.process, self.era, _, self.period = mat2.groups()

        if self.era is not None:
            self.era = int(self.era)
        if self.process is not None:
            if "Data" in self.process:
                self.isData = True
            if "fastsim" in self.process:
                self.isFastsim = True
            if "SMS" in self.process:
                self.isSUSY = True
        ## Temp fix for v2p6 pro
        if self.process is None:
            self.isData = True
        return False

