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

;two types of jumps occur in tb
;type 1: rollover 
;type 2: discontinuity due to end of the previous buffer 
;        being included at end of the current buffer. try
;        to recover this orphaned data.  examples 
;
;   frame 20 in  
;   /media/godot/data/eRC1490_lm7_newfirm_141206_202723.csv
;   frame 1 in
;   /media/godot/data/eRC1490_lm7_newfirm_141225_130920.csv
;
;type 3: corrupted frame due to bad event offsetting 
;        en, ta, tb
;

;handle type 3 jump first
if max(en) gt 15000 then begin

	ret.flag = 3

	if max(tb) le 15000 then begin

		en_tmp = tb[0:-2] 
		ta_tmp = en[1:-1]
		tb_tmp = ta[1:-1]

		en = en_tmp
		ta = ta_tmp
		tb = tb_tmp

		;update buffer size
		buffer_size = n_elements(en) 

		;update lmstr
		lmstr = create_lmstr(en, ta, tb)
	
	endif else begin

		en_tmp = ta[0:-2] 
		ta_tmp = tb[0:-2]
		tb_tmp = en[1:-1]

		en = en_tmp
		ta = ta_tmp
		tb = tb_tmp

		;update buffer size
		buffer_size = n_elements(en) 

		;update lmstr
		lmstr = create_lmstr(en, ta, tb)
	endelse 	

endif


;check for large jumps in tb
dtb = (shift(tb,-1)-tb)[0:-2]
jumps = where(abs(dtb) gt 1e4, njumps)+1

if njumps gt 0 then begin

	;check only for type 2 jumps if prev_lmstr is defined
	if keyword_set(prev_lmstr) then begin

		last_prev_en = preva[-3] ;last energy from prev lmstr
		last_prev_ta = preva[-2] 
		last_prev_tb = preva[-1] 

		;see if last event from previous frame matches event 
		;in current frame past last jump (jumps[-1]:-1)

		en_past_jump = en[jumps[-1]:-1]
		ta_past_jump = ta[jumps[-1]:-1]
		tb_past_jump = tb[jumps[-1]:-1]

		w = where(en_past_jump eq last_prev_en and $
							ta_past_jump eq last_prev_ta and $
              tb_past_jump eq last_prev_tb, count)+1
		
		if count then begin
			if w le n_elements(en_past_jump) then begin

				ret.flag += 2 ;on return update lmstr

				orphan_en = en_past_jump[w:-1]
				orphan_ta = ta_past_jump[w:-1]
				orphan_tb = tb_past_jump[w:-1]

				;move orphan data to beginning of buffer
				en = [orphan_en, en[0:jumps[-1]-1]]
				ta = [orphan_ta, ta[0:jumps[-1]-1]]
				tb = [orphan_tb, tb[0:jumps[-1]-1]]

				w0 = n_elements(orphan_en) ;index of first event
	
				;update buffer size
				buffer_size = n_elements(en) 

				;update lmstr
				lmstr = create_lmstr(en, ta, tb)

			endif ;if orphaned data good
		endif ;if orphaned data exists
	endif ;if prev_lmstr
endif ;if njumps gt 0

;3

;handle rollovers (type 1)
skips=where(tb GT 40000l and shift(tb,-1) LT 20000l, nskips)

for k=0, nskips-1 do $
	if skips[k]+1 le buffer_size-1 then $
		tb[skips[k]+1:buffer_size-1] += 65536.d	

t=ta*1.d + tb*65536.d
t*=12.5d-9

;make time of first event in lmstr equal to 0
t -= t[w0]

;record time and energy
ret = {flag:ret.flag, time:t, ta:ta, tb:tb, energy:en, lmstr:lmstr}

return, ret

end
