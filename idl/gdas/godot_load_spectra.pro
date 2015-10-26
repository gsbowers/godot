pro godot_load_spectra, date, calibration=calibration, quicklook=quicklook, custom=custom, wsize=wsize

;initialize tplot
thm_graphics_config
tplot_options, 'xmargin', [20,15]
tplot_options, 'ymargin', [5,2]
window, xsize=700, ysize=500

;sn_list = ['eRC1489', 'eRC1490', 'eRC1491']
;description_list = ['SmPl', 'LgNaI', 'LgPl']

sn_list = ['eRC1490']
description_list = ['LgNaI']

for n=0, n_elements(sn_list)-1 do begin

	sn = sn_list(n)
	s = get_spectra_from_date_detector(date,sn, calibration=calibration, custom=custom, wsize=wsize) 

	description=description_list[n]
	tname = string(format='(%"%s")', description)

	;store spectrogram

	dlimit={spec:1,zlog:1,ylog:1, $
		ztitle:"counts",zsubtitle:"[15s]",$
		ztickformat:"logticks_exp",$
    ytitle:tname, ysubtitle:"[ADC Units]", $
		yrange:[100, 1e4],ystyle:1,$
    xtitle:'UTC', $
		charsize:1.8}

	if keyword_set(calibration) then begin 
		dlimit.ysubtitle="[MeV]"
		dlimit.ztitle="[cts/MeV/s]"
		dlimit.yrange=[0.1,15]
		;dlimit.yrange=[15,0.1]
	endif
	

	store_data, tname, $
		data={x:s.time, y:s.spectra, v:s.amplitudes}, dlimit=dlimit
	if keyword_set(quicklook) then begin
		window, xsize=700, ysize=500
		tplot, tname
		t0 = gettime('20'+date)
		tlimit, [t0,t0+86400]
		;write_png, './quicklook_plots/NOTO/SSPC_CUSTOM/'+'godot_SSPC_'+description+'_'+date+'.png', tvrd(/true)
		if ~keyword_set(custom) then $ 
			write_png, './quicklook_plots/KANAZAWA/SSPC_CUSTOM/'+'godot_SSPC_'+description+'_'+date+'.png', tvrd(/true) $
		else $
			write_png, './quicklook_plots/KANAZAWA/SSPC_CUSTOM2/'+'godot_SSPC_'+description+'_'+date+'.png', tvrd(/true)
	endif

endfor

end
