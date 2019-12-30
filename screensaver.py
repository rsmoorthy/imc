import logging
import threading
import time
import queue
import includes

class ScreenSaver():
    ctrlQueue = None
    thread = None
    idleCounter = 0
    timeStep = 0.08
    saverTimeout = 5
    active = None
    ena = False

    def _worker(self):
        while True:
            time.sleep(self.timeStep)
            self.idleCounter = self.idleCounter + self.timeStep

            #just limit the counter value
            if self.idleCounter > includes.config['settings']['screensaverTime'] and self.ena:
                self.idleCounter = includes.config['settings']['screensaverTime']
                self.screenManager.current = self.blackScreenName
                self.active = True

            if not self.ctrlQueue.empty():
                cmd = self.ctrlQueue.get()

                if cmd is None:
                    continue

                if cmd['cmd'] == 'reset':
                    self.idleCounter = 0
                    self.screenManager.current = self.menuName
                    self.active = False

                elif cmd['cmd'] == 'disable':
                    self.ena = False
                    #self.screenManager.current = self.menuName
                    self.idleCounter = 0
                    self.active = False

                elif cmd['cmd'] == 'enable':
                    self.ena = True
                    self.idleCounter = 0
                    self.active = False
                    self.screenManager.current = self.menuName

                elif cmd['cmd'] == 'start':
                    self.ena = True
                    self.idleCounter = includes.config['settings']['screensaverTime'] + 1
                    self.active = True
                    self.screenManager.current = self.blackScreenName


    def start(self, args):
        self.ctrlQueue.put({'cmd':'start'})

    def resetTime(self):
        if self.ena:
            self.ctrlQueue.put({'cmd':'reset'})

    def disable(self):
        self.ctrlQueue.put({'cmd':'disable'})

        while self.ena:
            continue



    def enable(self):
        self.ctrlQueue.put({'cmd':'enable'})


    def __init__(self, screenManager, blackScreenName, menuName):
        logging.info("ScreenSaver: init: called")
        self.ctrlQueue = queue.Queue()
        self.thread = threading.Thread(target=self._worker)
        self.thread.setDaemon(True)
        self.screenManager = screenManager
        self.idleCounter = 0
        self.blackScreenName = blackScreenName
        self.menuName = menuName
        self.active = False


        self.thread.start()
