import threading, Queue
from sub_plot_usb import display, xbeedisplay
from bigquery_m import data_insert

from sqs_pi import sqs_read
# import RPi.GPIO as GPIO

# below is the imports for xbee
import serial
from datetime import datetime
import time
from xbee import ZigBee
from sqlite_ import insert_db, getCommand

import threading

from initial_port import port_initialize
from frame_process import grab_analog_data
from app_process import display_temp
from m_control import grab_data
from error_handle import log_error
# from email_html import processEmail
from multiprocessing import Process


class xbeeThread(threading.Thread):
	def __init__(self, threadID, pri_flag=False):
		threading.Thread.__init__(self)
		self.threadID = threadID
		self.q = Queue.Queue()
		self.coor = None
		self.pri_flag = pri_flag
		self.cnt = 0

	def port_initialize(self):
	# this one defines the port info of the coordinator
		try:
			#set up port info
			port = '/dev/ttyUSB0'
			baud_rate = 19200
			#connet serial port to zigbee moudle
			ser = serial.Serial(port , baud_rate)
			self.coor = ZigBee(ser, escaped=True)
			self.cnt = 0
			print 'xbee port ', self.coor
		except Exception as err:
			method = 'xbee port_initialize()'
			log_error(method,err)
			self.cnt += 1

	def xbee_control_plot(self):
		xbee_list = {
					'\x00\x13\xA2\x00\x40\xE4\x42\x61': 'E1',
					'\x00\x13\xA2\x00\x40\xD8\x72\x50': 'E2',
					'\x00\x13\xA2\x00\x40\xE4\x42\xAB': 'E3',
					'\x00\x13\xA2\x00\x40\xE9\x64\x30': 'E4',
					'\x00\x13\xA2\x00\x40\xE9\x64\x22': 'E5'
				}
		self.port_initialize()
		print self.coor
		temp_tokens = [('8vf5kqtvsq', 'osi6wq0ycx'), ('3zmdvkdr3d', 'reus4ulnsm'), ('wwfamavla7', 'reada5usvl')] #first is the object, second is the moving average
		brightness_tokens = [('ksovtmjxtz', 'z6ebrojt9g'), ('z8ke5lz3ht', '0i4f2x6sie'), ('r9p798ftbb', 'fdjl6r6vka')]
		device_list = ['E1', 'E2', 'E5']
		temp_objs = xbeedisplay(temp_tokens, 'Temperature', 'Temperature/C','XBee_Temperature', device_list)
		for item in temp_objs:
			item[0].open()
			item[1].open()
		brightness_objs = xbeedisplay(brightness_tokens, 'Brightness', 'Brightness/Lumen','XBee_Brightness', device_list)
		for item in brightness_objs:
			item[0].open()
			item[1].open()
		last_push = datetime.now().minute
		while True:
			try:
				# print 'in reading'
				flag, data = grab_data(self.coor, self.pri_flag)
				# stream plot
				# print data
				if flag and data['timestamp'].minute >= last_push:
					if data['id'] == 'E1':
						temp_objs[0][0].write(dict(x = data['timestamp'].strftime('%H:%M:%S'), y=data['temp']))
						temp_objs[0][0].heartbeat()
						brightness_objs[0][0].write(dict(x = data['timestamp'].strftime('%H:%M:%S'),y=data['brightness']))
						brightness_objs[0][0].heartbeat()
					elif data['id'] == 'E2':
						temp_objs[1][0].write(dict(x=data['timestamp'].strftime('%H:%M:%S'), y=data['temp']))
						temp_objs[1][0].heartbeat()
						brightness_objs[1][0].write(dict(x=data['timestamp'].strftime('%H:%M:%S'), y=data['brightness']))
						brightness_objs[1][0].heartbeat()
					elif data['id'] == 'E5':
						temp_objs[2][0].write(dict(x=data['timestamp'].strftime('%H:%M:%S'), y=data['temp']))
						temp_objs[2][0].heartbeat()
						brightness_objs[2][0].write(dict(x=data['timestamp'].strftime('%H:%M:%S'), y=data['brightness']))
						brightness_objs[2][0].heartbeat()
					last_push = data['timestamp'].minute
				else:
					self.cnt += 1
			except Exception as err:
				i = 0
				method = '@usb_read module has plotly error: '
				log_error(method,err)
				for item in temp_objs:
					item[0].close()
					item[1].close()
				for item in brightness_objs:
					item[0].close()
					item[1].close()
				time.sleep(3)
				for item in temp_objs:
					item[0].open()
					item[1].open()
				for item in brightness_objs:
					item[0].open()
					item[1].open()
				self.cnt += 1
			if self.cnt == 5:
				return


	def run(self):
		self.xbee_control_plot()
		# print self.cnt
		while True:
			if self.cnt == 5:
				time.sleep(3)
				self.cnt = 0
				self.xbee_control_plot()
			print 'xbee error',self.cnt

