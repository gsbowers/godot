function get_data_from_file, filename, stopframe=stopframe, silent=silent

;DIAGNOSTIC
if ~keyword_set(stopframe) then stopframe = -1

;initialize main data structure
event = {time:double(!VALUES.F_NAN), energy:ULONG64(0), frame:ULONG(64), ta:ULONG64(0), tb:ULONG64(0)}
events = replicate(event, 10000000l)
count = ULONG64(0)

;initalize data structures associated with frame info  
timestamps = []
goodframes = []
framecount = 0

;read file into array of lines
OpenR, lun, filename, /GET_LUN
nlines = FILE_LINES(filename)
lines = strarr(nlines)
readf, lun, lines
close, lun
free_lun, lun

;seperate lines into lmstrs and timestamps 
lmstrs = lines(indgen(nlines/2)*2)
timestamparrays = lines(indgen(nlines/2)*2 + 1) 

;iterate through frames
;one frame consists of timestamp + lmstr
started = 0
nframes = nlines/2
for frame=1,nframes-1 do begin

	;get timestamp
	a = strsplit(timestamparrays[frame-1], ' ', /extract)
	year = double(a[0])
	month = double(a[1])
	day = double(a[2])
	hour = double(a[3])
	minute = double(a[4])
	second = double(a[5])
	micro = double(a[6])
	timestamp = string(format='(%"%4d-%02d-%02d/%02d:%02d:%0.8g")', $
		year, month, day, hour, minute, second+double(micro*1e-6))

	;DIAGNOSTIC
	;check that timestamp captures all significant figures of micro
	;print, timestamp, ' ', double(micro*1e-6)

	;record timestamp (for all frames)
	timestamps = [timestamps, timestamp]

	;get lmstr data
	a = strsplit(lmstrs[frame], ' ', /extract)
	if n_elements(a) eq 1 then continue ;first lmstr always empty

	buffer_size = a[1]*1 
	
	if started then begin 
		check = check_lmstr(a, lasta, frame, silent=silent)
		;DIAGNOSTIC
		if frame eq stopframe then stop
		if check.flag then continue
	endif

	en = a[indgen(buffer_size)*3+2]*1l
	ta = a[indgen(buffer_size)*3+3]*1l
	tb = a[indgen(buffer_size)*3+4]*1l

	;handle rollovers
	skips=where(tb GT 40000l and shift(tb,-1) LT 20000l, nskips)

	for k=0, nskips-1 do $
		if skips[k]+1 le buffer_size-1 then $
			tb[skips[k]+1:buffer_size-1] += 65536.d	

	t=ta*1.d + tb*65536.d
	t*=12.5d-9

	;make first event in lmstr occur at timestamp  
	t -= t[0]

	;DIAGNOSTIC
	if frame eq stopframe then stop
	

	;add initial time to get seconds since start of day
	;t += hour*3600.0d + minute*60.d + double(second) + micro*1.d-6
	t += gettime(timestamp)

	;record event data
	events[count:count+buffer_size-1].energy = en
	events[count:count+buffer_size-1].time = t
	events[count:count+buffer_size-1].ta = ta
	events[count:count+buffer_size-1].tb = tb
	events[count:count+buffer_size-1].frame = frame

	;DIAGNOSTIC
	if frame eq stopframe then stop

	;record goodframe
	goodframes = [goodframes, frame]
	framecount += 1

	;check that time in frame is monotonic
	dt = shift(t,-1)-t
	dt = dt[0:-2] 
	bad = where(dt lt 0, nbad)
	if nbad gt 0 then begin
		message, string(format='(%"in frame %d: time not monotonic. stopping")', frame)
	endif

	;check that time across frame is monotonic
	if started then begin
		curframe_firstevent_time = events[count].time
		if curframe_firstevent_time lt lastframe_lastevent_time then begin
			print, string(format='(%"across frames %d, %d: time not monotonic.")', goodframes[-2], goodframes[-1])
			print, string(format='(%"filename: %s")', filename)
			print, ''
			show_lmstr, lasta, frame=goodframes[-2], timestamp=timestamps[-2] 
			show_lmstr, a, frame=goodframes[-1], timestamp=timestamps[-1] 
			message, 'stopping'
		endif 
	endif

	count += buffer_size
	lastframe_lastevent_time = events[count-1].time
	lasta = a

	started = 1

endfor

;trim events structure
events = events[0:count-1]

;final check that overall time is monotonic
dt = shift(events.time,-1)-events.time
dt = dt[0:-2]
bad = where(dt lt 0, nbad)
if nbad gt 0 then begin
	message, string(format='(%"filename %s: time not monotonic. stopping")', filename)
endif

data = {time:events.time, energy:events.energy, frame:events.frame, timestamps:timestamps, goodframes:goodframes, filename:filename}

return, data

end
