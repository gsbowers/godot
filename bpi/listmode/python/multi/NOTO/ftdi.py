import os
import time
from  ctypes import *
import ctypes
import sys

#Interface between the API programmed in C and
#the python code.  Since complex objects, such
#as classes and structures don't travel well
#across such an interface, we only use variables
#and arrays.
#
#
#  We use ctypes to make the connection between
#python variables and C-variables.
LIBUSB_HAS_GET_DRIVER_NP = sys.platform.startswith('linux')

USE_WIN32 = sys.platform.startswith('win32') # rturns TRUE or FALSE

if sys.platform.startswith('linux'):
	w_dir=str(sys.path[0])
	print w_dir+"/lib/libusb.so"
	#Use the following two lines for linux
	cdll.LoadLibrary(w_dir+"/lib/libusb.so") 
	libusb0=CDLL(w_dir+"/lib/libusb.so")
	_PATH_MAX=4096

elif sys.platform.startswith('win32'):
	#Use the following two line for windows
	w_dir=str(sys.path[0])
	#print w_dir+"\lib\libusb0_x86.dll"
	#cdll.LoadLibrary(w_dir+"\lib\libusb0_x86.dll")
	#libusb0=CDLL(w_dir+"\lib\libusb0_x86.dll")
	cdll.LoadLibrary("C:\Windows\System32\libusb0.dll")
	libusb0=CDLL("C:\Windows\System32\libusb0.dll")
	_PATH_MAX=511
	
# libusb-win32 makes all structures packed, while
# default libusb only does for some structures
# _PackPolicy defines the structure packing according
# to the platform.

class _PackPolicy(object):
	pass

if sys.platform == 'win32' or sys.platform == 'cygwin':
	_PackPolicy._pack_ = 1
	
class _usb_descriptor_header(Structure):
	_pack_ = 1
	_fields_ = [('blength', c_uint8),
				('bDescriptorType', c_uint8)]

class _usb_string_descriptor(Structure):
	_pack_ = 1
	_fields_ = [('bLength', c_uint8),
				('bDescriptorType', c_uint8),
				('wData', c_uint16)]

class _usb_endpoint_descriptor(Structure, _PackPolicy):
	_fields_ = [('bLength', c_uint8),
				('bDescriptorType', c_uint8),
				('bEndpointAddress', c_uint8),
				('bmAttributes', c_uint8),
				('wMaxPacketSize', c_uint16),
				('bInterval', c_uint8),
				('bRefresh', c_uint8),
				('bSynchAddress', c_uint8),
				('extra', POINTER(c_uint8)),
				('extralen', c_int)]

class _usb_interface_descriptor(Structure, _PackPolicy):
	_fields_ = [('bLength', c_uint8),
				('bDescriptorType', c_uint8),
				('bInterfaceNumber', c_uint8),
				('bAlternateSetting', c_uint8),
				('bNumEndpoints', c_uint8),
				('bInterfaceClass', c_uint8),
				('bInterfaceSubClass', c_uint8),
				('bInterfaceProtocol', c_uint8),
				('iInterface', c_uint8),
				('endpoint', POINTER(_usb_endpoint_descriptor)),
				('extra', POINTER(c_uint8)),
				('extralen', c_int)]

class _usb_interface(Structure, _PackPolicy):
	_fields_ = [('altsetting', POINTER(_usb_interface_descriptor)),
				('num_altsetting', c_int)]

class _usb_config_descriptor(Structure, _PackPolicy):
	_fields_ = [('bLength', c_uint8),
				('bDescriptorType', c_uint8),
				('wTotalLength', c_uint16),
				('bNumInterfaces', c_uint8),
				('bConfigurationValue', c_uint8),
				('iConfiguration', c_uint8),
				('bmAttributes', c_uint8),
				('bMaxPower', c_uint8),
				('interface', POINTER(_usb_interface)),
				('extra', POINTER(c_uint8)),
				('extralen', c_int)]

class _usb_device_descriptor(Structure, _PackPolicy):
	_pack_ = 1
	_fields_ = [('bLength', c_uint8),
				('bDescriptorType', c_uint8),
				('bcdUSB', c_uint16),
				('bDeviceClass', c_uint8),
				('bDeviceSubClass', c_uint8),
				('bDeviceProtocol', c_uint8),
				('bMaxPacketSize0', c_uint8),
				('idVendor', c_uint16),
				('idProduct', c_uint16),
				('bcdDevice', c_uint16),
				('iManufacturer', c_uint8),
				('iProduct', c_uint8),
				('iSerialNumber', c_uint8),
				('bNumConfigurations', c_uint8)]

