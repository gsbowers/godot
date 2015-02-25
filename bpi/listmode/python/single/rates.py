#!/usr/bin/python
#
# version 1.0
from __future__ import division
import time
import sys
import emorpho_io
import ftdi

#Note: durations < 3 seconds appear to give rates too high relative
#to the asymptotic limit of longer durations.  
iterations=4
interval = 5.


# start new MCA acquisition
# http://www.bridgeportinstruments.com/products/mds/mds_doc/read_mca.php

print '  Time        events   triggers dead fraction'

sumct=0.
sumtr=0.
sumti=0.
for i in range(iterations):
    cmd_record = [0, 2, 1, 1, 1, 0, 1]
    emorpho_io.start_mca(all_morpho, sn, cmd_record)
    time.sleep(interval)
    rates  = emorpho_io.get_rates(all_morpho, sn)
    print("%10.3f %8i %8i %10.3f"%(rates[5],rates[1],rates[2],rates[3]))
    sumct = sumct+rates[1]
    sumtr = sumtr+rates[2]
    sumti = sumti + interval
print 'Event rate, trigger rate: '
print ("%10.3f %10.3f"%(sumct/sumti, sumtr/sumti))
