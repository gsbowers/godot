#!/bin/bash

source ~/.bashrc

if [ "$#" -ne 1 ]; then   
	DATE=`date -d "1 hour ago" -u +"%y%m%d"`
else
	DATE="$1"
fi

cd /home/gsbowers/github/godot/idl/gdas
echo $DATE
idl -e "godot_load_data, '$DATE', channel=[200,1e6], nevents=[50,250,250], /quicklook"
idl -e "godot_load_data, '$DATE', channel=[200,1e6], nevents=[10,25,25], /quicklook, fileprefix='_'"
idl -e "godot_load_spectra, '$DATE', /quicklook"
