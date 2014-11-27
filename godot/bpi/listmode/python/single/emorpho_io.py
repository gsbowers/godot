# release public
from __future__ import division
import ftdi
from ftdi import *
import time
import math
import os.path
from configobj import ConfigObj # to read .ini files


# module addresses
MA_CONTROLS   = 0; #!< Access eMorpho control registers
MA_STATISTICS = 1; #!< Access eMorpho statistics registers
MA_RESULTS    = 2; #!< Access eMorpho results registers (version, telemtry, calibration)
MA_HISTOGRAM  = 3; #!< Access eMorpho histogram memory
MA_TRACE      = 4; #!< Access eMorpho trace memory
MA_LISTMODE   = 5; #!< Access eMorpho list mode memory
MA_USER       = 6; #!< Access eMorpho user memory
MA_MA7        = 7; #!< Access eMorpho firmware module no. 7 memory (non-standard code)

def set_IS(IS, key, value):
	""" Use this function to avoid creating new keys in the IS dictionary because of a typo."""
	if key in IS:
		IS[key] = value
	else:
		a = 1/0 # for debugging, raise an exception
		
def make_req(cmd_data, default_request):
	"""Merge command data with comand defaults in case the input data list is shorter than expected or supported.
	Also handles the case where the command data list is longer than supported."""
	req = default_request #default record
	l_cmd = len(cmd_data)
	l_req = len(req)
	if(l_cmd)>= l_req:
		req = cmd_data[0:l_req]
	else:
		req[0:l_cmd] = cmd_data # replace the fields that were given
	return req

def write(ft245, sn, module, words_in):
	nmax = len(words_in) // 16;
	step = 16;
	words2ft245 = [0]*17
	words2ft245[0] = (module & 0xFF) * 0x100 + 1
	for n in range(nmax):
		if(n>0):
			words2ft245[0] = (module & 0xFF) * 0x100 # no address clear for subsequent writes
		for k in range(16):
			words2ft245[k+1] = words_in[k + n*step]
		ft245.write_data(sn, words2ft245)

	return 0

def read(ft245, sn="", module=0, num_bytes=32, bytes_per_datum=2):   
	PH = [(module & 0xFF) * 0x100 + 7] # short write, 2 bytes packet header only
	ft245.write_data(sn, PH)   # program the module to read from
	return ft245.read_data(sn, num_bytes, bytes_per_datum)

def cr2is(CR, ADC_sampling_rate):
	""" Convert control register values into instrument settings. This function defines the keys for IS"""
	if len(CR)<16:
		return dict()
	IS = dict() # We make IS a dictionary
	IS['fine_gain'] = int(CR[0])
	IS['baseline_threshold'] = int(CR[1]) & 0x03FF
	IS['pulse_threshold'] = int(CR[2]) & 0x03FF
	IS['hold_off'] = int(CR[3])
	IS['integration_time'] = int(CR[4])
	IS['roi_bounds'] = int(CR[5])
	IS['trigger_delay'] = int(CR[6]) & 0x03FF

	IS['dac_data'] = int(CR[7]) & 0xFFF;
	IS['HV'] = 3000.0/4096.0 * int(IS['dac_data']);

	IS['request'] = int(CR[8] + CR[9] * 0x10000);    #in units of 65536 adc_sampling clock cycles
	IS['ACQ_Time'] = 65536.0/ADC_sampling_rate * IS['request'];

	IS['pit'] = int(CR[10]);
	IS['put'] = int(CR[11]);

	# CR12
	val = int(CR[12]);
	IS['ecomp'] = val & 0xF;
	IS['pcomp'] = (val & 0xF0) >> 4;
	IS['gain_select'] = (val & 0xF00) >> 8;
	IS['lm_data_switch'] = (val & 0x1000) >> 12;

	# CR13
	val = int(CR[13]);
	IS['etout'] = val & 1;
	IS['ptout'] = int((val & 0x2) / 0x2);
	IS['suspend'] = int((val & 0x4) / 0x4);
	IS['segment'] = int((val & 0x8) / 0x8);
	IS['segment_enable'] = int((val & 0x10) / 0x10);
	IS['daq_mode'] = int((val & 0x20) / 0x20);
	IS['nai_mode'] = int((val & 0x40) / 0x40);
	IS['temperature_disable'] = int((val & 0x80) / 0x80);

	# CR14
	val = int(CR[14]);
	IS['opto_repeat_time'] = val & 0x1F;
	IS['opto_pulse_width'] = (val >> 5) & 0xF;
	IS['opto_pulse_sep'] = (val >> 9) & 0xF;
	IS['opto_trigger'] = (val >> 14) & 0x1;
	IS['opto_enable'] = (val >> 15) & 0x1;

	# CR15
	val = int(CR[15]);
	IS['clear_histogram']= val & 1;
	IS['clear_statistics'] = int((val & 0x2)/0x2);
	IS['clear_trace'] = int((val & 0x4)/0x4);
	IS['clear_list_mode'] = int((val & 0x8)/0x8);
	IS['program_hv'] = int((val & 0x10)/0x10);
	IS['ut_run'] = int((val & 0x20)/0x20);
	IS['write_nv'] = int((val & 0x40)/0x40);
	IS['read_nv'] = int((val & 0x80)/0x80);

	IS['ha_run'] = int((val & 0x200)/0x200);
	IS['vt_run'] = int((val & 0x400)/0x400);
	IS['trace_run'] = int((val & 0x800)/0x800);
	IS['lm_run'] = int((val & 0x1000)/0x1000);
	IS['rtlt'] = int((val & 0x6000)/0x2000);
	IS['run'] = int((val & 0x8000)/0x8000);

	return IS

