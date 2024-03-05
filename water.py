import threading
import time
import datetime
import logit
import RPi.GPIO as GPIO
import waterdb
import sys

class valveThread(threading.Thread):

	def __init__(self, valve, pin):
		threading.Thread.__init__(self)

		self.valve = int(valve)
		self.on = False
		self.up = True
		self.event = threading.Event()
		self.endtime = datetime.datetime.now()
		
		# Weekday (1 = Monday, 7 = Sunday). This is used to trigger a database read once a day
		self.today = datetime.datetime.now().isoweekday()
		
		self.count = 0
		self.pin = int(pin)

		self.timers = []

		threading.Thread.daemon = True
		GPIO.setmode(GPIO.BCM)
		GPIO.setup(self.valve, GPIO.OUT)
	
	def run(self):
		logit.logit("Starting thread", self.valve)

		self.timers = self.storeTimers()

		for t in self.timers:
			print("timer (valve " + str(self.valve) + ") :" + str(t["start"]))

		while (self.up):
			
			self.event = threading.Event()
			
			self.event.wait(timeout=5)
			
			if (self.on):
				self.count += 1
				if (self.endtime < datetime.datetime.now() or self.count > 60):
						self.closeValve()
			else:
				try:
					self.checkTimers()
				except:
					print("Exception: " + str(sys.exc_type))
					print("           " + str(sys.exc_value))
					continue

		self.closeValve()
		

	def remaining(self):
#                print "Remaining: " + str(self.on) + " time = " + str(self.endtime)
		if (self.on):
			left =  self.endtime - datetime.datetime.now()
			return ({"left" : left.total_seconds(),
					"endtime" : self.endtime})
		else:
			return ({"left" : 0,
						"endtime" : 0})

		
	def stop(self):
		logit.logit("Stopping valve thread", self.valve)
		self.up = False
		self.event.set()


		
	def getState(self):
		"Read the current value of a valve"
		if (GPIO.input(self.valve)) :
			return "On"
		else :
			return "Off"



	def openValve(self, timer):
		"Open a valve"
		self.endtime = datetime.datetime.now() + datetime.timedelta(seconds=timer)
		logit.logit("Opening valve (ends " + str(self.endtime) + ")", self.valve)
		GPIO.output(self.valve, True)
		self.count = 0
		self.on = True



	def closeValve(self):
		"Close a valve"
		logit.logit("Closing valve", self.valve)
		GPIO.output(self.valve, False)
		self.on = False
		

	def storeTimers(self):
		wdb = waterdb.waterdb()
		timers = wdb.getTimers(self.valve)

		return timers
	
	def scheduledStart(self, timers):
		for timer in timers:
#				print timer
			r = timer["remaining"]
			logit.logit("Scheduled start - %02d:%02d:%02d remaining" % (r//3600, r//60, r%60), self.valve)
			self.openValve(timer["remaining"])



	def checkTimers(self):
		# Get today's weekday number (1 = Monday, 7 = Sunday)
		today = datetime.datetime.now().isoweekday()
		
		# Detect if timers have been refreshed from database
#		if (today != self.today):
		try:
			self.timers = self.storeTimers()
#			logit.logit("Timers refreshed from database", self.valve)
			self.today = today
		except:
			logit.logit("Failed to refresh timers from database - using previous ones", self.valve)
			for timer in self.timers:
				timer["done"] = False
					
		# Current time
		now = datetime.datetime.now().time()
		
		# For each timer we've stored, check:
		#		If today's day matches (or the day on the timer is zero [all days])
		#		If the timer's already been processed (in case it was terminated early)
		#		If the time now is in the window of the timer
		#
		# If we find a timer that matches, then open the valve
		
		for timer in self.timers:

			if (timer["day"] == 0 or timer["day"] == today):

				if (timer["done"] == False):
					
					windowStart = (datetime.datetime.min + timer["start"]).time()
					windowEnd = (datetime.datetime.min + timer["start"] + timer["duration"]).time()
					
					if (now >= windowStart and now <= windowEnd):

						r = timer["duration"].total_seconds()
						timer["done"] = True
						logit.logit("Scheduled start - %02d:%02d:%02d remaining" % (r//3600, r//60, r%60), self.valve)
						self.openValve(r)
						return True
					
		return False
															
	def getPin(self):
#                print "getPin: " + str(self.pin)
		
		return self.pin
		
		
	def getValve(self):
		
#                print "getPin: " + str(self.valve)
		
		return self.valve
			
			
	