class gpioThread(threading.Thread):
	def __init__(self,q):
		self.q = q
	def gpio_control():
		# initial the port settings
		GPIO.setmode(GPIO.BCM)
		ledPin = 23

		GPIO.setup(ledPin, GPIO.OUT)
		GPIO.output(ledPin,GPIO.LOW)
		
		ledPin_1 = 24
		GPIO.setup(ledPin_1, GPIO.OUT)
		GPIO.output(ledPin_1,GPIO.LOW)
		cnt = 0
		last_update = datetime.now()
		while True:
			try:
				sqs = getCommand(database_path, last_update)
				if len(sqs) >= 1:
					device, switch, update_time = sqs
					if device == 0: #ledPin 
						if switch != '0':
							switch = GPIO.HIGH
						else:
							switch =  GPIO.LOW
						GPIO.output(ledPin,switch)
					else:
						if switch != '0':
							switch = GPIO.HIGH
						else:
							switch =  GPIO.LOW
						GPIO.output(ledPin_1,switch)
					
					last_update = update_time
				time.sleep(10)
			except Exception as err:
				GPIO.cleanup()
				GPIO.setmode(GPIO.BCM)
				ledPin = 23
				GPIO.setup(ledPin, GPIO.OUT)
				GPIO.output(ledPin,GPIO.LOW)
				led_status = GPIO.LOW
				cnt += 1
				if cnt > 5:
					return
	def run(self):
		while True:
			if len(self.q) != 0:
				self.gpio_control()

