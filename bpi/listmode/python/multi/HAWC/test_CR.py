#!/usr/bin/python
#
# version 1.0
from __future__ import division
import zmq
import time
import sys
import emorpho_io
import ftdi
import xml.dom.minidom
import array
from datetime import datetime
import string
import numpy
from emorpho_io import *

filelength=100000
restartpoint = 0.5*5461
maxfiletime = 10000


#if sn == 'eRC1488':
# restartpoint = 200

execfile('/home/vladimir/GODOT/boot_all.py')

sn = 'eRC1488'

#print "running lm8_newfirm.py"
#print "restartpoint: ", restartpoint
#print "maxfiletime: ", maxfiletime
#print time.strftime("%Y-%m-%d/%H:%M:%S", time.localtime())

#assumes detector has already been booted up and configured with
#setplastic_api.py or setnai_api.py
if sn == 'eRC1488':
 max_buffer_frac = 500/5461.0
 maxfiletime = 50
if sn == 'eRC1489':
 max_buffer_frac = 0.35
 maxfiletime = 900
if sn == 'eRC1490':
 max_buffer_frac = 0.65
 maxfiletime = 900
if sn == 'eRC1491':
 max_buffer_frac = 0.50
 maxfiletime = 900

restartpoint = 5461*max_buffer_frac

overallt0 = time.time()
totallength=0
finishing=0

#reset statistics
#emorpho_io.start_lm(all_morpho, sn, [0,1])

adc_sr = get_sr(all_morpho, sn)
CR = read(all_morpho, sn, MA_CONTROLS, 32, 2)
print CR
IS = cr2is(CR, adc_sr)
set_IS(IS, 'ACQ_Time', 0.05)
set_IS(IS, 'rtlt', 1)
set_IS(IS, 'lm_run', 1)
set_IS(IS, 'run', 1)
set_IS(IS, 'ha_run', 1)
apply_settings(all_morpho, sn, IS)
print 'IS: ', IS

emorpho_io.start_lm(all_morpho, sn, [0,1])


while 1:
  time.sleep(2.11)
  is_val = get_is(all_morpho, sn)
  cr = read(all_morpho, sn, MA_CONTROLS, 32, 2)
  print cr
  
