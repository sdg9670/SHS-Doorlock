#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
PyFingerprint
Copyright (C) 2015 Bastian Raschke <bastian.raschke@posteo.de>
All rights reserved.

"""

import datetime
import time
import threading
import RPi.GPIO as GPIO
import os
import signal
import string
from picamera import PiCamera
from pyfingerprint.pyfingerprint import PyFingerprint
import subprocess
import storage
import random
import monitor
import multiprocessing

## Tries to initialize the sensor
class DoorLock(threading.Thread):
	def __init__(self, sc):
		try:
			threading.Thread.__init__(self)
			self.mode = 'check'
			self.sc = sc
			self.f = PyFingerprint('/dev/ttyAMA0', 57600, 0xFFFFFFFF, 0x00000000)
			if self.f.verifyPassword() == False:
				raise ValueError('The given fingerprint sensor password is wrong!')

			GPIO.setmode(GPIO.BCM)
			GPIO.setup(21, GPIO.OUT)
			os.system('killall nc')
			self.camera()

			self.lcdControl = monitor.lcd()
			self.lcdControl.lcd_clear()

		except Exception as e:
			print('The fingerprint sensor could not be initialized!')
			print('Exception message: ' + str(e))
			exit(1)

	def camera(self):
		PIPE = subprocess.PIPE
		self.p = subprocess.Popen(["/bin/bash", "-i", "-c",
								   "sudo raspivid -n -ih -t 0 -rot 0 -w 1280 -h 720 -fps 15 -b 1000000 -o - | nc -lkv4 5000"],
								  stdout=PIPE, preexec_fn=os.setsid)
		print(self.p)

	def run(self):
		while True:
			if self.mode == 'check':
				self.checkFingerprint()
			elif self.mode == 'enroll':
				self.saveFingerprint()

	def chageMode(self, modename):
		self.mode = modename

	def deleteFingerprint(self, id):
		if (self.f.deleteTemplate(id) == True):
			print('Template deleted!')

	def checkFingerprint(self):
		while True:
			try:
				print('mode: ' + self.mode)
				print('Waiting for finger...')

				self.lcdControl.lcd_clear()
				self.lcdControl.lcd_display_string("mode: " + self.mode, 1)
				self.lcdControl.lcd_display_string("Waiting Finger", 2)

				while self.f.readImage() == False and self.mode == 'check':
					pass
				if self.mode != 'check':
					return
				self.f.convertImage(0x01)
				print('Remove finger...')
				self.lcdControl.lcd_clear()
				self.lcdControl.lcd_display_string("mode: " + self.mode, 1)
				self.lcdControl.lcd_display_string("Remove Finger...", 2)
				time.sleep(2)
				result = self.f.searchTemplate()
				positionNumber = result[0]

				os.killpg(os.getpgid(self.p.pid), signal.SIGKILL)
				with PiCamera() as camera:
					camera.start_preview()
					time.sleep(1)
					camera.capture('/home/pi/Desktop/image.jpg')
					camera.stop_preview()

				self.var = self.rand()
				if storage.download('doorlock/' + self.var + '.jpg'):
					self.var = self.rand()

				storage.upload('/home/pi/Desktop/image.jpg', 'doorlock/' + self.var + '.jpg')
				self.camera()

				if(positionNumber >= 0):
					print('Success #' + str(positionNumber))
					self.lcdControl.lcd_clear()
					self.lcdControl.lcd_display_string("mode: " + self.mode, 1)
					self.lcdControl.lcd_display_string("Success #" + str(positionNumber), 2)
					GPIO.output(21, True)
					time.sleep(1)
					GPIO.output(21, False)

					now = datetime.datetime.now()
					timenow = now.strftime('%Y-%m-%d %H:%M:%S')
					picturePath = storage.path('doorlock/' + self.var + '.jpg')
					doorLockstatus = '정상'

					self.sc.sndMsg('doorlock\timage\t' + str(picturePath[3:]) + '\t' + timenow + '\t' + doorLockstatus)

				else:
					print('Failed to FingerPrint')

					self.lcdControl.lcd_clear()
					self.lcdControl.lcd_display_string("mode: " + self.mode, 1)
					self.lcdControl.lcd_display_string("Falied Finger", 2)
					time.sleep(1)

					now = datetime.datetime.now()
					timenow = now.strftime('%Y-%m-%d %H:%M:%S')
					picturePath = storage.path('doorlock/' + self.var + '.jpg')
					doorLockstatus = '비정상'
					self.sc.sndMsg('doorlock\timage\t' + str(picturePath[3:]) + '\t' + timenow + '\t' + doorLockstatus)


			except Exception as e:
				print('Operation failed!')
				print('Exception message: ' + str(e))

	def saveFingerprint(self):
		try:
			print('mode: ' + self.mode)
			print('Waiting for finger...')
			self.lcdControl.lcd_clear()
			self.lcdControl.lcd_display_string("mode: " + self.mode, 1)
			self.lcdControl.lcd_display_string("Waiting Finger...", 2)
			while self.f.readImage() == False and self.mode == 'enroll':
				pass
			if self.mode != 'enroll':
				return
			self.f.convertImage(0x01)

			print('Remove finger...')
			self.lcdControl.lcd_clear()
			self.lcdControl.lcd_display_string("mode: " + self.mode, 1)
			self.lcdControl.lcd_display_string("Remove Finger...", 2)

			print('Waiting for same finger again...')
			self.lcdControl.lcd_clear()
			self.lcdControl.lcd_display_string("mode: " + self.mode, 1)
			self.lcdControl.lcd_display_string("SameFinger again", 2)

			while self.f.readImage() == False and self.mode == 'enroll':
				pass
			if self.mode != 'enroll':
				return
			self.f.convertImage(0x02)

			time.sleep(2)

			if self.f.compareCharacteristics() == 0:
				self.lcdControl.lcd_clear()
				self.lcdControl.lcd_display_string("mode: " + self.mode, 1)
				self.lcdControl.lcd_display_string("Do not match", 2)
				time.sleep(1)
			if self.f.compareCharacteristics() == 0:
				raise Exception('Fingers do not match')


			self.f.createTemplate()
			positionNumber = self.f.storeTemplate()
			print('#' + str(positionNumber))
			self.lcdControl.lcd_clear()
			self.lcdControl.lcd_display_string("mode: " + self.mode, 1)
			self.lcdControl.lcd_display_string("Success #" + str(positionNumber), 2)
			time.sleep(1)
			self.sc.sndMsg('doorlock\tenroll\t' + str(positionNumber))

			time.sleep(2)
			self.mode = 'check'
		except Exception as e:
			print('Operation failed!')
			print('Exception message: ' + str(e))

	def openDoor(self):
		GPIO.output(21, True)
		time.sleep(4)
		GPIO.output(21, False)

	def rand(self):
		_LENGTH = 8
		random_var = string.digits
		result = ""
		for i in range(_LENGTH):
			result += random.choice(random_var)
		return result



