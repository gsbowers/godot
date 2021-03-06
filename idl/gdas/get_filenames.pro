function get_filenames, date, timespan=timespan, filter=filter 

datadir = '/media/godot_/data/'

;load filenames from /media/godot/data for given date
files=file_search(datadir+'*_'+date+'_*.csv')
;pull last file from end of previous day for small plastic
prevfiles = []
dhour = 1
while (prevfiles eq !NULL or prevfiles eq '') and (dhour lt 8) do begin
	prevfiles=file_search(datadir+'eRC1489*'+$
		time_string(gettime('20'+date)-3600*dhour,$
			tformat='yyMMDD_hh')+'*.csv')
	dhour++
endwhile

files = [prevfiles, files]

if keyword_set(filter) then $ 
	files = strfilter(files, filter)

return, files

end
