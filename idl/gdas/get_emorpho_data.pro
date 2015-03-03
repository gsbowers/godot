pro get_emorpho_data, filename

;initialize main data structure
event = {timestamp:'', time:!VALUES.F_NAN, energy:ULONG64(0)}
data = replicate(event, 10000000l)

;read file into array of lines
OpenR, lun, filename, /GET_LUN
nlines = FILE_LINES(filename)
lines = strarr(nlines)
readf, lun, lines
close, lun 

;seperate lines into lmbuffers and timestamps 
lmbuffers = lines(indgen(nlines/2)*2)
timestamps =  lines(indgen(nlines/2)*2 + 1) 

for i=0,nlines/2-1 do begin

	;get timestamp
	a = strsplit(timestamps[i], ' ', /extract)
	year = double(a[0])
	month = double(a[1])
	day = double(a[2])
	hour = double(a[3])
	minute = double(a[4])
	second = double(a[5])
	micro = double(a[6])
	timestamp = string(format='(%"%4d-%02d-%02d/%02d:%02d:%0.8g")', $
		year, month, day, hour, minute, second+double(micro*1e-6))

	;check that timestamp captures all significant figures of micro
	;print, timestamp, ' ', double(micro*1e-6)

	;get lmbuffer data
	a = strsplit(lmbuffers[i], ' ', /extract)

endfor


stop

end
