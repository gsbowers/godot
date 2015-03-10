function get_rates_from_date_detector, date, detector, ch=ch, nevents=nevents
;bdas parameter/alias checking

;valid detector names
vdetectors = ['eRC1489', 'eRC1490', 'eRC1491']

;define aliases
smpl_aliases = ['SMALL', 'SmPl']
lgnai_aliases = ['NAI', 'LgNaI']
lgpl_aliases = ['LARGE', 'LgPl']

;search DETECTOR aliases
smpl_request = strfilter(smpl_aliases, detector, /FOLD_CASE, COUNT=n_smpl)
lgnai_request= strfilter(lgnai_aliases, detector, /FOLD_CASE, COUNT=n_lgnai)
lgpl_request = strfilter(lgpl_aliases, detector, /FOLD_CASE, COUNT=n_lgpl)

vdetector_key = where([n_smpl, n_lgnai, n_lgpl], n_aliased)

not_aliased = strfilter(vdetectors, detector, delimiter=' ',/string,/FOLD_CASE)
print, '  NOT ALIASED: ', not_aliased

if (n_aliased GT 0) THEN BEGIN
	are_aliased = vdetectors[vdetector_key]
	print, '  ARE ALIASED: ', are_aliased
	detector = [not_aliased, are_aliased]
	sorted_detectors = detector[SORT(detector)]
	detector = sorted_detectors[UNIQ(sorted_detectors)]
ENDIF ELSE detector = not_aliased 
detector = detector(where(detector ne ''))
detector = detector[0] ;only take first detector
print, 'Requesting ... ', detector

;load filenames from /media/godot/data for given date
allfiles=file_search('/media/godot/data/*_'+date+'_*.csv')
;pull last file from end of previous day for small plastic
prevfiles = []
dhour = 1
while (prevfiles eq !NULL or prevfiles eq '') and (dhour lt 8) do begin
	prevfiles=file_search('/media/godot/data/eRC1489*'+$
		time_string(gettime('20'+date)-3600-dhour,$
			tformat='yyMMDD_hh')+'*.csv')
	dhour++
endwhile
allfiles = [prevfiles, allfiles]

;get files associated with requested decetor
files = strfilter(allfiles, '*'+detector+'*.csv')

;concatenante rates from all files
allrates = []
for i=0, n_elements(files)-1 do begin

	filename = files[i]
	data = get_data_from_file(filename)
	rates = get_rates_from_data(data, ch=ch, nevents=nevents) 
	
	allrates = [allrates, rates]

endfor

return, allrates

end
