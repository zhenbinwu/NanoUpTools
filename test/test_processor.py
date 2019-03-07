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
sys.path.insert(1, "%s/.." % os.path.dirname(os.path.abspath(__file__)))

from framework import processor, module
from modules.QCD_HEMStudy import QCDHEMVeto

g = processor("out.root", "./TTbarInc.txt", [QCDHEMVeto("Testing")], nbatches=3)
g.run()