class _usb_device(Structure, _PackPolicy):
	pass

class _usb_bus(Structure, _PackPolicy):
	pass

_usb_device._fields_ = [('next', POINTER(_usb_device)),
						('prev', POINTER(_usb_device)),
						('filename', c_int8 * (_PATH_MAX + 1)),
						('bus', POINTER(_usb_bus)),
						('descriptor', _usb_device_descriptor),
						('config', POINTER(_usb_config_descriptor)),
						('dev', c_void_p),
						('devnum', c_uint8),
						('num_children', c_ubyte),
						('children', POINTER(POINTER(_usb_device)))]

_usb_bus._fields_ = [('next', POINTER(_usb_bus)),
					('prev', POINTER(_usb_bus)),
					('dirname', c_char * (_PATH_MAX + 1)),
					('devices', POINTER(_usb_device)),
					('location', c_uint32),
					('root_dev', POINTER(_usb_device))]

_usb_dev_handle = c_void_p

libusb0.usb_get_busses.restype = ctypes.POINTER(_usb_bus)
libusb0.usb_get_busses.argtypes = []

libusb0.usb_open.restype = _usb_dev_handle
libusb0.usb_open.argtypes = [ctypes.POINTER(_usb_device)]

libusb0.usb_get_string_simple.argtypes = [_usb_dev_handle, c_int, c_char_p, c_size_t ]

if(LIBUSB_HAS_GET_DRIVER_NP):
	libusb0.usb_detach_kernel_driver_np.argtypes = [_usb_dev_handle, c_int]

libusb0.usb_set_configuration.argtypes = [_usb_dev_handle, c_int]
libusb0.usb_claim_interface.argtypes = [_usb_dev_handle, c_int]
libusb0.usb_control_msg.argtypes =\
	[_usb_dev_handle, c_int, c_int, c_int, c_int, c_char_p, c_int, c_int]

libusb0.usb_close.argtypes = [_usb_dev_handle]

libusb0.usb_bulk_read.argtypes =\
	[_usb_dev_handle,c_int,c_char_p,c_int,c_int]
	
libusb0.usb_bulk_write.argtypes =\
	[_usb_dev_handle,c_int,c_char_p,c_int,c_int]
			

#FT245 chip control I/O requests
SIO_SET_LATENCY_TIMER_REQUEST=0x9
SIO_GET_LATENCY_TIMER_REQUEST=0xA
SIO_READ_EEPROM_REQUEST=0x90
SIO_WRITE_EEPROM_REQUEST=0x91
SIO_ERASE_EEPROM_REQUEST=0x92

SIO_RESET_REQUEST=0x0

SIO_RESET_SIO=0x0
SIO_RESET_PURGE_RX=0x1
SIO_RESET_PURGE_TX=0x2
	
