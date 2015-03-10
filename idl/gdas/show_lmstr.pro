pro show_lmstr, lmstr, nevents=nevents, frame=frame, timestamp=timestamp

if ~keyword_set(nevents) then nevents = 3

;prepend characters to amplitude, ta, tb
delim = ['','*','#']
delims = []
for i=0,nevents-1 do delims = [delims,delim]

head = indgen(nevents*3+2)
tail = n_elements(lmstr)-reverse(indgen(nevents*3,/UL64)+1)  

if keyword_set(timestamp) and keyword_set(frame) then $ 
	print, string(format='(%"frame %d: %s\r")', frame, timestamp)

print, [['','',delims]+lmstr[head], '...']
print, ['...', delims+lmstr[tail]]
print, ''

end
