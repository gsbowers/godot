#!/bin/bash

LOCAL_DIR=/media/godot_/data/.

if [ "$#" -ne 1 ]; then
	PREV_UTC_WILDCARD=`date -d "1 hour ago" -u +"*_%y%m%d_%H*.csv"`
	UTC_WILDCARD=$PREV_UTC_WILDCARD
else 
	UTC_WILDCARD="*_$1_*.csv"
fi

echo $UTC_WILDCARD

scp pokko@adele.ucsc.edu:~/Dropbox/data/HAWC/raw/$UTC_WILDCARD $LOCAL_DIR
