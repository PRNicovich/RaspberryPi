#!/usr/bin/python
#
# Periodically read temperature from 1-wire probe
# Save a week's worth to text file
# Every Sunday at 2 AM email report 
# Push log to network storage
# Email on low temp, high temp, or temp change alert
 
import sys
import time
import datetime
import smtplib
import numpy as np
from UploadToGoogleDrive import GoogleDriveFileUpload

email = ('gausLabAnalysis@gmail.com',)
password = ('1LikeB33s',)
destinationEmail = ('p.nicovich@unsw.edu.au',)
FileName = 'TempLog'
StoreFolder = '/home/pi/TempLogs/'
CYCLE = (60,) # Seconds between temp reads
TEMPLIMITS = (18, 26)
TEMPCHANGEPERHOUR = (1.0,)
lastAlert = 0
deviceList = {0 : 'Base', 
			  1 : '333A'}


def MakeLogFile():
	try:
		dateNow = datetime.datetime.now()
		fN = '{0}{1}{2}_{3}_{4}.txt'.format(StoreFolder, FileName, dateNow.month, dateNow.day, dateNow.year)
		fid = open(fN, 'w+')
		# Add in header information here
		
		# 
		fid.write('Timestamp\tDeviceID\tTemperature (deg C)\n')
	except:
		print('fail')
		sys.exit()
	return fid
	
def InitializeDevice(devNum):
	base_dir = '/sys/bus/w1/devices'
	device_folder = glob.glob(base_dir + '28*')[sensors]
    device_file = device_folder + '/w1_slave'
	
	return device_file
	
def read_temp_raw():
        f = open(device_file, 'r')
        lines = f.readlines()
        f.close()
        return lines
		
def read_temp():
        lines = read_temp_raw()
        while lines[0].strip()[-3:] != 'YES':
            time.sleep(0.2)
            lines = read_temp_raw()
        equals_pos = lines[1].find('t=')
        if equals_pos != -1:
            temp_string = lines[1][equals_pos+2:]
			temp_c = float(temp_string)/1000.0
			
	return temp_c

def cycleWifiConnection():
	os.system('sudo ifdown --force wlan0')
	time.sleep(200)
	os.system('sudo ifup --force wlan0')
	
def SendAndClearFile(fid):
	fileName = fid.name
	fid.close()
	# Post file to storage location
	
	gdoc = GoogleDriveFileUpload(fileName, 'TemperatureDataRecords', 'GausLabAnalysis', '1LikeB33s')	
	
	Up = 0
	while Up == 0
		if internet_on():
			gdoc.upload()
			Up = 1
		else:
			cycleWifiConnection()

	# Delete file from Pi
	os.remove(fileName)
	
	
def SendAlertEmail(Flag, tempVal, dateNow):
	# Send email via Gmail address above
		
	if Flag == 'High':
		subjectLine = 'High Temperature Alert! Temp Val = %d'.format(tempVal)
		body = 'High temperature of %d reached at %s.\n'.format(tempVal, str(dateNow))
	elif Flag == 'Low':
		subjectLine = 'Low Temperature Alert! Temp Val = %d'.format(tempVal)
		body = 'Low temperature of %d reached at %s.\n'.format(tempVal, str(dateNow))
	elif Flag == 'Delta':
		subjectLine = 'Delta Temperature Alert! Delta(Temp) Val = %d'.format(tempVal)
		body = 'Change in temperature of %d over one hour reached at %s.\n'.format(tempVal, str(dateNow))	

	headers = "\r\n".join(["from: " + email,
		"subject: " + email_subject,
		"to: " + destinationEmail,
		"mime-version: 1.0",
		"content-type: text/html"])
	
	content = headers + '\r\n\r\n' + body

	Sent = 0
	while Sent == 0:
		if internet_on():
			
			try:
				session = smtplib.SMTP('smtp.gmail.com', 587)
				session.ehlo()
				session.starttls()
				session.login(email, password)
				session.sendmail(email, destinationEmail, content)
				Sent = 1
			except:
				print('Failure to access Gmail')
				cycleWifiConnection()
		else:
			cycleWifiConnection()
			
	return 1
	
def checkForTempError(tempNow, lastAlert):
	# Calc delta temp
	if np.sum(delArray) == 0:
		# array has never been used
		delArray.fill(tempNow)
	else:
		#Typical behavior - shift all one back, add newest to list
		# Array now newest -> oldest
		delArray.roll(1)
		delArray[0] = tempNow
	
	deltaTemp = np.amax(delArray) - np.amin(delArray)	
	
	# Check for Alert status, send email if needed
	if tempNow > TEMPLIMTS[1]:
		# High alert
		if lastAlert != 1:
			SendAlertEmail(session, 'High', tempNow[0], dateNow)
			lastAlert = 1
	elif tempNow < TEMPLIMITS[0]:
		# Low alert
		if lastAlert != 2:
			SendAlertEmail(session, 'Low', tempNow[0], dateNow)
			lastAlert = 2
	elif deltaTemp > TEMPCHANGEPERHOUR:
		# Change alert
		if lastAlert != 3:
			SendAlertEmail(session, 'Delta', deltaTemp, dateNow)
			lastAlert = datetime.datetime.now()
	else:
		lastAlert = 0
		
	return lastAlert


def InitializeLogger():	
	fid = MakeLogFile()
	
	for devNum in range(len(deviceList)):
		device[devNum] = InitProbe(devNum)
		
	NCyclesPerHour = (360/CYCLES) # Figure this is close enough to an hour's worth of measurements
								  # Won't be perfect, but is close enough
	delArray = np.zeros(np.ceil(NCyclesPerHour), 1)
	
	return fid, device

def TempLoggerLoop(deviceList, fid):
	
	lastAlert = 0
	
	while True:
		for device in range(len(deviceList)):
			tempNow = (read_temp(device))
			dateNow = datetime.datetime.now()
			fid.write('{0}\t{1\n'.format(str(datetime.datetime.now()), tempNow[0]))
			
		if (time.strftime('%a') == 'Sun') % (time.strftime('%H') == 20):
			# Time to deal with log files
			# If log file is old, send-clear-remake
			fNameIfNow = '{0}{1}{2}_{3}_{4}.txt'.format(StoreFolder, FileName, dateNow.month, dateNow.day, dateNow.year)
			fNameNow = fid.name
			if fNameIfNow != fNameNow:
				# Files were NOT made on the same day
				SendAndClearFile(fid)
				fid = MakeLogFile()
				
		lastAlert = checkForTempError(tempNow[0], lastAlert)

		time.sleep(CYCLE)
		
if __name__ == '__main__':
	
	print 'Starting Temperature Logger'
	
