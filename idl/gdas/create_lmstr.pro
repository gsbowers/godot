function create_lmstr, en, ta, tb
	
	n = n_elements(en)

	data = indgen(3*n, /long)
	
	data[indgen(n)*3+0] = en
	data[indgen(n)*3+1] = ta
	data[indgen(n)*3+2] = tb

	data = [n, data]

	;return lmstr
	return, ['!!!!!!!', string(data, format='(I0.0)')]

end
