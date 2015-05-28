function get_time_from_ta_tb, ta, tb

;handle rollovers in data 
skips=where(tb GT 40000l and shift(tb,-1) LT 20000l, nskips)

n = n_elements(ta)
for k=0, nskips-1 do $
	if skips[k]+1 le n-1 then $
		tb[skips[k]+1:n-1] += 65536.d	
	
t=ta*1.d + tb*65536.d
t*=12.5d-9

return, t

end
