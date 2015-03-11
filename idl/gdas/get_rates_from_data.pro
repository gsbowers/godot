function get_rates_from_data, data, binsize=binsize, ch=ch, nevents=nevents

;check that data is structure with 'energy' and 'time' tags
if ~is_struct(data) then $
	message, "data expected to be struct with tag names 'ENERGY','TIME','FRAME', 'GOODFRAMES', 'FILENAME'"
tagnames = tag_names(data)	
w = where(tagnames eq 'ENERGY', count)
if count ne 1 then $
	message, "data expected to be struct with tag names 'ENERGY'"
w = where(tagnames eq 'TIME', count)
if count ne 1 then $
	message, "data expected to be struct with tag names 'TIME'"
w = where(tagnames eq 'FRAME', count)
if count ne 1 then $
	message, "data expected to be struct with tag name 'FRAME'"
w = where(tagnames eq 'GOODFRAMES', count)
if count ne 1 then $
	message, "data expected to be struct with tag name 'GOODFRAMES'"
w = where(tagnames eq 'FILENAME', count)
if count ne 1 then $
	message, "data expected to be struct with tag name 'FILENAME'"

;check keywords
if ~keyword_set(ch) then ch = [1,1e4]

;initialize main data structure
rate = {time:double(!VALUES.F_NAN), counts:double(!VALUES.F_NAN), rate:double(!VALUES.F_NAN), dt:double(!VALUES.F_NAN), filename:'', fid:-1}   	
rates = replicate(rate, 10000000l)	
count = ULONG64(0)	

;calculate rates within frames 
nframes = n_elements(data.goodframes)	

for i=0,nframes-1 do begin

	frame = data.goodframes(i)

	;extract event amplitudes in frame
	wf = where(data.frame eq frame,nwf)
	energy = data.energy(wf) ;event amplitude;

	;extract events within given channel
	w = where(energy gt ch[0] and energy le ch[1], n)
	if n eq 0 then continue

	;get event times within given frame and channel
	t = data.time(wf)
	t = t(w)

	;calculate rates from event times
	;using either fixed interval or fixed number of events
	if ~keyword_set(binsize) and ~keyword_set(nevents) then $
		nevents = 50

	if keyword_set(nevents) then begin ;fixed number of events

		if nevents gt n then nevents = n

		nbins = n/nevents
		nmod = n mod nevents

		;distribute remainder events evenly amongst nbins	
		nadd = nmod/nbins ;events to add to every bin
		nmod = nmod - nmod/nbins*nbins ;new remainder

		ntot = nevents+nadd ;total events per bin

		for bin=0, nbins-1 do begin
			
			;distribute remainder of remainder events into first nmod bins
			if nmod gt 0 then $ 
				select = indgen(ntot+1, /UL64)+bin*(ntot+1) $
			else $
				select = indgen(ntot, /UL64)+bin*ntot + (n mod ntot)
			nmod--

			tbin = t(select)

			rate.time = (tbin[-1]+tbin[0])/2
			rate.counts = n_elements(select)  
			rate.dt = tbin[-1]-tbin[0]
			rate.rate = double(rate.counts/rate.dt)
			rate.filename = data.filename

			rates[count] = rate
			count++
		endfor

	endif else begin ;fixed interval
	
	endelse
		
endfor

return, rates[0:count-1]

end
