pro godot_load_data, date, channel=channel, nevents=nevents

;initialize tplot
thm_graphics_config
tplot_options, 'xmargin', [30,20]
tplot_options, 'ymargin', [5,2]
colors = [0,1,2,3,4,5,6,100,500,510]
window, xsize=700, ysize=500

;get data files
allfiles = get_data_files(date) 

;sn_list = ['eRC1489', 'eRC1490', 'eRC1491']
;description_list = ['SmPl', 'LgNaI', 'LgPl']

sn_list = ['eRC1491']
description_list = ['LgPl']

for n=0, n_elements(sn_list)-1 do begin

	sn = sn_list(n)
	description = description_list(n)

	rates = get_rates_from_date_detector(date, sn,ch=channel,nevents=nevents) 

	print, sn, ': ', description
	files = strfilter(allfiles, '*'+sn+'*.csv')
	
	if n_elements(files) eq 1 then begin
		if files[0] eq '' then begin
			print, 'No files found for ', sn, ': ', description
			continue
		endif
	endif 

	;store data in tplot variable 

	tname = string(format='(%"%s")', description)
	label = string(format='(%"%0d")', nevents)  

	time = rates.time
	rate = rates.rate
		
	w = where(finite(time))

	;store_data, tname, data={x:data[*,ch].time, y:data[*,ch].rate}
	store_data, tname, data={x:time(w), y:rate(w)}
	options, tname, ysubtitle='[cnts/s]', $
		charsize=1.8, labels=label, psym=10, xtitle='Time (UTC)'
		
endfor ;for each sn in sn_list

stop

end
