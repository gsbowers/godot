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

#set electronic and digitial gain parameters
#c.f. 6.1 in "Morpho Data Server - Refernce"

hv 				= 99 #N/A for GODOT detectors
gain_select = 0 
digital_gain = 512

gain_record = [hv, gain_select, digital_gain]

for sn in sn_list:
	gain = emorpho_io.set_gain(all_morpho,sn, gain_record)
	print sn, " gain: ", gain


#set digitial signal processing parameters
#c.f. 6.2 in "Morpho Data Server - Reference" 

threshold	= 40	
integrate	=	0.4
holdoff		= 0.6
put 			= 0
baseline_threshold = 5
pit				= 1
nai_mode 	= 0
roi_low		= 0
roi_high  = 4080
temperature_disable = 0 
suspend		= 0

dsp_record = [threshold, integrate, holdoff, put, baseline_threshold, pit,
	nai_mode, roi_low, roi_high, temperature_disable, suspend]

for sn in sn_list:
	dsp = emorpho_io.set_dsp(all_morpho,sn, dsp_record)
	print sn, " dsp: ", dsp

