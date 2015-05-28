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

filelength=100000
restartpoint = 0.5*5461
maxfiletime = 10000

def lm8_newfirm(all_morpho, sn, seconds):

 #if sn == 'eRC1488':
 # restartpoint = 200

 #print "running lm8_newfirm.py"
 #print "restartpoint: ", restartpoint
 #print "maxfiletime: ", maxfiletime
 #print time.strftime("%Y-%m-%d/%H:%M:%S", time.localtime())
 
 #assumes detector has already been booted up and configured with
 #setplastic_api.py or setnai_api.py
 if sn == 'eRC1488':
  max_buffer_frac = 2500/5461.0
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

 #reset statistics and counter
 emorpho_io.start_lm(all_morpho, sn, [0,1])
 
 while finishing < 1:
   lm_data_file = "/home/vladimir/GODOT/data/%s%s.csv"%(sn,time.strftime("_lm8_newfirm_%y%m%d_%H%M%S"))
 
   #From lm3 we replaced "clear_statistics" with 0 instead of 1
   #polling (don't reset statistics)
   emorpho_io.start_lm(all_morpho, sn, [0,0])
   tnextstart=datetime.now()

   #get current state of buffer
   lm_data = emorpho_io.read(all_morpho, sn, emorpho_io.MA_LISTMODE, 32768,2)
   lm_counts = lm_data[0] 
   first3lasttime=lm_data[1:4]
   countslasttime=lm_counts
 
   length=0
   lmstr=""
   filet0 = time.time()
   filefinishing = 0
 
   while (length < filelength and finishing < 1 and filefinishing < 1) :
 
     if (time.time()-filet0 >= float(maxfiletime)):
       filefinishing=1
 
     if (time.time()-overallt0 >= float(seconds)):
       finishing=1
 
     #Gather data and check where you are in the buffer:
     #larger list mode can store 5461 48 bit events. Each event is 
     #16 bit energy, 32 bit timestamp, so buffer is 32766 bytes = 
     #2^15 - 2 
     lm_data = emorpho_io.read(all_morpho, sn, emorpho_io.MA_LISTMODE, 32768,2)
     lm_counts = lm_data[0] 
 
     #Check for zero length or identical to previous read:
     if lm_counts == 0:
       countslasttime = lm_counts
       first3lasttime=[0,0,0]
       continue
     first3=lm_data[1:4] #get words in first event
     #if first3 == first3lasttime and lm_counts == countslasttime:
     if first3 == first3lasttime and lm_counts == countslasttime and filefinishing < 1 and finishing < 1:
       #nothing new; repeated frame.
       continue
 
     #Restart and record if halfway through buffer (restart comes first to avoid
     #losing time & events)
     if (lm_counts > restartpoint or finishing==1 or filefinishing==1) :
       emorpho_io.start_lm(all_morpho, sn, [0,1])
       t0=tnextstart
       tnextstart=datetime.now()
 
       st='%s %s %s %s %s %s %s' %(str(t0.year),str(t0.month),str(t0.day),str(t0.hour),str(t0.minute),str(t0.second),str(t0.microsecond))
 
       d_lst = [sn, lm_counts] + lm_data[1:3*lm_counts+1] 
       data = ' '.join(map(str,d_lst))
       #print first3
       #print first3lasttime
       #print lm_counts
       #print countslasttime
       #print 'data=', data
       if first3 == first3lasttime and lm_counts == countslasttime:
        data = '*'
       tojoin = [lmstr,st,data]
       lmstr = '\n'.join(tojoin)
       length = length + lm_counts
 
       countslasttime = lm_counts
       first3lasttime = first3
 
   #print "length, filename: ", length, lm_data_file
   t1=datetime.now()
   st1='\n%s %s %s %s %s %s %s\n' %(str(t1.year),str(t1.month),str(t1.day),str(t1.hour),str(t1.minute),str(t1.second),str(t1.microsecond))
   f=open(lm_data_file,'w')
   f.write(lmstr)
   f.write(st1)
   f.close()
   totallength = totallength + length
 
 print time.strftime("%Y-%m-%d/%H:%M:%S", time.localtime())
 print "%s List mode done, total length: ",sn, totallength," ",totallength/seconds,"c/s"
