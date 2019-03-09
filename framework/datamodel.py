#!/usr/bin/env python
# encoding: utf-8

# File        : datamodel.py
# Author      : Ben Wu
# Contact     : benwu@fnal.gov
# Date        : 2019 Mar 06
#
# Description :

import awkward
import uproot_methods.classes.TLorentzVector
import numpy as np
import uproot_methods
from awkward.array.table import Table

## awkward-array won't support attribute-style access of items as Pandas
## This has been discussed with Jim and understood
## https://github.com/scikit-hep/awkward-array/issues/98#issuecomment-471216078
## https://github.com/scikit-hep/awkward-array/issues/56#issuecomment-471094824
## For this light weighted tools for Nano study, we are cutting corners.
## Take the example from fnal-column-analysis-tools for attribute access of columns
## https://github.com/CoffeaTeam/fnal-column-analysis-tools/blob/master/fnal_column_analysis_tools/analysis_objects/JaggedCandidateArray.py#L400

JaggedTLorentzVectorArray = awkward.Methods.mixin(uproot_methods.classes.TLorentzVector.ArrayMethods, awkward.JaggedArray)

class NanoTLorentzVectorArray(JaggedTLorentzVectorArray):
    def __init__(self, *args, **kwargs):
        super(NanoTLorentzVectorArray, self).__init__(*args, **kwargs)

    def __getattr__(self,what):
        """
            extend get attr to allow access to columns,
            gracefully thunk down to base methods
        """
        if what in self.columns:
            return self[what]
        thewhat = getattr(super(JaggedCandidateMethods,self),what)
        if 'p4' in thewhat.columns: return self.fromjagged(thewhat)
        return thewhat


class NanoTable(Table):
    def __init__(self, columns1={}, *columns2, **columns3):
        super(NanoTable, self).__init__(columns1={}, *columns2, **columns3)

    def __getattr__(self,what):
        """
            extend get attr to allow access to columns,
            gracefully thunk down to base methods
        """
        if what in self.columns:
            return self[what]
        thewhat = getattr(super(JaggedCandidateMethods,self),what)
        return thewhat

def Object(arrays, name, selection=None):
    jaggedarray = None
    matkeys = set([k for k in arrays.keys() if k.startswith("%s_" % name)])

    if "%s_mass" % name  in matkeys:
        flatarray = uproot_methods.classes.TLorentzVector.TLorentzVectorArray.from_ptetaphim(
            arrays["%s_pt" % name].content, arrays["%s_eta" % name].content, arrays["%s_phi" % name].content, arrays["%s_mass" % name].content)
        jaggedarray = NanoTLorentzVectorArray.fromoffsets(arrays["%s_pt" % name].offsets, flatarray)
        matkeys = matkeys - {"%s_pt" % name, "%s_eta" % name, "%s_phi" % name, "%s_mass" % name}

    for k in matkeys:
        if "Stop0l_HOT" in k: ##Temp fix for v1 Post-processing
            continue
        if jaggedarray is None:
            jaggedarray = NanoTable({'_': arrays[k]})
        _, att = k.split("%s_" % name, 1)
        jaggedarray[att] =arrays[k]

    if selection is None:
        return jaggedarray
    else:
        return jaggedarray[selection]

