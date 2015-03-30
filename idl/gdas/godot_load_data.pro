pro godot_load_data, date, channel=channel, nevents=nevents, quicklook=quicklook

;initialize tplot
thm_graphics_config
tplot_options, 'xmargin', [20,15]
tplot_options, 'ymargin', [5,2]
colors = [0,1,2,3,4,5,6,100,500,510]
window, xsize=700, ysize=500

;get data files
allfiles = get_filenames(date) 

sn_list = ['eRC1489', 'eRC1490', 'eRC1491']
description_list = ['SmPl', 'LgNaI', 'LgPl']

;sn_list = ['eRC1489']
;description_list = ['SmPl']

data = []

for n=0, n_elements(sn_list)-1 do begin

	sn = sn_list(n)
	description = description_list(n)
		
	if keyword_set(nevents) then $
		if n_elements(nevents) gt 1 then $ 
			pass_nevents = nevents[n] $
		else $
			pass_nevents = nevents $
	else $
		pass_nevents = 50

		rates = get_rates_from_date_detector(date, sn,ch=channel,$
			nevents=pass_nevents) 

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
	label = string(format='(%"%0d")', pass_nevents)  

	time = rates.time
	rate = rates.rate
		
	w = where(finite(time))

	;store rate data
	store_data, tname, data={x:time(w), y:rate(w)}
	options, tname, ysubtitle='[cnts/s]', $
		charsize=1.8, labels=label, psym=0, xtitle='UTC'
	if max(rate(w) gt 10e3) then $	
		options, tname, ylog=1

	;store fileid (use 'get_filenames(date)' to do lookup
	tname = string(format='(%"%s_FID")', description)
	label = string(format='(%"%s")', 'File_ID')
	store_data, tname, data={x:time(w), y:rates(w).fid}	
	options, tname, charsize=1.8, labels=label, psym=0, xtitle='UTC'

	;store flag data
	tname0 = string(format='(%"%s_flag0")', description)
	label = 'good'
	store_data, tname0, data={x:time(w), y:rates(w).flag0}
	options, tname0, charsize=1.8, labels=label, psym=0, xtitle='UTC'

	tname1 = string(format='(%"%s_flag1")', description)
	label = 'repeat'
	store_data, tname1, data={x:time(w), y:rates(w).flag1}
	options, tname1, charsize=1.8, labels=label, psym=0, xtitle='UTC'

	tname2 = string(format='(%"%s_flag2")', description)
	label = 'jumps'
	store_data, tname2, data={x:time(w), y:rates(w).flag2}
	options, tname2, charsize=1.8, labels=label, psym=0, xtitle='UTC'

	tname3 = string(format='(%"%s_flag3")', description)
	label = 'orphan'
	store_data, tname3, data={x:time(w), y:rates(w).flag3}
	options, tname3, charsize=1.8, labels=label, psym=0, xtitle='UTC'

	tname = string(format='(%"%s_Flags")', description)
	store_data, tname, data=[tname0, tname1, tname2, tname3]
	options, tname, colors=colors[0:4]

	data = [data, rates]
	
endfor ;for each sn in sn_list

;make quicklook plots
if keyword_set(quicklook) then begin
	window, xsize=700, ysize=500
	tplot, description_list
	t0 = gettime('20'+date)
	tlimit, [t0, t0+86400]
	write_png, './quicklook_plots/godot_'+date+'.png', tvrd(/true)
endif

;save data products
save, data, filename='./savdat/godot_'+date+'.sav', /compress
end
