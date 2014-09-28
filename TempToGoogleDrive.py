import threading
import time
import datetime
import random
import os
import smtplib
import numpy as np
from UploadToGoogleDrive import GoogleDriveFileUpload, internet_on

username = ('GausLabAnalysis',)
email = ('gausLabAnalysis@gmail.com',)
password = ('1LikeB33s',)
destinationEmail = ('p.nicovich@unsw.edu.au',)

# TEMPFILEPATH = '/home/pi/TempDataRecords/'
TEMPFILEPATH = 'C:\\Users\\Rusty\\Dropbox\\Python\\ThreadTestData\\'

CYCLE = (1,)
TEMPLIMITS = (18, 26)
TEMPCHANGEPERHOUR = (1.0,)
lastAlert = 0
deviceList = {0 : 'Base', 
			  1 : '333A'}

deviceID = {0 : '28-000005d04cb0', 
			1 : '28-000005d05499'}

class Notify(threading.Thread):
	# Thread class for sending notifications
	def __init__(self, Val, Alert):
		super(Notify, self).__init__()
		self.Val = Val
		self.Alert = Alert
		
	def run(self):
		didNot = False
		while not didNot:
			# Insert commands to send proper email here
			print self.Alert + ' temp Alert! Temperature of  ' + str(self.Val) + ' read.\n'
			didNot = True
			
def read_temp_raw(device_file):
	f = open(device_file, 'r')
	lines = f.readlines()
	f.close()
	return lines
		
def read_temp(deviceNumber):
	print deviceList[deviceNumber]
	lines = read_temp_raw(deviceID[deviceNumber])
	while lines[0].strip()[-3:] != 'YES':
		time.sleep(0.2)
		lines = read_temp_raw()
	equals_pos = lines[1].find('t=')
	if equals_pos != -1:
		temp_string = lines[1][equals_pos+2:]
		temp_c = float(temp_string)/1000.0
			
	return temp_c
	
def read_temp_test(deviceNumber):
	print deviceList[deviceNumber]
	return [random.randint(17, 27)]

class TempLog:
	# Class for primary loop.  Handle data capture, writing, and notification here

	def __init__(self, fN):
		
		self.fileName = fN
		# self._value_lock = threading.Lock()
		self._running = True
		print self.fileName
		
	def terminate(self):
		self._running = False
		
	def ReadTemp(self, dv):
		tempNow = read_temp(dv)
			
		if tempNow[0] > TEMPLIMITS[1]: # Notify of specific event occurance
			N = Notify(tempNow[0], 'High')
			N.start()
		elif tempNow[0] < TEMPLIMITS[0]:
			N = Notify(tempNow[0], 'Low')
			N.start()
			# elif case for deltaTemp notification
			
			
		now = datetime.datetime.now()
		return now.isoformat() + '\t' + deviceList[dv] + '\t' + str(tempNow[0]) + '\n'
		
	
	def run(self):

		while self._running:
				
			f = open(self.fileName, 'a')
			for dv in deviceList:
				toWrite = self.ReadTemp(dv)
				f.write(toWrite)
			
			f.close()
			
			time.sleep(sum(CYCLE))
			
			
		
def MakeDataFile(filePath):
	# Generate new file for writing data
	now = datetime.datetime.now()
	fileName = filePath + now.strftime('%f') + '.txt'
	
	f = open(fileName, 'w')
	f.write(datetime.datetime.now().strftime("%I:%M%p on %B %d, %Y\n"))
	f.write('Timestamp\tProbeName\tTemperature\n')
	f.close()
	
	return fileName
	
def cycleInternet():
	os.system('sudo ifdown --force wlan0')
	time.sleep(200)
	print 'Attempt Reconnect'
	os.system('sudo ifup --force wlan0')
	time.sleep(30)
	return
	
def SendAndDeleteFile(filePath):
	# Move old file to Google Drive
	print 'Uploading file ' + filePath
	gdoc = GoogleDriveFileUpload(filePath, 'TemperatureDataRecords', 'GausLabAnalysis', '1LikeB33s')	
	gdocSent = False
	while not gdocSent:
		if internet_on():
			try:
				gdoc.upload()
				time.sleep(0.1)
				print 'File copied successfully'
				os.remove(filePath)
				gdocSent = True
			except:
				print 'Copy error'
				pass
		else:
			print 'Network not active'
			cycleInternet()
	return
	

if __name__ == '__main__':
	filePath = TEMPFILEPATH
	for n in range(1):
		f = MakeDataFile(filePath)
		c = TempLog(f)
		t = threading.Thread(target=c.run)
		t.start()
		time.sleep(5)
		c.terminate() # Signal termination

		fthread = threading.Thread(target=SendAndDeleteFile, args=(f,))
		fthread.start()
		
		
	t.join()
	fthread.join()