def is2cr(IS, ADC_sampling_rate):

	CR = [0]*16
	CR[0] = int(IS['fine_gain']);
	CR[1] = int(IS['baseline_threshold']) & 0x03FF;
	CR[2] = int(IS['pulse_threshold']) & 0x03FF;
	CR[3] = int(IS['hold_off']);
	CR[4] = int(IS['integration_time']);
	CR[5] = int(IS['roi_bounds']);
	CR[6] = int(IS['trigger_delay']) & 0x03FF;

	dac_data = int(math.floor((4096.0/3000.0 * IS['HV'])+0.5)) & 0x0FFF;
	CR[7] = dac_data;

	IS['request'] = int(math.floor(IS['ACQ_Time'] * ADC_sampling_rate / 65536.0));
	CR[8] = int(IS['request']) & 0xFFFF;                # lower 16-bit word
	CR[9] = (int(IS['request'] & 0xFFFFFFFF)) >> 16;    # upper 16-bit word

	CR[10] = int(IS['pit']);
	CR[11] = int(IS['put']);

	val =  (int(IS['ecomp']) & 0xF) + ((int(IS['pcomp']) & 0xF) << 4) + ((int(IS['gain_select']) & 0xF) << 8);
	val += (int(IS['lm_data_switch']) & 0x1) << 12;
	CR[12] = val;

	val =  (int(IS['etout']) & 1) + (int(IS['ptout']) & 1) * 0x2 + (int(IS['suspend']) & 1) * 0x4 + (int(IS['segment']) & 1) * 0x8;
	val += (int(IS['segment_enable']) & 1) * 0x10 + (int(IS['daq_mode']) & 1) * 0x20 + (int(IS['nai_mode']) & 1) * 0x40;
	val += (int(IS['temperature_disable']) & 1) * 0x80;
	CR[13] = val;

	val  = (int(IS['opto_repeat_time']) & 0x1F) + ((int(IS['opto_pulse_width']) & 0xF) << 5);
	val += (int(IS['opto_pulse_sep']) & 0xF) << 9;
	val += ((int(IS['opto_trigger']) & 1) << 14) + ((int(IS['opto_enable']) & 1) << 15);
	CR[14] = val;

	# self-clearing bits first
	val =  (int(IS['clear_histogram']) & 1) + (int(IS['clear_statistics']) & 1) * 0x2 + (int(IS['clear_trace']) & 1) * 0x4;
	val += (int(IS['clear_list_mode']) & 1) * 0x8 + (int(IS['program_hv']) & 1) * 0x10 + (int(IS['ut_run']) & 1) * 0x20;
	val += (int(IS['write_nv']) & 1) * 0x40 + (int(IS['read_nv']) & 1) * 0x80;
	# sticky bits
	val += (int(IS['ha_run']) & 1) * 0x200 + (int(IS['vt_run']) & 1) * 0x400 + (int(IS['trace_run']) & 1) * 0x800;
	val += (int(IS['lm_run']) & 1) * 0x1000 + (int(IS['rtlt']) & 3) * 0x2000 + (int(IS['run']) & 1) * 0x8000;
	CR[15] = val;

	return CR; #!< convert instrument settings to control registers;

