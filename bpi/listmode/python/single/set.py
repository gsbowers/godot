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

hv 				   = 0 #N/A for GODOT detectors
gain_select  = 0 
digital_gain = 4503.75

gain_record = [hv, gain_select, digital_gain]

gain = emorpho_io.set_gain(all_morpho,sn, gain_record)

gain_parameters = ["hv", "gain_select", "digitial_gain"]

print '\n',sn, " gain: "
for i in range(len(gain_parameters)):
  print gain_parameters[i].ljust(25),":",repr(gain[i]).rjust(10)


#set digitial signal processing parameters
#c.f. 6.2 in "Morpho Data Server - Reference" 

threshold	= 20
integrate	=	1
holdoff		= 1.875
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

dsp = emorpho_io.set_dsp(all_morpho,sn, dsp_record)

dsp_parameters = ["threshold", "integrate", "holdoff", "put", \
  "baseline_threshold", "pit", "nai_mode", "roi_low", "roi_high", \
  "temperature_disable", "suspend"]

print '\n',sn, " dsp: "
for i in range(len(dsp_parameters)):
  print dsp_parameters[i].ljust(25),":",repr(dsp[i]).rjust(10)


#print out instrument settings (IS array)
#c.f. 6.10 in "Morpho Data Server - Reference" 

IS = emorpho_io.get_is(all_morpho, sn)

print "\n", sn, " Instrument Settings:" 

IS_parameters = ["fine_gain", "baseline_threshold", "pulse_threshold", \
  "holdoff", "integration_time", "roi_bounds", "trigger_delay", \
  "dac_data", "pit", "put", "request", "ecomp", "pcomp", "gain_select", \
  "lm_data_swtich", "etout", "ptout", "suspend", "segment", \
  "segment_enable", "daq_mode", "nai_mod", "temperature_disable", \
  "opt_repeat_time", "opto_pulse_width", "opto_pulse_sep", \
  "opto_trigger", "opto_enable", "clear_statistics", "clear_histogram", \
  "clear_list_mode", "clear_trace", "ut_run", "program_hv", "read_nv", \
  "write_nv", "ha_run", "trace_run", "vt_run", "lm_run", "rtlt", "run", \
  "ACQ_Time", "HV"] 

for i in range(len(IS)):
  print IS_parameters[i].ljust(25),":", repr(IS[i]).ljust(10)
