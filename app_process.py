import time, datetime
from error_handle import log_error

def display_temp(raw_data): #read raw temp date from 'IO data sample RX indicator'
# calculate the temperature by using formula from the sensor data sheet
    try:
        temp = raw_data/1023.0 * 1200 #the unit is voltage, so we need to multiply 1000 to turn it to mv
        temp = temp / 10 #this set comes from the LM35 output formula,its in F
        temp = (temp - 32) *(5/9.0)
        return round(temp,2)
    except Exception as err:
        method = '@app_process module has display_temp error: '
        log_error(method,err)
        # print 'error at display_temp():',err
        
def humidity_fun(raw_data, temp): #read raw temp date from 'IO data sample RX indicator'
# calculate the temperature by using formula from the sensor data sheet
    try:
        supplyVolt = 3300
        voltage = raw_data/1023.0 * 1200
        sensorRH =  (voltage/supplyVolt-0.1515)/0.00636
        trueRH = sensorRH / (1.0546 - 0.00216 * temp)
        # print "Vout: %f, RH: %f" % voltage, sensorRH
        return round(sensorRH, 2)
    except Exception as err:
        method = '@app_process module has humidity_fun: '
        log_error(method,err)
