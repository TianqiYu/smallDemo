
import time
from datetime import datetime
from sqlite_ import insert_db
from frame_process import grab_analog_data
from app_process import display_temp, humidity_fun
from bigquery_m import data_insert
from error_handle import log_error
xbee_list = {
                '\x00\x13\xA2\x00\x40\xE4\x42\x61': 'E1',
                '\x00\x13\xA2\x00\x40\xD8\x72\x50': 'E2',
                '\x00\x13\xA2\x00\x40\xE4\x42\xAB': 'E3',
                '\x00\x13\xA2\x00\x40\xE9\x64\x30': 'E4',
                '\x00\x13\xA2\x00\x40\xE9\x64\x22': 'E5'
            }

def grab_data(coor, pri_flag):
#this funcation unpack the frame and reformat them for database
    try:
        data = dict()
        # coor.remote_at(dest_addr_long=address,frame_id=b'\x01',command = 'IS')
        response = coor.wait_read_frame()
        if response['id'] != 'node_id_indicator':
            frame_data = grab_analog_data(response, pri_flag)
            data_temp = frame_data['adc-1']
            brightness = frame_data['adc-2']
            humidity = frame_data['adc-3']

            humidity = 0 #humidity_fun(humidity, data_temp)
            temp =  display_temp(data_temp)
            timestamp = datetime.now()#.strftime('%Y-%m-%dT%H:%M:%S')
            id_ = xbee_list[response['source_addr_long']]
            data['temp'] = temp
            data['id'] = id_
            data['timestamp'] = timestamp
            data['brightness'] = brightness
            data['humidity'] = humidity
            def print_var(pri_flag):
                if pri_flag:
                    print '-start,grab_data-'
                    print 'frame response: ',response
                    print '-' *20
                    print 'frame_data: ', frame_data
                    print 'temp: ', data_temp
                    print 'brightness: ', brightness
                    print 'humidity: ', humidity
                    print '-' *20
                    print xbee_list[response['source_addr_long']] #show the name of the source device
                    print 'Time: ', timestamp
                    print 'Temp: ', temp
                    print '-end,Sgrab_data-'
            sor_addr = response['source_addr_long'].encode('hex')
            sor_name = xbee_list[response['source_addr_long']]
            #store data to local database
            sql_data = [(sor_addr, sor_name, timestamp, temp, humidity,  brightness)]
            insert_db(sql_data)
            #store data to bigquery - google database
            return True, data
        else:
            return False, None
    except Exception as err:
        method = 'error @grab_data()'
        log_error(method,err)
        if pri_flag:
            print 'error at grab_data():',err
