def grab_analog_data(frame, pri_flag): 
#read raw temp date from 'IO data sample RX indicator'
    try:
        if pri_flag:
            print 'frame: ',frame
        if  frame['id'] == 'rx_io_data_long_addr' :
            data = frame['samples'][0]
            return data
        elif frame['id'] == 'remote_at_response':
            data = frame['parameter'][0]
            return data
        else:
            return -1, 0
    except Exception as err:
        return False

# def ni_detect(cmd): #cmd , [address, frame id, parameter]
#     address, cmd, parameter = cmd
#     print address.encode('hex'), cmd, parameter
#     response = coor.wait_read_frame()
#     if response['id'] = 'NI':
#         if response['source_addr_long'] == address:
#             coor.remote_at(# API
#                             dest_addr_long=address,
#                             frame_id= '\x01',
#                             command=cmd,
#                             parameter = parameter
#                             )
#             response = coor.wait_read_frame()
#             if response['id'] == 'status':
#                 if response['status'] == '\x00':
#                     return True
#                 else:
#                     return False
