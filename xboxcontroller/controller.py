# controller.py

# Defines a controller class which allows for control of the dorna arm via the xbox controller for positioning

from inputs import devices, get_gamepad

from threading import Lock

import time

import random

class xbox_controller:

	'''
	Controller for an attached xbox controller, using the inputs library (cross-platform)
	'''

	def __init__(self, arm_instance):

		'''Initialise the controller object and find attached gamepad (only supports one)'''

		self.arm = arm_instance

		# Force detection of attached gamepads
		devices._detect_gamepads()

		self.updateLock=Lock()

		self.state={}

	def updateButtonsAndAxes(self, events):

		'''Update internal representation of buttons and axes '''

		with self.updateLock:

			print(len(events))

			for event in events:

				print(event.code, event.state)

				if event.ev_type!='Sync':

					self.state[event.code]=event.state

				else:
					self.moveIfReqd()

	def control_loop(self):

		running=True
		try:
			while running:
				events=get_gamepad()
				self.updateButtonsAndAxes(events)

		except KeyboardInterrupt:
			print(self.state)
			return None

	def moveIfReqd(self):

		if 'BTN_NORTH' in self.state.keys() and self.state['BTN_NORTH']==1:

			self.doFakeActionAndAwaitCompletion(0.5)

	def randomMove(self):

		if random.random()>0.8:

			dt=random.random()*2

			self.doFakeActionAndAwaitCompletion(dt)

	def doFakeActionAndAwaitCompletion(self, dt):

		print('Moving')
		time.sleep(dt)
		print('Finished')



		return 1