class ft245:
	def __init__(self):
		self.max_packet_size = 64
		self.in_ep  = 0x02  #!< writing to the FT245
		self.out_ep = 0x81  #!< reading from the FT245
		self.usb_read_timeout=1000
		self.usb_write_timeout=1000
		self.ftdi_vid=0x0403;
		self.bpi_vid=0x1FA4;
		self.morpho_pid=0x6001;
		self.use_only_bpi_vid = False;
		self.devices=list()
		self.handles=list()
		self.adc_speed=list()
		self.sn=list()

	def init(self):
		self.max_packet_size = 64
		self.in_ep  = 0x02  #!< writing to the FT245
		self.out_ep = 0x81  #!< reading from the FT245
		self.usb_read_timeout=1000
		self.usb_write_timeout=1000
		self.ftdi_vid=0x0403;
		self.bpi_vid=0x1FA4;
		self.morpho_pid=0x6001;
		self.use_only_bpi_vid = False;
		self.devices=list()
		self.handles=list()
		self.adc_speed=list()
		self.sn=list()
		
	def scan_all(self, bpi_only):
		"""Scans for morphos and count them; Does not open a Morpho."""
		libusb0.usb_init();
		libusb0.usb_find_busses()
		libusb0.usb_find_devices()
		bus = libusb0.usb_get_busses() # get won't work without the find's above
		count = 0
		while(bool(bus)):
			dev = bus[0].devices
			while (bool(dev)):
				vid = dev[0].descriptor.idVendor
				pid = dev[0].descriptor.idProduct
				ok = (vid == 0x1FA4 and pid == 0x6001) # find emorpho with BPI VID
				if( not bpi_only):
					ok = ok or (vid == 0x0403 and pid == 0x6001) # find emorpho with FTDI VID
				if ok:
					count +=1 
				dev = dev[0].next
			bus = bus[0].next
		return count

	def find_all(self, bpi_only):
		libusb0.usb_init();
		libusb0.usb_find_busses()
		libusb0.usb_find_devices()
		bus = libusb0.usb_get_busses() # get won't work without the find's above
		count = 0
		while(bool(bus)):
			dev = bus[0].devices
			while (bool(dev)):
				vid = dev[0].descriptor.idVendor
				pid = dev[0].descriptor.idProduct
				ok = (vid == 0x1FA4 and pid == 0x6001) # find emorpho with BPI VID
				if( not bpi_only):
					ok = ok or (vid == 0x0403 and pid == 0x6001) # find emorpho with FTDI VID
				if ok:
					self.devices.append(dev)
				dev = dev[0].next
			bus = bus[0].next
			
		print "number of eMorphos: ",len(self.devices)
		if len(self.devices) == 0:
			return -1
	
		self.handles = list()
		self.sn = list()
		dev = self.devices[0]
		offset = dev[0].descriptor.iSerialNumber
                print "Offset: ",offset
		for dev in self.devices:
			handle = libusb0.usb_open(dev)
			self.handles.append(handle) # open and store handle
			sn_char = create_string_buffer('\000'*16)
			libusb0.usb_get_string_simple(handle, offset, sn_char, 16)
                        print offset, "x",ctypes.string_at(sn_char),"x"
			ser_num = ''.join(sn_char).split(b'\0',1)[0] # treat first null-byte as stop character
			self.sn.append(ser_num)
                print "handles: ",self.handles
                print "sn: ",self.sn
		# After the open, we need to detach the linux kernel driver
		# and claim the interface
		for dev_num in range(len(self.devices)):
			if(LIBUSB_HAS_GET_DRIVER_NP):
				libusb0.usb_detach_kernel_driver_np(self.handles[dev_num], 0)
	
			if(USE_WIN32): # for ft245 config_value = 1 always
				#if(self.devices[dev_num][0].descriptor.bNumConfigurations > 0):
				#	config_val = self.devices[dev_num][0].config[0].bConfigurationValue
				#	print "configuration value = ",config_val
				#	if(config_val < 0):
				#		return -1
				#	libusb0.usb_set_configuration(self.handles[dev_num], config_val)
				libusb0.usb_set_configuration(self.handles[dev_num], 1)

			libusb0.usb_claim_interface(self.handles[dev_num],0)

			# now reset the device
			libusb0.usb_control_msg(
				self.handles[dev_num], 64,0, 0, 0, c_char_p(0), 0, self.usb_write_timeout)

			latency = 2; # set 2ms minimum in all devices
			self.set_latency_timer(latency)

		# now sort handles, serial numbers and other unit-specific values
		num_devices = len(self.handles)
		sn_hndl = zip(self.sn, self.handles)
		sn_hndl_sorted = sorted(sn_hndl, key=lambda sn: sn[0]) # sort opened emorphos by serial number
		self.sn2devnum = dict()
		for n in range(num_devices):
			self.sn[n] = sn_hndl_sorted[n][0]
			self.handles[n] = sn_hndl_sorted[n][1]
			self.sn2devnum[self.sn[n]] = n  # Now build the S/N to dev num dictionary
			print "S/N: ",self.sn[n]
	
	# preset default values for lists and values that are stored within the ft245 class
		self.adc_speed = [40.0e6] * num_devices  # a default value
		ac_list = [3.0, 1.0, 350, 1200, 661.62, 12]
		self.autocal = list()
		for n in range(num_devices):
			self.autocal.append(ac_list) 
	
		return 0

	# close all open devices
	def close(self):
		for handle in self.handles:
			libusb0.usb_close(handle);
		self.handles = [] # now an empty list
		self.devices = [] # now an empty list
		return 0;
	
	# controls
	
	# set latency timer in all devices
	def set_latency_timer(self, latency):
		latency = latency & 0xFF; # only lower byte is valid
		for handle in self.handles:
			libusb0.usb_control_msg(handle, 64,
							SIO_SET_LATENCY_TIMER_REQUEST,
							latency, 0, c_char_p(0), 0, self.usb_write_timeout);
		return 0;
	
	def sn_to_devnum(self, sn):
		""" Find the ordinal number of the unit.
		If sn is an empty string, we use devnum=0 as the default.
		If a serial number can't be found, we return devum=-1"""
		if len(sn)>0:
			if sn in self.sn2devnum:
				devnum = self.sn2devnum[sn]
			else:
				devnum = -1
		else:
			devnum = 0
		return devnum
	
	# purge receive buffer in enumerated device
	def purge_rx_buffer(self, sn):
		dev_num = self.sn_to_devnum(sn)
		handle = self.handles[dev_num]
		ret = libusb0.usb_control_msg(handle, 64,
							SIO_RESET_REQUEST, SIO_RESET_PURGE_RX,
							0, c_char_p(0), 0, self.usb_write_timeout);
		return ret;
	
	# read byte data from device dev_num
	def read_data(self, sn, num_bytes, bytes_per_datum):
		dev_num = self.sn_to_devnum(sn)
		read_bytes = int(((num_bytes + 256)//62 + 1)*64)
		char_buf = create_string_buffer('\000'*read_bytes)
		handle = self.handles[dev_num]
		self.purge_rx_buffer(sn)
		ret = libusb0.usb_bulk_read (
				handle, self.out_ep, char_buf, read_bytes, self.usb_read_timeout);
		
		# Remove the modem status bytes
		bytes_out = []
		for n in range(read_bytes):
			if( (n%64 == 0) or (n%64 == 1) ): continue;
			bytes_out.append(char_buf[n])

		# Combine bytes into data words (16=bit or 32-bit)
		data_out = []
		if(bytes_per_datum == 2):
			for n in range(int(num_bytes//2)): # '//' is the floor division operator
				data_out.append(ord(bytes_out[2*n+256]) + 0x100 * ord(bytes_out[2*n+257]))
				
		if(bytes_per_datum == 4):
			for n in range(int(num_bytes//4)): # '//' is the floor division operator
				data_out.append(ord(bytes_out[4*n+256]) + 0x100 * ord(bytes_out[4*n+257]) +
								0x10000*ord(bytes_out[4*n+258]) + 0x1000000 * ord(bytes_out[4*n+259]))

		return data_out;
	
	# write data to emorpho dev_num
	def write_data(self, sn, words_in):
		num_words = len(words_in)
		dev_num = self.sn_to_devnum(sn)
		handle = self.handles[dev_num]
		buf = create_string_buffer('\000'*(num_words*2-1))
		for n in range(num_words):
			buf[2*n]   = chr(words_in[n] % 0x100);
			buf[2*n+1] = chr(words_in[n] // 0x100);
		ret = libusb0.usb_bulk_write(handle, self.in_ep, buf, num_words*2,
									self.usb_write_timeout);
		#wr_buf = [ord(buf[n]) for n in range(num_bytes)]
		#print "write buffer = ", wr_buf
		return ret;

	# read the eeprom of emorpho number dev_num
	def read_eeprom(self, sn):
		dev_num = self.sn_to_devnum(sn)
		val = c_int16(0)
		ret = 0
		handle = self.handles[dev_num]
		for n in range(64):
			ret += usb_control_msg(
				handle, FTDI_DEVICE_IN_REQTYPE,
				SIO_READ_EEPROM_REQUEST, 0,
				n, byref(val), 2, self.usb_read_timeout);
			eeprom[n] = val
	
		return eeprom
	
	# write eeprom for emorpho number dev_num
	def write_eeprom(self, sn, eeprom):
		dev_num = self.sn_to_devnum(sn)
		handle = self.handles[dev_num]
		self.set_latency_timer(0x77) # writing to the eeprom takes time
		for n in range(64):
			usb_val = eeprom[2*n] + 0x100 * eeprom[2*n+1]; # low-byte first
			ret = usb_control_msg(
				handle, FTDI_DEVICE_OUT_REQTYPE,
				SIO_WRITE_EEPROM_REQUEST, usb_val, n,  # n fills the index slot.
				NULL, 0, self.usb_write_timeout);
	
		libusb0.set_latency_timer(2);
		return 0;
	
