function get_data_from_file, filename

	;,stopframe=stopframe, hang=hang, logfile=logfile
	
	;DIAGNOSTIC
	if ~keyword_set(stopframe) then stopframe = -1
	
	if ~keyword_set(logfile) then logfile='log.txt'
	
	;initialize main data structure
	event = {time:double(!VALUES.F_NAN), energy:LONG(0), frame:LONG(64), ta:LONG(0), tb:LONG(0)}
	;events = replicate(event, 100000000l)
	events = replicate(event, 10000000l)
	count = ULONG64(0)
	
	;initalize data structures associated with frame info  
	timestamps = []
	goodframes = []
	framecount = 0
	
	;initialize data structures associated with file info
	frameflag = {flag0:0, flag1:0, flag2:0}
	frameflags = replicate(frameflag, 1000)
	
	;read file into array of lines
	OpenR, lun, filename, /GET_LUN
	nlines = FILE_LINES(filename)
	lines = strarr(nlines)
	readf, lun, lines
	close, lun
	free_lun, lun
	
	if nlines le 2 then return, -1
	
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
		;print, filename
		SWITCH ret.flag of
			1:BEGIN
					;print, string(format='(%"frame %2d: repeated frame")', frame)
					flag = 1
					frameflags[frame].flag1 = 1
					BREAK
				END	
			ELSE:BEGIN
					flag = 0
					frameflags[frame].flag0 = 1
				END	
		ENDSWITCH	
	
		if flag then continue
	
		t = ret.time
		
		;add initial time to get seconds since start of day
		;t += hour*3600.0d + minute*60.d + double(second) + micro*1.d-6
		t += gettime(timestamp)
	
		if n_elements(t) ge 3 then begin
	
		;check that time in frame is monotonic
		dt = shift(t,-1)-t
		dt = dt[0:-2] 
		bad = where(dt lt 0, nbad)
		if nbad gt 0 then begin
			print, string(format='(%"filename: %s")', filename)
			print, string(format='(%"in frame %d: time not monotonic")', frame)
			frameflags[frame].flag2 = 1
			openw, 20, logfile, /append
			printf, 20, string(format='(%"filename: %s")', filename)
			printf, 20, string(format='(%"in frame %d: time not monotonic.")', frame)
			close, 20
	
			continue
		endif
	
		;check that time across frame is monotonic
		if started then begin
			curframe_firstevent_time = t[0]
			if curframe_firstevent_time lt lastframe_lastevent_time then begin
				print, string(format='(%"time across frames not monotonic: at frame %d.")', frame)
				print, string(format='(%"filename: %s")', filename)
				frameflags[frame].flag2 = 2
				openw, 20, logfile, /append
				printf, 20, string(format='(%"time across frames not monotonic: at frame %d.")', frame)
				printf, 20, string(format='(%"filename: %s")', filename)
				close, 20
	
				;throw away previous frame and keep going
				count -= buffer_size 
				if n_elements(goodframes) gt 1 then goodframes = goodframes[0:-2]
				framecount -= 1
	
			endif 
		endif
	
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
	
		count += buffer_size
		lastframe_lastevent_time = events[count-1].time
		lasta = a
	
		started = 1
	
	endfor
	
	if count eq 0 then return, -1
	
	;trim events structure
	events = events[0:count-1]
	
	;CHECK DATA (2)
	
	;final check that overall time is monotonic
	;if n_elements(events.time) ge 3 then begin
	;dt = shift(events.time,-1)-events.time
	;dt = dt[0:-2]
	;bad = where(dt lt 0, nbad)
	;if nbad gt 0 then begin
	;	message, string(format='(%"filename %s: time not monotonic. stopping")', filename)
	;endif
	;endif
	
	if goodframes eq !NULL then goodframes = -1
	
	data = {time:events.time, energy:events.energy, frame:events.frame, timestamps:timestamps, goodframes:goodframes, filename:filename, frameflags:frameflags[0:nframes-1], tb:events.tb, ta:events.ta}
	
	if keyword_set(hang) then stop
	
	return, data

end
