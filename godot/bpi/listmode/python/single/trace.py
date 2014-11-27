#!/usr/bin/python
#
# version 1.0
from __future__ import division
import zmq
import time
import sys
import emorpho_io
import ftdi
import matplotlib.pyplot as plot
import numpy


triggered = 1  #1 or 0
offset=100
samples = 1024
pngfile='atrace.png'

#assumes detector has already been booted up and configured with
#setplastic_api.py or setnai_api.py

print "Starting trace acquisition...\n"
										
cmd_data = [triggered, offset]
entered=1

while entered != 0:
    emorpho_io.start_trace(all_morpho, sn, cmd_data)

    time.sleep(1)

    trace = emorpho_io.read(all_morpho, sn, emorpho_io.MA_TRACE, 2*samples, 2)

    print "Sample values from start of trace:\n"
    print trace[0:32]
    #Insert python code here to open a file and save raw trace data if
    # you want
    print len(trace)

    fig = plot.figure
    ymx=numpy.amax(trace)
    ymn=numpy.amin(trace)        
    ymax=1.05*ymx
    ymin=0.95*ymn
    len = numpy.alen(trace)
    x_max = len
    xseries = numpy.zeros(len)
    for n in range(0,len,1):
        xseries[n] = float(n)
    plot.plot(xseries, trace, label=" ")
    plot.xlabel("Time, raw bins")
    plot.ylabel("ADC value")
    plot.title("Trace - " + sn)
    plot.xlim(0, x_max)
    plot.ylim(ymin,ymax)
    plot.ion()
    plot.show()
    entered = input('Get another? (0=no, 1=yes): ')

plot.savefig(pngfile, bbox_inches='tight')
