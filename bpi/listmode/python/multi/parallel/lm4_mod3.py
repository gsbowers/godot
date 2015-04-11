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
restartpoint = 25
maxfiletime = 900
maxbuffertime = 50

def lm4_mod3(all_morpho, sn, seconds):

  #assumes detector has already been booted up and configured with
  #setplastic_api.py or setnai_api.py
  
  #timeunit = input('Time in seconds (0) or hours (1)? ')
  #timeunit = int(timeunit)
  #if timeunit == 0:
  #    seconds = input('Enter seconds for accumulation: ')
  #    seconds = float(seconds)
  #if timeunit == 1:
  #    hours = input('Enter hours for accumulation: ')
  #    seconds = float(hours)*3600.

  overallt0 = time.time()
  totallength=0
  finishing=0

  #open file to record intial system times around buffer restart
  t0=datetime.now()
  st0='%s %s %s %s %s %s %s\n' %(str(t0.year),str(t0.month),str(t0.day),str(t0.hour),str(t0.minute),str(t0.second),str(t0.microsecond))
  t0file = "/home/vladimir/GODOT/t0/%s%s"%(sn,time.strftime("_lm4_mod3_t0_%y%m%d_%H%M%S.csv"))
  f=open(t0file,'w')

  #record system time before emorpho restart
  tb=datetime.now()
  #reset event counter and time
  emorpho_io.start_lm(all_morpho, sn, [0,1])
  #record system time after emorpho restart
  ta=datetime.now()

	#write timing information to file
  stb='%s %s %s %s %s %s %s' %(str(tb.year),str(tb.month),str(tb.day),str(tb.hour),str(tb.minute),str(tb.second),str(tb.microsecond))
  sta='%s %s %s %s %s %s %s' %(str(ta.year),str(ta.month),str(ta.day),str(ta.hour),str(ta.minute),str(ta.second),str(ta.microsecond))
  f.write(sn+'\n'+stb+'\n'+sta)
  f.close()

  #second modification
  #initialize previous state of buffer
  first3lasttime=[0,0,0]
  countslasttime=0

  while finishing < 1:
      #lm_data_file = (time.strftime("lm_%y%m%d_%H%M%S.csv"))
      lm_data_file = "/home/vladimir/GODOT/data/%s%s.csv"%(sn,time.strftime("_lm4_mod3_%y%m%d_%H%M%S"))
  
      #From lm3 we replaced "clear_statistics" with 0 instead of 1
      emorpho_io.start_lm(all_morpho, sn, [0,0])
      tnextstart=datetime.now()
      bufferfinishing = 0
  
      length=0
      lmstr=""
      #first3lasttime=[0,0,0]
      #countslasttime=0
      filet0 = time.time()
      filefinishing = 0
      
      while (length < filelength and finishing < 1 and filefinishing < 1) :
  
          if (time.time()-filet0 >= float(maxfiletime)):
              filefinishing=1

          if ((datetime.now()-tnextstart).total_seconds() >= float(maxbuffertime)):
              bufferfinishing=1

          if (time.time()-overallt0 >= float(seconds)):
              finishing=1
  
          #Gather data and check where you are in the buffer:
          lm_data = emorpho_io.read(all_morpho, sn, emorpho_io.MA_LISTMODE, 2048,2)
          lm_counts = lm_data[1023] & 0x1FF # number of valid events
  
          #Check for zero length or identical to previous read:
          if lm_counts == 0:
              countslasttime = lm_counts
              first3lasttime=[0,0,0]
              continue
          first3=lm_data[0:3] 
          if first3 == first3lasttime and lm_counts == countslasttime:
              #nothing new; repeated frame.
              if bufferfinishing == 0:
                  continue
              emorpho_io.start_lm(all_morpho, sn, [0,0])
              t0=tnextstart
              tnextstart=datetime.now()
              bufferfinishing = 0
              st='%s %s %s %s %s %s %s' %(str(t0.year),str(t0.month),str(t0.day),str(t0.hour),str(t0.minute),str(t0.second),str(t0.microsecond))
  
              d_lst = '*'
              data  = ' '.join(map(str,d_lst))
              tojoin = [lmstr,st,data]
              lmstr = '\n'.join(tojoin)
  
          #Restart and record if halfway through buffer 
          #(restart comes first to avoid losing time & events)
          if (lm_counts > restartpoint or finishing==1 or filefinishing==1 or bufferfinishing==1):
              emorpho_io.start_lm(all_morpho, sn, [0,0])
              t0=tnextstart
              tnextstart=datetime.now()
              bufferfinishing = 0
  
              st='%s %s %s %s %s %s %s' %(str(t0.year),str(t0.month),str(t0.day),str(t0.hour),str(t0.minute),str(t0.second),str(t0.microsecond))
  
              d_lst = [sn, lm_counts] + lm_data[0:3*lm_counts] 
              data  = ' '.join(map(str,d_lst))
              tojoin = [lmstr,st,data]
              lmstr = '\n'.join(tojoin)
              length = length + lm_counts
  
              #first modification
              countslasttime = lm_counts
              first3lasttime = first3

          #countslasttime = lm_counts
          #first3lasttime = first3
  
      print "length, filename: ", length, lm_data_file
      t1=datetime.now()
      st1='\n%s %s %s %s %s %s %s\n' %(str(t1.year),str(t1.month),str(t1.day),str(t1.hour),str(t1.minute),str(t1.second),str(t1.microsecond))
      f=open(lm_data_file,'w')
      f.write(lmstr)
      f.write(st1)
      f.close()
      totallength = totallength + length
  
  #print "List mode done, total length: ",totallength,"  ",totallength/seconds,"c/s"
