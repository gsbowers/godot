function get_t0info_from_t0file, t0file

	t0fileinfo = {detector:'', timestamparrays:['','']}

	Openr, lun, t0file, /GET_LUN
	READF, lun, t0fileinfo	
	close, lun
	Free_lun, lun

	timestamps = ['','']
	times = dblarr(2)
	for i=0,1 do begin 
		a = strsplit(t0fileinfo.timestamparrays[i], ' ', /extract)
		year = double(a[0])
		month = double(a[1])
		day = double(a[2])
		hour = double(a[3])
		minute = double(a[4])
		second = double(a[5])
		micro = double(a[6])
		timestamps[i]= string(format='(%"%4d-%02d-%02d/%02d:%02d:%0.8f")', $
			year, month, day, hour, minute, second+double(micro*1e-6))
		
		times[i] = gettime(timestamps[i]) 
	endfor	

	t0info = {detector:t0fileinfo.detector, timestamparrays:t0fileinfo.timestamparrays, timestamps:timestamps, times:times}

	return, t0info

end
