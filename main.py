# import RPi.GPIO as GPIO

# below is the imports for xbee
import serial, time
from datetime import datetime
import time
from xbee import ZigBee


from initial_port import port_initialize
from frame_process import change_xbee_pins
from m_control import grab_sensor_data
from error_handle import log_error

import matplotlib.pyplot as plt #import matplotlib library
from drawnow import *
plt.style.use('fivethirtyeight')



# from incoming_data_plot import
class xbeeModule(object):
	def __init__(self, pri_flag=False):
		self.coor = None
		self.pri_flag = pri_flag
		self.error_cnt = 0


	def start_(self):

		plt.clf() # clear the plot buffer
		temp_1 = [] #put plot value 
		temp_2 = [] #put plot value 
		plt.ion() #Tell matplotlib you want interactive mode to plot live data
		g_cnt, b_cnt=0, 0

		def makeFig(): #this function set up the plot parameters such as axis, legend and label
			plt.ylim(15,40)                                 #Set y min and max values
			plt.title('Live Streaming Sensor Data')      #Plot the title
			plt.grid(True)                                  #Turn the grid on
			plt.ylabel('E1-Green led')                            #Set ylabels
			plt.plot(temp_1, 'go-', label='E1 Degree')       #plot the temperature
			plt.legend(loc='upper left')                    #plot the legend

			plt2=plt.twinx()                                #Create a second y axis
			plt.ylim(15,40)                           #Set limits of second y axis- adjust to readings you are getting
			plt2.plot(temp_2, 'b^-', label='E2 Degree') #plot pressure data
			plt2.set_ylabel('E2-Blue led')                    #label second y axis
			plt2.ticklabel_format(useOffset=False)           #Force matplotlib to NOT autoscale y axis
			plt2.legend(loc='upper right')                  #plot the legend

		self.coor = port_initialize('mac')

		while True:
			data = grab_sensor_data(self.coor, self.pri_flag) #read sensor unit data
			threshold = 21 #led control threshold
			try:
				if data != False: # if get valid sensor readings
					print data # data is a python dictionary 
					if data['id']=='E1': # get sensor data id
						temp_1.append(data['temp']) # put data to live data list to plot
						g_cnt=g_cnt+1 # first parameter counter for live data 
						if data['temp'] > threshold:
							change_xbee_pins(self.coor, 'green', switch='ON') # turn on led
						else:
							change_xbee_pins(self.coor, 'green', switch='off') # turn off led

					if data['id']=='E2':
						temp_2.append(data['temp'])  # put data to live data list to plot
						b_cnt=b_cnt+1
						if data['temp'] > threshold:
							change_xbee_pins(self.coor, 'blue', switch='ON')
						else:
							change_xbee_pins(self.coor, 'blue', switch='off')
								   
					drawnow(makeFig) #live plot                     
					plt.pause(.000001) #pause after each plot otherwise system would raise some errors                 
					if(g_cnt>50): # make sure the live plot has most recent 50 points                         
						temp_1.pop(0) 
					if b_cnt > 50:                      
						temp_2.pop(0)
					self.error_cnt = 0 # system error counter
			except Exception as err:
				method = '@error xbeeModule: start_: '
				log_error(method,err)
				self.coor = port_initialize('mac') # if error occur then re-initial the port
				self.error_cnt += 1
				time.sleep(3)

			if self.error_cnt == 5: # if system has error showed up more 5 times, system will stop
									# error are logged at the error.txt
				return

if __name__ == '__main__':
	threads = []
	xbee_module = xbeeModule(pri_flag=False)
	xbee_module.start_()


