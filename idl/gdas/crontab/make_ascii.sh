#!/bin/bash

source ~/.bashrc

DATE=`date -d "0 hour ago" -u +"%y%m%d"`
cd /home/gsbowers/github/godot/idl/tolga

rm -f /home/gsbowers/github/godot/idl/tolga/ascii/SmPl.csv
idl -e "to_ascii_from_date_detector, '$DATE', 'eRC1489',filename='SmPl.csv'"
rm -f /home/gsbowers/github/godot/idl/tolga/ascii/NaI.csv
idl -e "to_ascii_from_date_detector, '$DATE', 'eRC1490', filename='NaI.csv'"
rm -f /home/gsbowers/github/godot/idl/tolga/ascii/LgPl.csv
idl -e "to_ascii_from_date_detector, '$DATE', 'eRC1491', filename='LgPl.csv'"
cd /home/gsbowers/github/godot/idl/tolga/ascii
scp *.csv gsbowers@gsbowers.webfactional.com:~/webapps/godot_mx/tolga/.
