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
settings_path = '/home/vladimir/GODOT/settings/'
all_morpho = ftdi.ft245()
#find emorphos
ret_find = all_morpho.find_all(use_bpi_vid_only)
if(ret_find >= 0):
	emorpho_io.boot_all(all_morpho, settings_path)
#get serial numbers
sn_list = all_morpho.sn
if not isinstance(sn_list, list):
	sn_list = [sn_list]

dsp_parameters = ["threshold", "integrate", "holdoff", "put", \
  "baseline_threshold", "pit", "nai_mode", "roi_low", "roi_high", \
  "temperature_disable", "suspend"]

print "active devices: "
for sn in sn_list:
	print sn, " gain: ", emorpho_io.get_gain(all_morpho,sn) 
	dsp_file = "/home/vladimir/GODOT/dsp/%s%s"%(sn,time.strftime("_dsp_%y%m%d_%H%M%S.csv"))
	f=open(dsp_file,'w')
	f.write(sn+'\n')
	dsp = emorpho_io.get_dsp(all_morpho,sn)
	for i in range(len(dsp_parameters)):
		f.write("%s:%s\n"%(dsp_parameters[i].ljust(25),repr(dsp[i]).rjust(10)))
	f.close()
