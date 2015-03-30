function get_data_from_file, filename, stopframe=stopframe, silent=silent

;DIAGNOSTIC
if ~keyword_set(stopframe) then stopframe = -1

;initialize main data structure
event = {time:double(!VALUES.F_NAN), energy:LONG(0), frame:LONG(64), ta:LONG(0), tb:LONG(0)}
events = replicate(event, 10000000l)
count = ULONG64(0)

;initalize data structures associated with frame info  
timestamps = []
goodframes = []
framecount = 0

;initialize data structures associated with file info
frameflag = {flag0:0, flag1:0, flag2:0, flag3:0, flag5:0, flag9:0}
frameflags = replicate(frameflag, 1000)

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
	timestamp = string(format='(%"%4d-%02d-%02d/%02d:%02d:%0.8f")', $
		year, month, day, hour, minute, second+double(micro*1e-6))

	;DIAGNOSTIC
	;check that timestamp captures all significant figures of micro
	;print, timestamp, ' ', double(micro*1e-6)

	;record timestamp (for all frames)
	timestamps = [timestamps, timestamp]

	;get lmstr data
	a = strsplit(lmstrs[frame], ' ', /extract)
	if n_elements(a) eq 1 then continue ;frame 0 always empty

	if started then $
		ret = check_lmstr_get_time_energy(a, prev_lmstr=lasta) $
	else $
		ret = check_lmstr_get_time_energy(a)

	;DIAGNOSTIC
	if frame eq stopframe then stop

	flag = 0
	print, filename
	SWITCH ret.flag of
		1:BEGIN
				print, string(format='(%"frame %2d: repeated frame")', frame)
				flag = 1
				frameflags[frame].flag1 = 1
				BREAK
			END	
		2:BEGIN
				print, string(format='(%"frame %2d: orphan data")', frame)
				flag = 0
				frameflags[frame].flag2 = 1
				BREAK	
			END
		3:BEGIN
				print, string(format='(%"frame %2d: corrupt frame")', frame)
				flag = 0
				frameflags[frame].flag3 = 1
				a = ret.lmstr	
				BREAK
			END
		5:BEGIN
				print, string(format='(%"frame %2d: corrupt frame with orphan data")', frame)
				flag = 0
				frameflags[frame].flag5 = 1
				a = ret.lmstr	
				BREAK
		END
		ELSE:BEGIN
				frameflags[frame].flag0 = 1
			END	
	ENDSWITCH	

	if flag then continue

	t = ret.time
	
	;add initial time to get seconds since start of day
	;t += hour*3600.0d + minute*60.d + double(second) + micro*1.d-6
	t += gettime(timestamp)

	;check that time in frame is monotonic
	dt = shift(t,-1)-t
	dt = dt[0:-2] 
	bad = where(dt lt 0, nbad)
	if nbad gt 0 then begin
		print, string(format='(%"filename: %s")', filename)
		print, string(format='(%"in frame %d: time not monotonic")', frame)
		frameflags[frame].flag9 = 1
		openw, 20, 'log.txt'
		printf, 20, string(format='(%"filename: %s")', filename)
		printf, 20, string(format='(%"in frame %d: time not monotonic.")', frame)
		close, 20

		continue
	endif

	;record event data
	buffer_size = a[1]*1l
	events[count:count+buffer_size-1].energy = ret.energy
	events[count:count+buffer_size-1].time = t
	events[count:count+buffer_size-1].ta = ret.ta
	events[count:count+buffer_size-1].tb = ret.tb
	events[count:count+buffer_size-1].frame = frame

	;DIAGNOSTIC
	if frame eq stopframe then stop

	;record goodframe
	goodframes = [goodframes, frame]
	framecount += 1

	;CHECK DATA (1)

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

;CHECK DATA (2)

;final check that overall time is monotonic
dt = shift(events.time,-1)-events.time
dt = dt[0:-2]
bad = where(dt lt 0, nbad)
if nbad gt 0 then begin
	message, string(format='(%"filename %s: time not monotonic. stopping")', filename)
endif

data = {time:events.time, energy:events.energy, frame:events.frame, timestamps:timestamps, goodframes:goodframes, filename:filename, frameflags:frameflags[0:nframes-1]}

return, data

end
