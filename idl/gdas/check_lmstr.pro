function check_lmstr, a,lasta, frame, silent=silent

flag = 0
reta = -1

buffer_size = a[1]*1
last_buffer_size = lasta[1]*1

;1. check if current working buffer is same as previous buffer 
if last_buffer_size lt buffer_size then begin 
	if array_equal(a[5:last_buffer_size*3+1], lasta[5:-1]) then begin
		if ~keyword_set(silent) then $
			print, string(format='(%"frame %2d: current buffer same as previous buffer")', frame)
		flag = 1 ;continue
		reta = -1
		return, {flag:flag, a:reta}
	endif ;if last buffer is repeated
endif ;if last_buffer_size lt buffer_size

;2. check for anomalous jumps in significant timing byte
;frame 20 in  
;/media/godot/data/eRC1490_lm7_newfirm_141206_202723.csv
;frame 1 in
;/media/godot/data/eRC1490_lm7_newfirm_141225_130920.csv

;multiple jumps appear in
;frame 20 in 
;/media/godot/data/eRC1491_lm7_newfirm_141206_041658.csv
;ta->tb, tb->en, en->ta (??)

tb = a[indgen(buffer_size)*3+4]*1l

;check for large positive jumps in tb
dtb = (shift(tb,-1)-tb)[0:-2]
jumps = where(dtb gt 100, njumps)

if njumps gt 0 then begin
	if ~keyword_set(silent) then $
		print, string(format='(%"frame %2d: jump in frame")', frame)
	stop
	flag = 1; continue
	reta = -1;
	return, {flag:flag, a:reta}
endif

reta = a
flag = 0
return, {flag:flag, a:reta}

end
