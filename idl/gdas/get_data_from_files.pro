function get_data_from_files, files
	
	;concatenate data from all files
	time = []
	energy = []
	tb = []
	ta = []
	frame = []
	goodframes = []
	filename = []
	
	for i=0, n_elements(files)-1 do begin

		fname = files[i]
		data = get_data_from_file(fname)	

		;since data not uniform structure, must extract out 
		;rates and times before appending
	
		if ~ISA(data, /array) then continue

		time = [time, data.time]
		energy = [energy, data.energy]
		tb = [tb, data.tb] 
		ta = [ta, data.ta]
		frame = [frame, data.frame]
		goodframes = [goodframes, data.goodframes]
		filename = [filename, data.filename]

	endfor

	return, {time:time, energy:energy, tb:tb, ta:ta, frame:frame, goodframes:goodframes, filename:filename}

end
