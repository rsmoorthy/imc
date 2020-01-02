import os
import sys
import asyncio
import evdev
import threading
import logging
from selectors import DefaultSelector, EVENT_READ
import traceback

from ipc import Ipc

class KeyHandler():
	keyboards = []
	thread = None
	selector = None

	'''These keys are used to identify keyboards which can be usefull for our application'''
	supportedKeys = [
		'KEY_LEFT',
		'KEY_RIGHT',
		'KEY_UP',
		'KEY_DOWN'
	]

	def onPress(self, args):
		pass

	def onRelease(self, args):
		pass

	def _setScancodes(self):
		self.scancodes = {}
		self.scancodes[1] = "esc"
		self.scancodes[14] = "back"
		self.scancodes[25] = "power" #TODO: right now its P key for testing
		self.scancodes[27] = "+"
		self.scancodes[28] = "enter"
		self.scancodes[50] = "m"
		self.scancodes[53] = "-"
		self.scancodes[88] = "home"
		self.scancodes[103] = "up"
		self.scancodes[104] = "pgup"
		self.scancodes[105] = "left"
		self.scancodes[106] = "right"
		self.scancodes[108] = "down"
		self.scancodes[109] = "pgdown"
		self.scancodes[113] = "volume mute"
		self.scancodes[114] = "volume down"
		self.scancodes[115] = "volume up"
		self.scancodes[158] = "back" #browser back
		self.scancodes[172] = "home" #home key


	def _worker(self):
		while True:
			try:
				for key,mask in self.selector.select():
					device = key.fileobj
				for event in device.read():
					if event.type == 1:
						if event.value == 0:#key released
							self.onRelease((evdev.ecodes.KEY[event.code], event.code))

						#elif event.value == 0:#key pressed
						else:
							try:
								self.onPress((event.code, self.scancodes[event.code]))
								#self.onPress((event.code, self.scancodes[event.code]))
							except AttributeError as e:
								# logging.error("keyHandler: [AttributeError] {}".format(e))
								logging.error("keyHandler: [AttributeError] {}".format(traceback.format_exc()))

							except TypeError as e:
								logging.error("keyHandler: [Type Error] {}".format(traceback.format_exc()))
							except KeyError as e:
								logging.debug("keyHandler: [KeyError] {}".format(traceback.format_exc()))
							except NameError as e:
								logging.error("keyHandler: [NameError] {}".format(traceback.format_exc()))
							except:
								logging.debug("keyHandler: [unhandled exception] unsupported key code = {}".format(traceback.format_exc()))

			except BlockingIOError:
				pass



	def __init__(self):
		devices = [evdev.InputDevice(path) for path in evdev.list_devices()]

		for dev in devices:
			cap = dev.capabilities(verbose=True)
			for item in cap:
				if 'EV_KEY' in item:
					isKeyboard = False
					for availKeys in cap[item]:

						for supKey in self.supportedKeys:
							if supKey in availKeys[0]:
								isKeyboard = True
								break

						if isKeyboard:
							isKeyboard = False
							self.keyboards.append(dev)
							break

		self.selector = DefaultSelector()

		for kbd in self.keyboards:
			self.selector.register(kbd, EVENT_READ)

		self.thread = threading.Thread(target=self._worker)
		self.thread.setDaemon(True)
		self.thread.start()

		self._setScancodes()


#------------------------------------------------------------------------------
#
if __name__ == "__main__":

	def onPress(self, args):
		print(args)


	k = KeyHandler()
	k.onPress = onPress


	while True:
		import time
		time.sleep(2)
		print("alive")
