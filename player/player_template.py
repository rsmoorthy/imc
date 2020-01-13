#from player import *
import logging
import subprocess
import os
import socket
import json
import time

from  subprocess import Popen, threading

import includes
from helper import mpvParams


class Player():
    process = None
    _isPlaying = False
    path = None
    semaExec = threading.Semaphore()
    endHandler = []

    #Playback end event
    #
    def onPlayEnd(self, args):
        for func in self.endHandler:
            if func:
                func(args)

    def addEndHandler(self, handler):
        self.endHandler.append(handler)

    # Public functions of the player, each player class should have them
    #
    def stop(self):
        pass

    def pause(self):
        pass

    def play(self):
        pass

    def seek(self, time):
        pass

    def togglePause(self):
        pass

    def start(self, path, tSeek):
        self.path = path
        self._isPlaying = True

    def getRuntime(self):
        pass

    def getTotalTime(self):
        pass

    def getCurrentFile(self):
        if self._isPlaying:
            return self.path
        else:
            return None

    def isPaused(self):
        pass

    def isPlaying(self):
        return self._isPlaying

    #
    # Private methods
    #