def apply_settings(ft245, sn, IS, ss_time=0): 
	""" ft245 contains the usb information for every attached emorpho,
	sn is the serial number, IS are the instrument settings,
	and ss_time is the soft-start time."""
	
	IS['program_hv'] = 1;  # always update the high-voltage dac
	if ss_time == 0:
		CR = is2cr(IS, ft245.adc_speed[ft245.sn_to_devnum(sn)]);   # convert settings to control registers
		write(ft245, sn, MA_CONTROLS, CR)
	else:
		ss_time /= 10.0
		hv_max = IS['HV']
		hv_step = (hv_max // 10)
		hv_min = hv_max - 10*hv_step
		#for hv in range(hv_min,hv_max+1,hv-step):
		for n in range(1,11,1):
			IS['HV'] = hv_min + n * hv_step
			CR = is2cr(IS, ft245.adc_speed[ft245.sn_to_devnum(sn)]);   # convert settings to control registers
			write(ft245, sn, MA_CONTROLS, CR)
			time.sleep(ss_time)
	# clear those bits that self-clear in the firmware
	IS['clear_histogram'] = 0;
	IS['clear_statistics'] = 0;
	IS['clear_trace'] = 0;
	IS['clear_list_mode'] = 0;
	IS['program_hv'] = 0;
	IS['ut_run'] = 0;
	IS['write_nv'] = 0;
	IS['read_nv'] = 0;
	return 0;    
	

# The IS dictionary holds the instrument settings
# for data transfer that is numerical only, we need to convert between the IS dictionary
# and the IS_val list.  A dictionary is not ordered, so val = [IS[k] for k in IS] won't work
def IS_to_IS_val(IS):
	"""Create a list from the values of IS in the order described in the documentation."""
	IS_val =  [IS['fine_gain'], IS['baseline_threshold'], IS['pulse_threshold']]
	IS_val += [IS['hold_off'], IS['integration_time'], IS['roi_bounds'], IS['trigger_delay']]
	IS_val += [IS['dac_data'], IS['pit'], IS['put'], IS['request'], IS['ecomp'], IS['pcomp']]
	IS_val += [IS['gain_select'], IS['lm_data_switch'], IS['etout'], IS['ptout'], IS['suspend']]
	IS_val += [IS['segment'], IS['segment_enable'], IS['daq_mode'], IS['nai_mode'], IS['temperature_disable']]
	IS_val += [IS['opto_repeat_time'], IS['opto_pulse_width'], IS['opto_pulse_sep'], IS['opto_trigger'] ]
	IS_val += [IS['opto_enable'], IS['clear_statistics'], IS['clear_histogram'], IS['clear_list_mode']]
	IS_val += [IS['clear_trace'], IS['ut_run'], IS['program_hv'], IS['read_nv'], IS['write_nv'] ]
	IS_val += [IS['ha_run'], IS['trace_run'], IS['vt_run'], IS['lm_run'], IS['rtlt'], IS['run'] ]
	IS_val += [IS['ACQ_Time'], IS['HV'] ]
	return IS_val

def IS_val_to_IS(IS_val):
	"""Create an IS dictionary from the IS_val list."""
	IS = dict()
	IS['fine_gain'] = IS_val[0];		IS['baseline_threshold'] = IS_val[1];
	IS['pulse_threshold'] = IS_val[2];	IS['hold_off'] = IS_val[3];
	IS['integration_time'] = IS_val[4];	IS['roi_bounds'] = IS_val[5];
	IS['trigger_delay'] = IS_val[6];	IS['dac_data'] = IS_val[7];
	
	IS['pit'] = IS_val[8];	IS['put'] = IS_val[9];	IS['request'] = IS_val[10];
	
	IS['ecomp'] = IS_val[11]; 		IS['pcomp'] = IS_val[12];
	IS['gain_select'] = IS_val[13];	IS['lm_data_switch'] = IS_val[14];
	
	IS['etout'] = IS_val[15];		IS['ptout'] = IS_val[16];	IS['suspend'] = IS_val[17];
	IS['segment'] = IS_val[18];		IS['segment_enable'] = IS_val[19];
	IS['daq_mode'] = IS_val[20];	IS['nai_mode'] = IS_val[21]; IS['temperature_disable'] = IS_val[22];
	
	IS['opto_repeat_time'] = IS_val[23];	IS['opto_pulse_width'] = IS_val[24];
	IS['opto_pulse_sep'] = IS_val[25];		IS['opto_trigger'] = IS_val[26];
	IS['opto_enable'] = IS_val[27];
	
	IS['clear_statistics'] = IS_val[28];
	IS['clear_histogram'] = IS_val[29];		IS['clear_list_mode'] = IS_val[30];
	IS['clear_trace'] = IS_val[31];			IS['ut_run'] = IS_val[32];
	IS['program_hv'] = IS_val[33];			IS['read_nv'] = IS_val[34]; IS['write_nv'] = IS_val[35];
	IS['ha_run'] = IS_val[36];		IS['trace_run'] = IS_val[37]; 		IS['vt_run'] = IS_val[38];
	IS['lm_run'] = IS_val[39];		IS['rtlt'] = IS_val[40]; 			IS['run'] = IS_val[41];
	IS['ACQ_Time'] = IS_val[42];	IS['HV'] = IS_val[43];
	return IS

# Read data from the eMorpho and put them in a form suitable to be sent back to the client

# get and set for various settings groups

def get_sr(ft245,sn):
	""" Returns the ADC sampling rate in samples per second (Hz); Not tied to a command """
	return ft245.adc_speed[ft245.sn_to_devnum(sn)]

def get_IS(ft245, sn):
	""" Returns the IS dictionary. It is not currently tied to a command,
	but used often in the functions below. """
	CR = read(ft245, sn, MA_CONTROLS, 32, 2)
	IS = cr2is(CR, get_sr(ft245,sn))
	return IS

def boot_all(ft245, settings_path):
	for sn in ft245.sn:
		boot(ft245, sn, settings_path)
	return 0

def boot(ft245, sn, settings_path):
	# step 1: boot from NV-Mem
	download_nvmem(ft245, sn)
	# step 2: read sn-specific settings file, if it exists
	settings_file = settings_path + sn + '.ini'
	if(os.path.isfile(settings_file)): # If the file exists, merge the instrument settings
		config = ConfigObj(settings_file)
		is_config = config['instrument settings'] # Section name is Instrument_Settings
		IS = get_IS(ft245, sn)
		for key in is_config: # overwrite IS settings with those read from file
			if key in IS: # only accept keys that are already in the IS dictionary
				IS[key] = float(is_config[key])
			
	# step 3: read a settings file that applies to all units
	settings_file = settings_path + 'all_sn.ini'
	if(os.path.isfile(settings_file)): # If the file exists, merge the instrument settings
		config = ConfigObj(settings_file)
		is_config = config['instrument settings'] # Section name is Instrument_Settings
		IS = get_IS(ft245, sn)
		for key in is_config: # overwrite IS settings with those read from file
			if key in IS: # only accept keys that are already in the IS dictionary
				IS[key] = float(is_config[key])
	# step 4: Apply seetings
	IS = get_IS(ft245, sn)
	apply_settings(ft245, sn, IS, ss_time=1.0) #ramp HV over 1 second
	get_status(ft245, sn) # to load the ADC sampling rate
	return 0

def get_is(ft245, sn):
	""" Returns a list of IS values in the order shown in the MDS reference. """
	IS = get_IS(ft245, sn)  # retrieve the current IS
	IS_val = IS_to_IS_val(IS)
	return IS_val

def set_is(ft245, sn, cmd_data):
	"""Receives an IS-values list, applies it to the eMorpho and returns a list of 44 values."""
	IS_val = make_req(cmd_data, get_is(ft245, sn)) # Merge current IS_val with given IS_val
	IS = IS_val_to_IS(IS_val) 		# create new IS dictionary
	apply_settings(ft245, sn, IS) 	# apply to emorpho
	IS_val = get_is(ft245, sn) 		# read back to check
	return IS_val
	
def get_gain(ft245, sn):
	sr = get_sr(ft245,sn) # ADC sampling rate
	IS = get_IS(ft245, sn)  # retrieve the current IS
	dg = IS['fine_gain'] * pow(2.0, -IS['ecomp']) * sr/40.0e6
	gain = [IS['HV'], IS['gain_select'], dg ]
	return gain

def set_gain(ft245, sn, cmd_data):
	gain = make_req(cmd_data, get_gain(ft245, sn))
	sr = get_sr(ft245, sn) # ADC sampling rate
	IS = get_IS(ft245, sn)
	set_IS(IS,'HV',gain[0])
	set_IS(IS,'gain_select',gain[1])
	dg = gain[2]
	fg = dg * 40.0e6/sr;
	ecomp = 0
	while fg<16384:
		fg *= 2; ecomp += 1
		#print fg, ecomp
		
	set_IS(IS,'fine_gain',fg);
	set_IS(IS,'ecomp',ecomp);	# set_IS(IS,'pcomp',ecomp);	
	CR = is2cr(IS, sr)
	apply_settings(ft245, sn, IS)
	gain = get_gain(ft245, sn)
	return gain

def get_dsp(ft245, sn):
	sr = get_sr(ft245,sn) # ADC sampling rate
	IS = get_IS(ft245, sn)
	put = IS['put']
	if(IS['nai_mode']==0):
		put = IS['put'] * 1.0e6/sr # convert to micro seconds
	
	roi_low  = (IS['roi_bounds'] & 0xFF) * 16;
	roi_high = (IS['roi_bounds'] &0xFF00)//0x100 * 16
	dsp = [IS['pulse_threshold'], IS['integration_time'] * 1.0e6/sr, IS['hold_off'] * 1.0e6/sr,\
		   put, IS['baseline_threshold'], IS['pit'] * 1.0e6/sr, IS['nai_mode'],\
		   roi_low, roi_high, IS['temperature_disable'], IS['suspend'] ]
	return dsp

def set_dsp(ft245, sn, cmd_data):
	dsp = make_req(cmd_data, get_dsp(ft245, sn))
	sr = get_sr(ft245, sn) # ADC sampling rate
	IS = get_IS(ft245, sn) # retrieve current IS dictionary (instrument settings)
	
	# convert dsp to IS
	set_IS(IS, 'pulse_threshold', dsp[0])
	set_IS(IS, 'integration_time', round(dsp[1] * sr/1.0e6))
	set_IS(IS, 'hold_off', round(dsp[2] * sr/1.0e6))
	
	set_IS(IS, 'nai_mode', dsp[6])
	set_IS(IS, 'put', dsp[3])
	if IS['nai_mode']==1:
		set_IS(IS, 'put', round(dsp[3] * sr/1.0e6))
	set_IS(IS,'baseline_threshold', dsp[4])
	set_IS(IS, 'pit', round(dsp[5] * sr/1.0e6))
	set_IS(IS, 'roi_bounds', dsp[7]//16 + 0x100*(dsp[8]//16))
	set_IS(IS, 'temperature_disable', dsp[9])
	set_IS(IS, 'suspend', dsp[10])
	
	CR = is2cr(IS, sr)
	apply_settings(ft245, sn, IS)
	dsp = get_dsp(ft245, sn)
	return dsp

def get_pulser(ft245, sn):
	""" Use the firmware pulser to drive an LED."""
	IS = get_IS(ft245, sn)
	pulser = [IS['opto_repeat_time'],	IS['opto_pulse_width'],	IS['opto_pulse_sep'],\
			  IS['opto_trigger'], IS['opto_enable'] ]
	return pulser

def set_pulser(ft245, sn, cmd_data):
	"""Program the paramaters controlling the firmware pulser"""
	pulser = make_req(cmd_data, get_pulser(ft245, sn))
	IS = get_IS(ft245, sn) # retrieve current IS dictionary (instrument settings)
	sr = get_sr(ft245, sn)
	set_IS(IS, 'opto_repeat_time', pulser[0]);
	set_IS(IS, 'opto_pulse_width', pulser[1])
	set_IS(IS, 'opto_pulse_sep', pulser[2]);
	set_IS(IS, 'opto_trigger', pulser[3])
	set_IS(IS, 'opto_enable', pulser[4])
	CR = is2cr(IS, sr)
	apply_settings(ft245, sn, IS)
	pulser = get_pulser(ft245, sn)
	return pulser
	
def get_autocal(ft245, sn):
	return ft245.autocal[ft245.sn_to_devnum(sn)]

def set_autocal(ft245, sn, data):
	if(len(data)>6):
		data = data[0:6]
	autocal = get_autocal(ft245, sn)
	autocal[0:len(data)] = data[:]
	ft245.autocal[ft245.sn_to_devnum(sn)] = autocal[:]
	
def get_params(ft245, sn):
	"""Return the four main parameter groups: gain, dsp, pulser and autocal."""
	gain	= get_gain(ft245, sn)
	dsp     = get_dsp(ft245, sn)
	pulser  = get_pulser(ft245, sn)
	autocal = get_autocal(ft245, sn)
	return gain, dsp, pulser, autocal

def read_nvmem(ft245, sn):
	IS = get_IS(ft245, sn) # retrieve current IS dictionary (instrument settings)
	set_IS(IS, 'read_nv', 1)
	apply_settings(ft245, sn, IS)
	time.sleep(0.02)
	nvmem = read(ft245, sn, MA_USER, 256, 2)
	return nvmem
	
def download_nvmem(ft245, sn):
	IS = get_IS(ft245, sn) # retrieve current IS dictionary (instrument settings)
	set_IS(IS, 'read_nv', 1)
	apply_settings(ft245, sn, IS)
	time.sleep(0.02)
	nvmem = read(ft245, sn, MA_USER, 256, 2)
	if(nvmem[0] == 0x8003): #checks for valid nvmem content (memory is not blank)
		CR = nvmem[1:17]
		write(ft245, sn, MA_CONTROLS, CR)
		autocal = nvmem[17:23]
		ft245.autocal[ft245.sn_to_devnum(sn)] = autocal[:]
	
	return nvmem

def update_nvmem(ft245, sn, data):
	CR = read(ft245, sn, MA_CONTROLS, 32, 2)
	autocal = ft245.autocal[ft245.sn_to_devnum(sn)]
	nvmem = [0]*128
	nvmem[0] = 0x8003
	nvmem[1:17] = CR[0:16]
	nvmem[17:23] = autocal[0:6]
	if(len(data)>64):
		data = data[0:64]
	nvmem[64:64+len(data)] =  data[:]
	nvmem = [int(d) for d in nvmem] # convert all to integer
	
	write(ft245, sn, MA_USER, nvmem)
	IS = get_IS(ft245, sn) # retrieve current IS dictionary (instrument settings)
	set_IS(IS, 'write_nv', 1)
	apply_settings(ft245, sn, IS)
	time.sleep(0.02)
	return nvmem

def string_to_nvmem(ft245, sn, data_string):
	CR = read(ft245, sn, MA_CONTROLS, 32, 2)
	autocal = ft245.autocal[ft245.sn_to_devnum(sn)]
	nvmem = [0]*128
	nvmem[0] = 0x8003
	nvmem[1:17] = CR[0:16]
	nvmem[17:23] = autocal[0:6]
	if(len(data_string)>128):
		data_string = data_string[0:128]
	data_bytes = [ord(c) for c in data_string]
	if len(data_bytes)%2 == 1:
		data_bytes += [32]  # add a padding blank
		
	n_max = len(data_bytes)//2
	data = []
	for n in range(n_max):
		data += [data_bytes[2*n] + 256*data_bytes[2*n+1]]
	
	nvmem[64:64+len(data)] =  data[:]
	nvmem = [int(d) for d in nvmem] # convert all to integer
	
	write(ft245, sn, MA_USER, nvmem)
	IS = get_IS(ft245, sn) # retrieve current IS dictionary (instrument settings)
	set_IS(IS, 'write_nv', 1)
	apply_settings(ft245, sn, IS)
	time.sleep(0.02)
	print nvmem
	return nvmem

def string_from_nvmem(ft245, sn):
	IS = get_IS(ft245, sn) # retrieve current IS dictionary (instrument settings)
	set_IS(IS, 'read_nv', 1)
	apply_settings(ft245, sn, IS)
	time.sleep(0.02)
	nvmem = read(ft245, sn, MA_USER, 256, 2)
	
	data_bytes = []
	for n in range(64,128,1):
		data_bytes += [ nvmem[n] & 0x00FF, (nvmem[n] & 0xFF00)//256]
	data_bytes = [ d if d>0 else 32 for d in data_bytes] # replace null-bytes with blanks
	data_string = ''.join(map(chr,data_bytes))
	
	return data_string
	

# Get Rates (2 banks of statistics counters + 4 external counters)
def get_rates(ft245, sn):
	sr = get_sr(ft245, sn) # ADC Sampling Rate
	raw_stats = read(ft245,sn,MA_STATISTICS,64,4)
	rates = [0]*52 # prepare output data
	if(raw_stats[0] == 0):
		rates[0:10] = [0]*10
	else:
		rates[0:4] = raw_stats[0:4]         # DAQ time clock ticks, events, triggers, dead time clock ticks (32-bit)
		rates[4] = raw_stats[1]             # histogrammed events, usually same as raw_stats[1]
		rates[5] = raw_stats[0] * 65536/sr  # acquisition time in seconds
		rates[6] = raw_stats[1] / rates[5]  # rate of histogrammed events
		rates[7] = raw_stats[2] / rates[5]  # rate of recognized triggers
		rates[8] = rates[7] / (1.0 - raw_stats[3]/raw_stats[0]) # estimated true pulse rate (taking the dead time into account)
		rates[9] = raw_stats[3]/raw_stats[0] # acquisition dead time fraction
	
	# Statistics associated with the second bank, when histogram bank splitting is enabled
	# reporting 0 otherwise
	if raw_stats[4] == 0:
		rates[10:20] = [0]*10
	else:
		rates[10:14] = raw_stats[4:8]       # DAQ time clock ticks, events, triggers, dead time clock ticks (32-bit)
		if(rates[10] == 0):
			rates[14:20] = [0]*6
		else:
			rates[14] = raw_stats[5]              # histogrammed events, usually same as raw_stats[1]
			rates[15] = raw_stats[4] * 65536/sr   # acquisition time in seconds
			rates[16] = raw_stats[5] / rates[15]  # rate of histogrammed events
			rates[17] = raw_stats[6] / rates[15]  # rate of recognized triggers
			rates[18] = rates[17] / (1.0 - raw_stats[7]/raw_stats[4]) # estimated true pulse rate (taking the dead time into account)
			rates[19] = raw_stats[7] * 65536/sr   # acquisition dead time in seconds
	
	# statistics for four additional counters (external digital pulse source); bank 0
	for n in range(4):
		if rates[5] == 0:
			rates[20+2*n] = 0    # Xctr_n events
			rates[21+2*n] = 0    # Xctr_n rate (cps)
		else:
			rates[20+2*n] = raw_stats[8+n]               # Xctr_n events
			rates[21+2*n] = raw_stats[8+n] / rates[5]    # Xctr_n rate (cps)
	# statistics for four additional counters (external digital pulse source); bank 1
	for n in range(4):
		if rates[15] == 0:
			rates[36+2*n] = 0	# Xctr_n events
			rates[37+2*n] = 0	# Xctr_n rate (cps)
		else:
			rates[36+2*n] = raw_stats[12+n]              # Xctr_n events
			rates[37+2*n] = raw_stats[12+n] / rates[15]  # Xctr_n rate (cps)
	return rates

# Get Rates (n banks of statistics counters )
def get_rates_b(ft245, sn, nb):
	sr = get_sr(ft245, sn) # ADC Sampling Rate
	raw_stats = read(ft245,sn,MA_STATISTICS,nb*16,4)
	rates = [0]*10*int(nb) # prepare output data
	
	for n in range(0,int(nb)):
		rates[0+10*n:4+10*n] = raw_stats[n*4:(n+1)*4]
		rates[4+10*n] = raw_stats[1+n*4]
		if raw_stats[4*n] != 0:
			rates[5+10*n] = raw_stats[0+4*n] * 65536/sr  # acquisition time in seconds
			rates[6+10*n] = raw_stats[1+4*n] / rates[5+10*n]  # rate of histogrammed events
			rates[7+10*n] = raw_stats[2+4*n] / rates[5+10*n]  # rate of recognized triggers
			rates[8+10*n] = rates[7] / (1.0 - raw_stats[3+4*n]/raw_stats[0+4*n]) # estimated true pulse rate (taking the dead time into account)
			rates[9+10*n] = raw_stats[3+4*n]/raw_stats[0+4*n] # acquisition dead time fraction
	
	return rates

# Read version, status and calibration data and report in a format to be sent to the client
def get_status(ft245, sn):
	raw_status = read(ft245,sn,MA_RESULTS,32)
	#print ', '.join(map(str, raw_status))
	CR = read(ft245,sn,MA_CONTROLS,32)
	sr = (raw_status[6] & 0xFF) * 1.0e6 # ADC sampling rate; samples per second (Hz)
	if sr == 0: # USB read failed => device was unplugged
		status = [0]*22
		status[0] = 21
		return status
	ft245.adc_speed[ft245.sn_to_devnum(sn)] = sr  # Update the ADC Sampling Rate (needed by cr2is, is2cr, etc)
	gain = (CR[12] // 0x100) & 0xF
	impedance = 100.0 + (gain & 1)*330.0 + (gain & 2)/2.0*1000.0
	impedance += (gain & 4)/4.0*3300.0 + (gain & 8)/8.0*10000.0
	max_ADC = 1024.0;  #  All on a 10-bit scale.  Extra bits are fractional.
	ADC_voltage_range = 1.056;
	
	dc_val = raw_status[1] / 64     # DC-val; unit is 1.056mV where full-scale is 1024*1.056mV.
	dI = ADC_voltage_range / max_ADC / impedance; # Anode current per 10-bit ADC bin; in Ampere
	dQ = dI / sr      # Charge per 10-bit ADC bin and clock cycle; in Coulomb
	d_mca_Q = dQ * (CR[12] & 0xF) / 2.0 * CR[0]/32768 # Charge per MCA bin in Coulomb
	
	status = [0]*22 # prepare output data
	status[0]  = raw_status[7] & 0xFF;  #!< Firmware version
	status[1]  = raw_status[8]          #!< Customization number
	status[2]  = raw_status[9]          #!< Build number; increases with every release
	status[3]  = (raw_status[7] // 256) & 0xF # number of ADC bits
	status[4]  = sr                     # ADC sampling rate; samples per second (Hz)
	status[5]  = dc_val                 # DC-val; unit is 1.056mV where full-scale is 1023*1.056mV.
	val        = raw_status[0]
	if val & 0x1000: # temperature is negative
		val = (val & 0x01FFF)-8192
	else:
		val = val & 0x07FF
	status[6]  = val / 16               # Temperature in deg. C
	status[7]  = raw_status[5]          # Average energy deposited in the region of interest; reported as 16 times the average MCA bin.
		
	if(raw_status[4] & 0x1000):  # Test for sign bit; Negative numbers mean zero current (just noise)
		status[8] = 0
	else:
		status[8] = (raw_status[3]+ 0x10000 * raw_status[4])* dI * pow(2.0, -15.0)
									 
	status[9] = (CR[15] & 0x8000) // 0x8000  # run active
	
	status[10] = raw_status[2] & 0x1        # histogram done
	status[11] = (raw_status[2] & 0x4) // 4 # trace done
	status[12] = (raw_status[2] & 0x2) // 2 # listmode done
	
	status[13] = impedance # Input amplifier transimpedance in Ohms
	status[14] = max_ADC - dc_val
	status[15] = status[14] / 1000 * ADC_voltage_range / impedance # Maximum measurable anode pulse current before going out of range
	status[16] = dQ # Charge unit: delta_T * delta_I
	status[17] = dI # Current unit: PMT-anode current per ADC bin (ie per mV)
	status[18] = d_mca_Q # Charge unit per MCA bin: delta_q, in Coulomb
	
	# Battery monitor
	status[19] = raw_status[10] * 3.3/4096 * 2
	status[20] = (raw_status[11] - 2047) * 3.3/4096 / 5.0 / 0.15 # Current in Ampere, R_measure=0.15_Ohms
	
	# LED average
	status[21] = raw_status[12]
	return status

# Commands to perform data acquisition

def start_mca(ft245, sn, cmd_record):
	"""Receives a start_mca record and restarts DAQ."""
	adc_sr = get_sr(ft245, sn)
	CR = read(ft245, sn, MA_CONTROLS, 32, 2)
	IS = cr2is(CR, adc_sr)
	req = make_req(cmd_record, [IS['ACQ_Time'], IS['rtlt'], IS['ha_run'], 1, 1, IS['segment_enable'], 1]) # Merge command and defaults as needed
		
	set_IS(IS, 'ACQ_Time', req[0])
	set_IS(IS, 'rtlt', req[1])
	set_IS(IS, 'ha_run', req[2])
	set_IS(IS, 'clear_histogram', req[3])
	set_IS(IS, 'clear_statistics', req[4])
	set_IS(IS, 'segment_enable', req[5])
	set_IS(IS, 'run', req[6])
	apply_settings(ft245, sn, IS)
	return 0

def start_trace(ft245, sn, cmd_data):
	adc_sr = get_sr(ft245, sn)
	CR = read(ft245, sn, MA_CONTROLS, 32, 2)
	IS = cr2is(CR, adc_sr)
	req = make_req(cmd_data, [0, IS['trigger_delay']]) # Merge command and defaults as needed
	set_IS(IS, 'trigger_delay', req[1])
	if(req[0] == 0): # untriggered trace
		set_IS(IS, 'ut_run', 1)
		set_IS(IS, 'trace_run', 0)
		set_IS(IS, 'vt_run', 0)
	if(req[0] == 1): # triggered trace
		set_IS(IS, 'ut_run', 0)
		set_IS(IS, 'trace_run', 1)
		set_IS(IS, 'vt_run', 0)
	if(req[0] == 2): # validated and triggered trace
		set_IS(IS, 'ut_run', 0)
		set_IS(IS, 'trace_run', 0)
		set_IS(IS, 'vt_run', 1)
	set_IS(IS, 'clear_trace', 1)
	set_IS(IS, 'run', 1)
	apply_settings(ft245, sn, IS)
	
	return 0

def trace_summary(trace, IS, adc_sr):
	try:
		thr = IS['pulse_threshold']
		b_thr = IS['baseline_threshold']
		dc_val = trace[0]
		for n,t in enumerate(trace[1:]):
			if abs(t-dc_val)<b_thr:
				dc_val = 7/8*dc_val + t/8
			elif (t-dc_val) > thr:
				break
		else: # no pulse found
			tlen = len(trace)
			avg = sum(trace)/tlen 
			std_dev = sum([(t-avg)**2/(tlen-1) for t in trace])
			mini = min(trace)
			maxi = max(trace)
			return [adc_sr, -1, 0, 0, maxi, mini, std_dev, avg]
		
		delay = n+1 # trigger point
		tlen = len(trace)
		it = IS['integration_time']
		n0 = min(0,delay-8)
		n1 = max(min(0,delay-8+it),tlen-1)
		pulse = [t-dc_val for t in trace[n0:n1]]
		energy = sum(pulse)
		mca_bin = 32*(energy * IS['fine_gain']*pow(2.0, -IS['ecomp'])) // (16*32768)
		
		ymax = max(pulse)
		xmax = pulse.index(ymax)
		
		y10 = 0.1*ymax
		y50 = 0.5*ymax
		y90 = 0.9*ymax
		
		p10 = [idx for idx,p in enumerate(pulse) if p>y10]
		xrise10 = p10[0]  + n0
		xfall10 = p10[-1] + n0
		
		p90 = [idx for idx,p in enumerate(pulse) if p>y90]
		xrise90 = p90[0]  + n0
		xfall90 = p90[-1] + n0
			
		rise_time = (xrise90 - xrise10)/adc_sr
		fall_time = (xfall10 - xfall90)/adc_sr
		peaking_time = (xmax - delay)/adc_sr
		
		p50 = [idx for idx,p in enumerate(pulse) if p>y50]
		fwhm = (p50[-1] - p50[0])/adc_sr
		
		results = [adc_sr, mca_bin, ymax/32, rise_time, peaking_time, fall_time, fwhm, dc_val/32]
	except:
		results = [adc_sr, 0, 0, 0, 0, 0, 0, 0]
	#print ', '.join(map(str, results))
	
	return results
	
def start_lm(ft245, sn, cmd_data):
	"""Receives command data list and starts a single listmode run."""
	adc_sr = get_sr(ft245, sn)
	CR = read(ft245, sn, MA_CONTROLS, 32, 2)
	IS = cr2is(CR, adc_sr)
	req = make_req(cmd_data, [IS['lm_data_switch'], IS['clear_statistics']]) # Merge command and defaults as needed
	set_IS(IS, 'lm_data_switch', req[0])
	set_IS(IS, 'lm_run', 1)
	set_IS(IS, 'clear_list_mode', 1)
	set_IS(IS, 'clear_statistics', req[1])
	set_IS(IS, 'run', 1)
	apply_settings(ft245, sn, IS)
	return 0

def clear_list_mode(ft245, sn):
	"""Just clear list mode """
	adc_sr = get_sr(ft245, sn)
	CR = read(ft245, sn, MA_CONTROLS, 32, 2)
	IS = cr2is(CR, adc_sr)
	set_IS(IS, 'clear_list_mode', 1)
	apply_settings(ft245, sn, IS)
	return 0

def exit_mds():
	sys.exit()

