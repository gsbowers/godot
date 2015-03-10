function checklmbuffer, a,lasta, frame

flag = 0
reta = -1

buffer_size = a[1]
last_buffer_size = lasta[1]

;1. throw out events at beginning of frame that are leftover 
;from end of previous frame.  check that it's not rollover
;prevleftover = 0
;tb_cur_first = double(a[4])
;tb_cur_second = double(a[7])
;tb_prev_last = double(lasta[-1])
;if ((tb_cur_first - tb_prev_last) le 500) and abs(tb_cur_second - tb_cur_first) gt 1000 and ((65536 - tb_cur_first) gt 500) then begin

;			a = [a[0:1], a[5:-1]] ;remove first event in current buffer
;			buffer_size -= 1
;			message, string(fromat='(%"frame %d: First event leftover from previous frame")', frame) 
;			prevleftover = 1
;		endif  

;2. check if current working buffer is same as previous buffer 
if last_buffer_size lt buffer_size then begin 
	if array_equal(a[5:last_buffer_size*3+1], lasta[5:-1]) then begin
		print, string(format='(%"frame %d: current buffer same as previous buffer")', frame)
		flag = 1 ;continue
		reta = -1
	endif ;if last buffer is repeated
endif ;if last_buffer_size lt buffer_size

ret = {flag:flag, a:reta}

return, ret

end
