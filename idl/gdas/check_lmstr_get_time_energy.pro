function check_lmstr_get_time_energy, lmstr, prev_lmstr=prev_lmstr
  
  ;initialize return structure
  ret = {flag:0}
  
  a = lmstr
  buffer_size = a[1]*1
  
  ;1
  
  ;compare lmstr to previous lmstr
  if keyword_set(prev_lmstr) then begin
  
  	preva = prev_lmstr
  	prev_buffer_size = preva[1]*1
  
  	; check if lmstr same as previous lmstr
  	if prev_buffer_size lt buffer_size then begin 
  		; sometimes lmstr is same as previous lmstr except that 
  		; first event is different: compare a and lasta starting at 5 
      if n_elements(a) gt 5 and n_elements(preva) gt 5 then $
  		if array_equal(a[5:prev_buffer_size*3+1], preva[5:-1]) then begin
  			ret.flag = 1 ;continue
  			return, ret
  		endif ;if last buffer is repeated
  	endif ;if last_buffer_size lt buffer_size
  
  endif ;if prev_lmstr defined
  
  ;get energy and timing information from lmstr
  en = a[indgen(buffer_size)*3+2]*1l
  ta = a[indgen(buffer_size)*3+3]*1l ;least sig. timing byte
  tb = a[indgen(buffer_size)*3+4]*1l ;most sig. timing byte
  
  w0 = 0 ;index of first event in frame
  
  ;2
  
  ;handle rollovers 
  skips=where(tb GT 40000l and shift(tb,-1) LT 20000l, nskips)
  
  for k=0, nskips-1 do $
  	if skips[k]+1 le buffer_size-1 then $
  		tb[skips[k]+1:buffer_size-1] += 65536.d	
  
  t=ta*1.d + tb*65536.d
  t*=12.5d-9
  
  ;make time of first event in lmstr equal to 0
  t -= t[w0]
  
  ;record time and energy
  tb = a[indgen(buffer_size)*3+4]*1l ;most sig. timing byte
  ret = {flag:ret.flag, time:t, ta:ta, tb:tb, energy:en, lmstr:lmstr}
  
  return, ret

end

;   discontinuity due to end of the previous buffer 
;   being included at end of the current buffer.
;
;   frame 20 in  
;   /media/godot/data/eRC1490_lm7_newfirm_141206_202723.csv
;   frame 1 in
;   /media/godot/data/eRC1490_lm7_newfirm_141225_130920.csv
;
