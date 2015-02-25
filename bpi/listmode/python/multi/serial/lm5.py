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

filelength = 100000
restartpoint = 200
maxfiletime = 2 

#assumes detector has already been booted up and configured with
#boot_all.py and set_all.py

#setup data structs for n emorphos
n = len(sn_list)
#create n-array of empty arrays to hold lm_data for each sn 
lm_data = [[]]*n 
#create n-array of 0s to hold lm_counts for each sn
lm_counts = [0]*n

timeunit = input('Time in seconds (0) or hours (1)? ')
timeunit = int(timeunit)
if timeunit == 0:
    seconds = input('Enter seconds for accumulation: ')
    seconds = float(seconds)
if timeunit == 1:
    hours = input('Enter hours for accumulation: ')
    seconds = float(hours)*3600.

overallt0 = time.time()
totallength=0
finishing=0

while finishing < 1:
  lm_data_dir = "/home/vladimir/github/godot/bpi/listmode/python/multi/serial/data/"
  prefix = ""
  suffix = time.strftime("lm5_%y%m%d_%H%M%S.csv")
  lm_data_file = lm_data_dir+prefix+suffix

  #start listmode in all emorphos
  for sn in sn_list:
    emorpho_io.start_lm(all_morpho, sn, [0,0])

  #n-array of buffer starting times
  tstart = [datetime.now()]*n

  length=0
  lmstr=""
  first2 = [0,0]*n
  first2lasttime = [0,0]*n
  countslasttime = [0]*n
  filet0 = time.time()
  filefinishing = 0

  #poll all emorpho buffers
  while (length < filelength and finishing < 1 and filefinishing < 1) :

    if (time.time()-filet0 >= float(maxfiletime)):
      filefinishing=1

    if (time.time()-overallt0 >= float(seconds)):
      finishing=1

    bufferready = [0]*n
    for i in range(n):
      sn = sn_list[i]
      #Gather data and check where you are in the buffer
      lm_data[i] = emorpho_io.read(all_morpho, sn, emorpho_io.MA_LISTMODE, 2048,2)
      lm_counts[i] = lm_data[i][1023] & 0x1FF # number of valid events
      #print sn, "lm_counts: ",i,": ", lm_counts[i]

      #Check for zero length or identical to previous read:
      if lm_counts[i] == 0:
        countslasttime[i] = lm_counts[i]
        first2lasttime[i]=[0,0]
        bufferready[i] = 0 #buffer has not changed since last read
        continue # goto next emorpho buffer

      #check if buffer has changed since last read
      first2[i]=lm_data[i][0:2] #1st 2 words of buffer
      if first2[i] == first2lasttime[i] and lm_counts[i] == countslasttime[i]:
        bufferready[i] = 0 #buffer has not changed since last read
        continue # goto to next emorpho buffer
      
      #if the loop makes it here then the buffer is ready
      bufferready[i] = 1

    #check if any buffers are ready to be recorded
    if max(bufferready) == 0:
      continue # no buffers ready. keep polling

    #check if buffer needs to be restarted and recorded 
    #(restart first to avoid losing time & events)
    for i in range(n):
      sn = sn_list[i]
      if ((bufferready[i] and lm_counts[i] > restartpoint) or finishing==1 or filefinishing==1):

        #restart
        emorpho_io.start_lm(all_morpho, sn, [0,0])
        t0=tstart[i]
        tstart[i]=datetime.now()

        #record buffer data
        st='%s %s %s %s %s %s %s' %( str(t0.year), str(t0.month), str(t0.day), str(t0.hour), str(t0.minute), str(t0.second), str(t0.microsecond))

        #print sn, "lm_counts: ", lm_counts

        d_lst = [sn, lm_counts[i]] + lm_data[i][0:3*lm_counts[i]]
        data  = ' '.join(map(str,d_lst))
        tojoin = [lmstr,st,data]
        lmstr = '\n'.join(tojoin)
        length = length + lm_counts[i]

			#for each sn, update countslast and first2
      countslasttime[i] = lm_counts[i]
      first2lasttime[i] = first2[i]

  print "length, filename: ", length, lm_data_file
  t1=datetime.now()
  st1='\n%s %s %s %s %s %s %s\n' %( str(t1.year), str(t1.month),  str(t1.day), str(t1.hour), str(t1.minute), str(t1.second), str(t1.microsecond))

  f=open(lm_data_file,'w')
  f.write(lmstr)
  f.write(st1)
  f.close()
  totallength = totallength + length

print "List mode done, total length: ",totallength,"  ",totallength/seconds,"c/s"
