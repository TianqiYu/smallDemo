import serial
import time, datetime
from xbee import ZigBee
from error_handle import log_error
def port_initialize(device):
# this one defines the port info of the coordinator
    try:
        #set up port info
        if device == 'mac':
            port = '/dev/tty.serial-AH03FIMG'
        elif device == 'pi':
            port = '/dev/ttyS0'
        elif device == 'pi1':
            try:
                port = '/dev/ttyUSB0'
            except:
                port = '/dev/ttyUSB1'
        else:
            port = 'COM3'
        baud_rate = 19200
        #connet serial port to zigbee moudle
        ser = serial.Serial(port , baud_rate)

        coor = ZigBee(ser, escaped=True)
        return coor
    except Exception as err:
        method = 'port_initialize()'
        log_error(method,err)
        # if pri_flag:
        #     print err
