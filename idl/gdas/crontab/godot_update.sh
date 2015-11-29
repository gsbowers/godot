#!/bin/bash

if [ "$#" -eq 1 ]; then 
	DATE="$1"
	#/usr/local/bin/godot/get_godot_data.sh $DATE
	/usr/local/bin/godot/make_quicklook.sh $DATE
	/usr/local/bin/godot/upload_quicklook_to_web.sh $DATE
else
	/usr/local/bin/godot/update_field_data.sh
	/usr/local/bin/godot/get_godot_data.sh
	/usr/local/bin/godot/make_quicklook.sh
	/usr/local/bin/godot/upload_quicklook_to_web.sh
	/usr/local/bin/godot/make_ascii.sh
fi
