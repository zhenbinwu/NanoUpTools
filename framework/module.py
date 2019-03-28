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
from rootpy.plotting import Hist, Hist2D

from collections import OrderedDict
import uproot
import awkward

class Module():
    def __init__(self, folder):
        self.folderName = folder
        self.hist = OrderedDict()
        self.color=None
        self.linecolor=None
        self.markercolor=None
        self.fillcolor=None
        self.linewidth=None
        self.linestyle=None
        self.markersize=None
        self.markerstyle=None
        self.fillstyle=None

    def get_hist(self, name):
        return self.hist[ self.folderName+"_"+name]

    def set_hist(self, name, th1):
        self.hist[ self.folderName+"_"+name] = th1


    def setHistStyle(self, name_, color_=None, linecolor_=None, markercolor_=None,
                     fillcolor_=None, linewidth_=None, linestyle_=None, markersize_=None,
                     markerstyle_=None, fillstyle_=None):
        name = self.folderName+"_"+name_
        if name not in self.hist:
            print("Histogram is not defined yet! Not setting style for %s, exitting!" % name_)
        ## Setup the plotting, since TH1 inherited from TAttLine, TAttFill, TAttMarkerS
        color = color_ if color_ is not None else self.color if self.color is not None else None
        if color is not None:
            self.hist[name].SetLineColor(color)
            self.hist[name].SetMarkerColor(color)
            self.hist[name].SetFillColor(color)
        ## Set line
        linecolor = linecolor_ if linecolor_ is not None else self.linecolor if self.linecolor is not None else None
        if linecolor is not None:
            self.hist[name].SetLineColor(linecolor)
        linewidth = linewidth_ if linewidth_ is not None else self.linewidth if self.linewidth is not None else None
        if linewidth is not None:
            self.hist[name].SetLineWidth(linewidth)
        linestyle = linestyle_ if linestyle_ is not None else self.linestyle if self.linestyle is not None else None
        if linestyle is not None:
            self.hist[name].SetLineStyle(linestyle)
        ## Set Marker
        markercolor = markercolor_ if markercolor_ is not None else self.markercolor if self.markercolor is not None else None
        if markercolor is not None:
            self.hist[name].SetMarkerColor(markercolor)
        markersize = markersize_ if markersize_ is not None else self.markersize if self.markersize is not None else None
        if markersize is not None:
            self.hist[name].SetMarkerSize(markersize)
        markerstyle = markerstyle_ if markerstyle_ is not None else self.markerstyle if self.markerstyle is not None else None
        if markerstyle is not None:
            self.hist[name].SetMarkerStyle(markerstyle)
        ## Set fill
        fillcolor = fillcolor_ if fillcolor_ is not None else self.fillcolor if self.fillcolor is not None else None
        if fillcolor is not None:
            self.hist[name].SetFillColor(fillcolor)
        fillstyle = fillstyle_ if fillstyle_ is not None else self.fillstyle if self.fillstyle is not None else None
        if fillstyle is not None:
            self.hist[name].SetFillStyle(fillstyle)

    def th2(self, name_, xvalues, yvalues, bins, title="", xlabel="", ylabel="", \
            color=None, linecolor=None, markercolor=None, fillcolor=None,
            linewidth=None, linestyle=None, markersize=None, markerstyle=None, fillstyle=None):
        '''
            template type of function for TH2D, including all the overloaded
            construction function
        '''
        ## Create an unique name to prevent memory leak in ROOT
        name = self.folderName+"_"+name_
        if name not in self.hist.keys():
            newtitle = title+";"+xlabel+";"+ylabel
            self.hist[name] = Hist2D(*bins, name =name, title =newtitle)
            self.setHistStyle(name_, color, linecolor, markercolor, fillcolor, linewidth, linestyle, markersize, markerstyle, fillstyle)

        #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ Fill Th2 ~~~~~
        x = None
        y = None
        if xvalues is None:
            pass
        elif isinstance(xvalues, awkward.JaggedArray):
            x = xvalues.flatten()
        elif isinstance(xvalues, np.ndarray):
            x = xvalues
        else:
            x = [xvalues]

        if yvalues is None:
            pass
        elif isinstance(yvalues, awkward.JaggedArray):
            y = yvalues.flatten()
        elif isinstance(yvalues, np.ndarray):
            y = yvalues
        else:
            y = [yvalues]
        self.hist[name].fill_array( np.vstack((x, y)).T)

        return self.hist[name]

    def th1(self, name_, values, xbins=None, xlow=0, xhigh=0, title="", xlabel="", ylabel="", \
            trigRate = False, color=None, linecolor=None, markercolor=None, fillcolor=None,
            linewidth=None, linestyle=None, markersize=None, markerstyle=None, fillstyle=None):
        ## Create an unique name to prevent memory leak in ROOT
        name = self.folderName+"_"+name_
        if name not in self.hist:
            newtitle = title+";"+xlabel+";"+ylabel
            if isinstance(xbins, (list, np.ndarray)):
                self.hist[name] = Hist(xbins, name =name, title =newtitle)
            else:
                self.hist[name] = Hist(xbins, xlow, xhigh, name =name, title =newtitle)
            self.setHistStyle(name_, color, linecolor, markercolor, fillcolor, linewidth, linestyle, markersize, markerstyle, fillstyle)

        #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ Filling ~~~~~
        if values is None:
            return self.hist[name]

        localvalue = None
        if isinstance(values, awkward.JaggedArray):
            localvalue = values.flatten()
        elif not isinstance(values, (list, np.ndarray)):
            localvalue = [values]
        else:
            localvalue = values

        if trigRate:
            bins = np.fromiter(self.hist[name].xedges(), float)
            upperidx = np.searchsorted(bins, localvalue)
            self.hist[name].fill_array(np.concatenate([bins[:x] for x in upperidx]))
        else:
            self.hist[name].fill_array(localvalue)

        return self.hist[name]

    def analyze():
        return True

    def endJob(self, totalevents):
        return True

    def SaveHist(self, outfile):
        outfile.cd()
        outfile.mkdir(self.folderName)
        outfile.cd(self.folderName)
        for k, v in self.hist.items():
            orgname = k.split("_", 1)[1]
            v.SetName(orgname)
            v.Write()


