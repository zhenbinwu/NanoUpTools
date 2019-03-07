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

def Object(arrays, name, selection=None):
    jaggedarray = None
    newjagger = False
    if "%s_pt" % name  in arrays.keys():
        flatarray = uproot_methods.classes.TLorentzVector.TLorentzVectorArray.from_ptetaphim(
            arrays["%s_pt" % name].content, arrays["%s_eta" % name].content, arrays["%s_phi" % name].content, arrays["%s_mass" % name].content)
        jaggedarray = awkward.Methods.mixin(uproot_methods.classes.TLorentzVector.ArrayMethods, awkward.JaggedArray).fromoffsets(
            arrays["%s_pt" % name].offsets, flatarray)
    for k in arrays.keys():
        if not k.startswith(name):
            continue
        if k == "%s_pt" % name or  k == "%s_eta" % name or  k == "%s_phi" % name or  k == "%s_mass" % name :
            continue
        if jaggedarray is None:
            ##ISSUE: This doesn't work as the p4 one above
            ##Attribute will be lost after passing
            jaggedarray = awkward.JaggedArray.fromiter([arrays[k]])
            ## Keep it to arrays in memory?
            newjagger = True
        _, att = k.split("%s_" % name, 1)
        setattr(jaggedarray, att, arrays[k])
    if newjagger: ## Doesn't work
        arrays[name+"__"] = jaggedarray
        jaggedarray=arrays[name+"__"]
    if selection is not None:
        return jaggedarray
    else:
        return jaggedarray[selection]


