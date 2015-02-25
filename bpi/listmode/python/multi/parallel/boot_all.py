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
#find emorphos
ret_find = all_morpho.find_all(use_bpi_vid_only)
if(ret_find >= 0):
	emorpho_io.boot_all(all_morpho, settings_path)
#get serial numbers
sn_list = all_morpho.sn
if not isinstance(sn_list, list):
	sn_list = [sn_list]

print "active devices: "
for sn in sn_list:
	print sn, " gain: ", emorpho_io.get_gain(all_morpho,sn)

