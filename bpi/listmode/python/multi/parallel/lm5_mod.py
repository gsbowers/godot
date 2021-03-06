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

def lm4_mod(all_morpho, sn,seconds):

  filelength = 100000
  restartpoint = 170
  maxfiletime = 120

  #assumes detector has already been booted up and configured with
  #boot_all.py and set_all.py

  overallt0 = time.time()
  totallength=0
  finishing=0

  while finishing < 1:
    lm_data_dir = "/home/vladimir/work/godot/threaded/data/"
    prefix = "%s"%sn
    suffix = time.strftime("_lm_%y%m%d_%H%M%S.csv")
    lm_data_file = lm_data_dir+prefix+suffix

    emorpho_io.start_lm(all_morpho, sn, [0,0])
    tnextstart=datetime.now()

    length=0
    lmstr=""
    first2lasttime=[0,0]
    countslasttime=0
    filet0 = time.time()
    filefinishing = 0
    
    while (length < filelength and finishing < 1 and filefinishing < 1) :

      if (time.time()-filet0 >= float(maxfiletime)):
        filefinishing=1

      if (time.time()-overallt0 >= float(seconds)):
        finishing=1

      #Gather data and check where you are in the buffer:
      lm_data = \
        emorpho_io.read(all_morpho, sn, emorpho_io.MA_LISTMODE, 2048,2)
      lm_counts = lm_data[1023] & 0x1FF # number of valid events

      #Check for zero length or identical to previous read:
      if lm_counts == 0:
        countslasttime = lm_counts
        first2lasttime=[0,0]
        continue
      first2=lm_data[0:2] #1st 2 words
      if first2 == first2lasttime and lm_counts == countslasttime:
         #nothing new; repeated frame.
         continue

      #Restart & record if halfway through buffer (restart first to avoid
      #losing time & events)
      if (lm_counts > restartpoint or finishing==1 or filefinishing==1) :
        #restart
        emorpho_io.start_lm(all_morpho, sn, [0,0])
        t0=tnextstart
        tnextstart=datetime.now()

        #record
        st='%s %s %s %s %s %s %s' %( str(t0.year), str(t0.month), str(t0.day), str(t0.hour), str(t0.minute), str(t0.second), str(t0.microsecond))
  
        d_lst = [sn, lm_counts] + lm_data[0:3*lm_counts]
        data  = ' '.join(map(str,d_lst))
        tojoin = [lmstr,st,data]
        lmstr = '\n'.join(tojoin)
        length = length + lm_counts

        countslasttime = lm_counts
        first2lasttime = first2

    print "length, filename: ", length, lm_data_file
    t1=datetime.now()
    st1='\n%s %s %s %s %s %s %s\n' %( str(t1.year), str(t1.month),  str(t1.day), str(t1.hour), str(t1.minute), str(t1.second), str(t1.microsecond))
    f=open(lm_data_file,'w')
    f.write(lmstr)
    f.write(st1)
    f.close()
    totallength = totallength + length

  print "List mode done, total length: ",totallength,"  ",totallength/seconds,"c/s"
