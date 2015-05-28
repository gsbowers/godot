#!/usr/bin/python

import thread
import threading
import time
from lm4_mod3 import lm4_mod3
from lm4_mod2_newfirm import lm4_mod2_newfirm
from lm4_mod3_newfirm import lm4_mod3_newfirm

execfile('/home/vladimir/GODOT/boot_all.py')
#execfile('set_all.py')

#timeunit = input('Time in seconds (0) or hours (1)? ')
#timeunit = int(timeunit)
#if timeunit == 0:
#    seconds = input('Enter seconds for accumulation: ')
#    seconds = float(seconds)
#if timeunit == 1:
#    hours = input('Enter hours for accumulation: ')
#    seconds = float(hours)*3600.

#run for ~1 year
seconds = 3e7

for sn in sn_list:

  if sn == 'eRC1386':
    try:
      thread.start_new_thread( lm4_mod3, (all_morpho, sn, seconds)) 
    except:
      print "Errror ", sn, ": unable to launch thread"
  elif sn == 'eRC1488':
    try:
      thread.start_new_thread( lm4_mod3_newfirm, (all_morpho, sn, seconds)) 
    except:
      print "Errror ", sn, ": unable to launch thread"
  else:
    try:
      thread.start_new_thread( lm4_mod2_newfirm, (all_morpho, sn, seconds)) 
    except:
      print "Errror ", sn, ": unable to launch thread"

#keep main alive otherwise launched threads die
time.sleep(seconds)
