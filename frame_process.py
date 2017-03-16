

def change_xbee_pins(coor, led_, switch, xbee_addr='\x00\x13\xA2\x00\x40\xE9\x64\x30'): 
	if led_ == 'green': # select led
		cmd = 'D2'
	else:
		cmd = 'D1'
	if switch == 'ON': # select switch
		para = '\x05'
	else:
		para = '\x04'
	coor.remote_at(# XBee API, these command are from Zigbee library doc or you can get them from xbee datasheet
					dest_addr_long=xbee_addr,
					frame_id= '\x01',
					command=cmd,
					parameter = para
					)
	coor.remote_at(# API
					dest_addr_long=xbee_addr,
					command='WR'
					)

# xbee.remote_at(
#     dest_addr='\x56\x78',
#     command='D2',
#     parameter='\x04')

# xbee.remote_at(
#     dest_addr='\x56\x78',
#     command='WR')
