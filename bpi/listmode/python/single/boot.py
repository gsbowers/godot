#!/usr/bin/python
#
# version 1.0
from __future__ import division
import zmq
import time
import sys
import xml.dom.minidom
import array
from datetime import datetime
import string
import emorpho_io
import ftdi

#Find and connect to eMorpho:
use_bpi_vid_only = 1 # only recognize devices with te BPI vendor id 
settings_path = 'settings/'
all_morpho = ftdi.ft245()

#print "all_morpho: ",all_morpho
ret_find = all_morpho.find_all(use_bpi_vid_only)
#print "ret_find: ",ret_find
if(ret_find >= 0):
	emorpho_io.boot_all(all_morpho, settings_path)
sn = all_morpho.sn[1] # use the first device only
#sn = 'eRC1386'
sn = 'eRC1488'

#clear statistics
#IS = emorpho_io.get_IS(all_morpho, sn)
#emorpho_io.set_IS(IS, 'clear_statistics', 1)
#emorpho_io.apply_settings(all_morpho, sn, IS)

print "active device: ", sn
#print emorpho_io.get_gain(all_morpho,sn)

