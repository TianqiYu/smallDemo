from datetime import datetime
from app_process import display_temp, humidity_fun
from error_handle import log_error
from collections import defaultdict
xbee_list = { #list all the xbees we have in our lab and associate with there mac address
            '\x00\x13\xA2\x00\x40\xE4\x42\x61': 'E1',
            '\x00\x13\xA2\x00\x40\xD8\x72\x50': 'E2',
            '\x00\x13\xA2\x00\x40\xE4\x42\xAB': 'E3',
            '\x00\x13\xA2\x00\x40\xE9\x64\x30': 'E4',
            '\x00\x13\xA2\x00\x40\xE9\x64\x22': 'E5'
            }

def grab_sensor_data(coor, pri_flag):
#this funcation unpack the frame and reformat them for database
    try:
        data = defaultdict()
        response = coor.wait_read_frame() # xbee incoming message

        # in our case we only care about the sensor reading, so we use multiple if statement to filter other
        # messages
        if response['id'] != 'node_id_indicator': 
            if response['id'] == 'rx_io_data_long_addr':
                if response['source_addr_long'] != '\x00\x13\xA2\x00\x40\xE9\x64\x30':
                    frame_data = response['samples'][0]
                    data_temp = frame_data['adc-1']
                    brightness = frame_data['adc-2']
                    humidity = frame_data['adc-3']

                    humidity = 0 #humidity_fun(humidity, data_temp)
                    temp =  display_temp(data_temp)
                    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                    id_ = xbee_list[response['source_addr_long']]

                    data['temp'] = temp
                    data['id'] = id_
                    data['timestamp'] = timestamp
                    data['brightness'] = brightness
                    data['humidity'] = humidity
                    return data
                else:
                    return False
            else:
                return False
        else:
            return False
    except Exception as err:
        method = 'error @m_control method grab_sensor_data()'
        log_error(method,err)
        if pri_flag:
            print 'error @m_control method grab_sensor_data(): ',err
