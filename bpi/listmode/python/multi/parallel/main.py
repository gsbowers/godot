#!/usr/bin/python

import thread
from lm7 import lm7
from lm7_newfirm import lm7_newfirm

execfile('boot_all.py')
execfile('set_all.py')

timeunit = input('Time in seconds (0) or hours (1)? ')
timeunit = int(timeunit)
if timeunit == 0:
    seconds = input('Enter seconds for accumulation: ')
    seconds = float(seconds)
if timeunit == 1:
    hours = input('Enter hours for accumulation: ')
    seconds = float(hours)*3600.

for sn in sn_list:

  if sn == 'eRC1386':
    try:
      thread.start_new_thread( lm7, (all_morpho, sn, seconds)) 
    except:
      print "Errror ", sn, ": unable to launch thread"
  else:
    try:
      thread.start_new_thread( lm7_newfirm, (all_morpho, sn, seconds)) 
    except:
      print "Errror ", sn, ": unable to launch thread"
