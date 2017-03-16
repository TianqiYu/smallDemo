import serial
from xbee import ZigBee
from error_handle import log_error

def port_initialize(device):
# this one defines the port info of the coordinator
    try:
        #set up port info
        if device == 'mac': # select port name
            port = '/dev/tty.usbserial-DN018QQK'
        elif device == 'pi':
            port = '/dev/ttyS0'
        elif device == 'pi1':
            try:
                port = '/dev/ttyUSB0'
            except:
                port = '/dev/ttyUSB1'
        else:
            port = 'COM3'
        baud_rate = 19200 # baud_rate of USB/serial
        #connect serial port to zigbee module

        ser = serial.Serial(port , baud_rate)
        ser.reset_input_buffer() # clear port 
        ser.reset_output_buffer()
        coor = ZigBee(ser, escaped=True) #connect port with Xbee module, then we can control xbee by this interface
        return coor
    except Exception as err:
        method = 'error @initial_port module: port_initialize()'
        log_error(method,err)