class usbThread(threading.Thread):
	def __init__(self, threadID):
		threading.Thread.__init__(self)
		self.threadID = threadID
		self.ard_usb = None
		self.q = Queue.Queue()
		self.cnt = 0

	def init_port(self):
		try:
			port = '/dev/ttyUSB1'
			self.ard_usb = serial.Serial(port, 9600)
		except Exception as err:
			self.cnt += 1

	def plot(self):
		self.init_port()
		print 'port ', self.ard_usb
		mac = '\x00\x13\xA2\x00\x00\x00\x00\x00'
		name = 'USB0'
		temp_tokens = ['d8qfgxheir', 'vpye3amqub'] #first is the object, second is the moving average
		humidity_tokens = ['72ir3jse1g', 'ix48y2ta1n']
		brightness_tokens = ['8oa84nu0bf', 'kdcit7gx5z']
		t_obj, t_moving = display(temp_tokens, 'Temperature', 'Temperature/C','USB_Temperature')
		t_obj.open(); t_moving.open()
		h_obj, h_moving = display(humidity_tokens, 'Humidity', 'Humidity/%','USB_Humidity')
		h_obj.open(); h_moving.open()
		b_obj, b_moving = display(brightness_tokens, 'Brightness', 'Brightness/Lumen','USB_Brightness')
		b_obj.open(); b_moving.open()

		t_queue, h_queue, b_queue = [], [], []

		def moving_average(data_queue):
			return sum(data_queue)/float(len(data_queue))
		i = 0
		moving_window_size = 4
		while True:
			# print self.cnt
			try:
				raw_data =  self.ard_usb.readline() #arduino v0.2.1
				h, t, b = raw_data.split()
				timestamp = datetime.now()
				humidity, temperature, brightness = float(h), float(t), float(b)
				data = {'timestamp': timestamp,\
						'humidity': humidity, \
						'id': name, \
						'temp': temperature, \
						'brightness': brightness}
				# print 'usb data', raw_data
			except Exception as err:
				method = '@ard_usb module has port error: '
				log_error(method,err)

				self.q.put(err)
				self.cnt += 1
			#sql_data = [(mac, 'USB0', timestamp, temperature, humidity,  brightness)]
			#insert_db(sql_data)
			last_push = datetime.now().minute
			try:
				if data['timestamp'].minute >= last_push:
					t_obj.write(dict(x = data['timestamp'].strftime('%H:%M:%S'), y=data['temp']))
					t_obj.heartbeat()
					h_obj.write(dict(x = data['timestamp'].strftime('%H:%M:%S'),y=data['humidity']))
					h_obj.heartbeat()
					b_obj.write(dict(x = data['timestamp'].strftime('%H:%M:%S'),y=data['brightness']))
					b_obj.heartbeat()
					if i < moving_window_size:
						t_queue.append(data['temp'])
						h_queue.append(data['humidity'])
						b_queue.append(data['brightness'])
						t_moving.write(dict(x = data['timestamp'].strftime('%H:%M:%S'), y=data['temp']))
						t_moving.heartbeat()
						h_moving.write(dict(x = data['timestamp'].strftime('%H:%M:%S'), y=data['humidity']))
						h_moving.heartbeat()
						b_moving.write(dict(x = data['timestamp'].strftime('%H:%M:%S'), y=data['brightness']))
						b_moving.heartbeat()
						i += 1
					else:
						v_t, v_h, v_b = moving_average(t_queue), moving_average(h_queue), moving_average(b_queue)
						t_moving.write(dict(x = data['timestamp'].strftime('%H:%M:%S'), y=v_t))
						t_moving.heartbeat()
						h_moving.write(dict(x = data['timestamp'].strftime('%H:%M:%S'), y=v_h))
						h_moving.heartbeat()
						b_moving.write(dict(x = data['timestamp'].strftime('%H:%M:%S'), y=v_b))
						b_moving.heartbeat()
						t_queue.pop(0); h_queue.pop(0);b_queue.pop(0);
						t_queue.append(data['temp']);h_queue.append(data['humidity']); b_queue.append(data['brightness'])
					last_push = data['timestamp'].minute
			except Exception as err:
				t_obj.close(),t_moving.close()
				h_obj.close(),h_moving.close()
				b_obj.close(),b_moving.close()
				method = '@usb_read module has plotly error: '
				log_error(method,err)
				t_obj.open(),t_moving.open()
				h_obj.open(),h_moving.open()
				b_obj.open(),b_moving.open()
				i = 0
				self.q.put(err)
				self.cnt += 1
			try:
				input_row = {
							'mac': mac.encode('hex'),
							'timeStamp': timestamp.strftime('%Y-%m-%dT%H:%M:%S'),
							'temp': temperature,
							'humidity': humidity,
							'brightness': brightness
							}
				data_insert(input_row, pri_flag=True)
			except Exception as err:
				method = '@ard_usb module has bigquery error: '
				log_error(method,err)
				self.cnt += 1
				self.q.put(err)
			if self.cnt ==5:
				return

	def run(self):
		# if the program goes wrong five times, then the main function will restart it
		# this will will quit only if the main thread quits
		self.plot()
		while True:
			# print 'in error loop'
			if self.cnt == 5:
				time.sleep(5)
				# print 'will recall'
				# print 'error queue', self.q
				self.cnt = 0
				self.plot()


if __name__ == '__main__':
	threads = []
	q = Queue.Queue() #error queue
	xbee_thread = xbeeThread('xbee_thread',pri_flag=True)
	threads.append(xbee_thread)
	#usb_thread = usbThread('usb_thread')
	#threads.append(usb_thread)


	for t in threads:
		t.daemon = True
		t.start()
	print_flag = False
	while True:
		try:
			if print_flag:
				print 'in main'
		except Exception as err:
			print err
