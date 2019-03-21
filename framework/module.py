#!/usr/bin/env python
# encoding: utf-8

# File        : module.py
# Author      : Ben Wu
# Contact     : benwu@fnal.gov
# Date        : 2019 Mar 06
#
# Description :

import numpy as np
## rootpy
import rootpy
from rootpy.plotting import Hist

from collections import OrderedDict
import uproot
import awkward
import uproot_methods.classes.TLorentzVector

class Module():
    def __init__(self, folder):
        self.folderName = folder
        self.hist = OrderedDict()

    def th1(self, name):
        return self.hist[ self.folderName+"_"+name]

    def th1(self, name_, xbins, xlow, xhigh, values, title="", xlabel="", ylabel="", \
            color=None, linecolor=None, markercolor=None, fillcolor=None,
            linewidth=None, linestyle=None, markersize=None, markerstyle=None, fillstyle=None):
        ## Create an unique name to prevent memory leak in ROOT
        name = self.folderName+"_"+name_
        if name not in self.hist.keys():
            newtitle = title+";"+xlabel+";"+ylabel
            self.hist[name] = Hist(xbins, xlow, xhigh, name =name, title =newtitle)
        if isinstance(values, awkward.JaggedArray):
            self.hist[name].fill_array(values.flatten())
        elif isinstance(values, np.ndarray):
            self.hist[name].fill_array(values)
        else:
            self.hist[name].Fill(values)
        ## Setup the plotting, since TH1 inherited from TAttLine, TAttFill, TAttMarkerS
        if color is not None:
            self.hist[name].SetLineColor(color)
            self.hist[name].SetMarkerColor(color)
            self.hist[name].SetFillColor(color)
        ## Set line
        if linecolor is not None:
            self.hist[name].SetLineColor(linecolor)
        if linewidth is not None:
            self.hist[name].SetLineWidth(linewidth)
        if linestyle is not None:
            self.hist[name].SetLineStyle(linestyle)
        ## Set Marker
        if markercolor is not None:
            self.hist[name].SetMarkerColor(markercolor)
        if markersize is not None:
            self.hist[name].SetMarkerSize(markersize)
        if markerstyle is not None:
            self.hist[name].SetMarkerStyle(markerstyle)
        ## Set fill
        if fillcolor is not None:
            self.hist[name].SetFillColor(fillcolor)
        if fillstyle is not None:
            self.hist[name].SetFillStyle(fillstyle)

    def analyze():
        return True

    def SaveHist(self, outfile):
        outfile.cd()
        outfile.mkdir(self.folderName)
        outfile.cd(self.folderName)
        for k, v in self.hist.items():
            orgname = k.split("_", 1)[1]
            v.SetName(orgname)
            v.Write()


