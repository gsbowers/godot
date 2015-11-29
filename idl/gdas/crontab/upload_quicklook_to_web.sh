#!/bin/bash

if [ "$#" -ne 1 ]; then 
	DATE=`date -d "1 hour ago" -u +"%y%m%d"`
else 
	DATE="$1"
fi

#cd /home/gsbowers/github/godot/idl/gdas/quicklook_plots/HAWC/.
#cd /home/gsbowers/github/godot/idl/gdas/quicklook_plots/KANAZAWA/.
cd /home/gsbowers/github/godot/idl/gdas/quicklook_plots/UCHINADA/.

scp "./godot_$DATE.png" gsbowers@gsbowers.webfactional.com:~/webapps/godot/quicklook/lgbin/.
scp "./_godot_$DATE.png" gsbowers@gsbowers.webfactional.com:~/webapps/godot/quicklook/smbin/.
scp "./SSPC_CUSTOM/godot_SSPC_LgNaI_$DATE.png" gsbowers@gsbowers.webfactional.com:~/webapps/godot/quicklook/sspc/.
