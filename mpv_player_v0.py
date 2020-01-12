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

"""
This is the media player we use for isha pi project.
On Raspberri PI we will be using the openmx player.
On virtual machines and testing on windows we can use mpv player
"""
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

    #Methods that need to be assigned from outside
    #
    def _onUpdateRunTime(self, val):
        '''User must overrid this'''
        pass

    def _onUpdateTotaltime(self, val):
        '''User must overrid this'''
        pass


    # Public functions of the player, each player class should have them
    #
    def stop(self):
        self.killPlayer()


    def pause(self):
        self._execute({'command': ["set_property", "pause", True]})

    def play(self):
        self._execute({'command': ["set_property", "pause", False]})

    def seek(self, time):
        self._execute({'command': ["seek", str(time), "absolute"]})

    def togglePause(self):
        val = self.isPaused()
        if val is not None:
            self._execute({'command': ["set_property", "pause", not val]})

    def start(self, path, tSeek):
        self.path = path
        self._isPlaying = True

        mpvParam = mpvParams(tSeek, path, includes.config)
        self.process = Popen(mpvParam)

        self.playThread = threading.Thread(target = self._playWorkThread)
        self.playThread.setDaemon(True)
        self.playThread.start()

    def getRuntime(self):
        ret = self._execute({'command': ["get_property", "time-pos"]})

        if ret is None:
            return 0

        try:
            if 'data' in ret:
                return int(ret['data'])

        except json.decoder.JSONDecodeError as e:
            logging.error("Player: {}".format(e))
            return 0

    def getTotalTime(self):
        ret = self._execute({'command': ["get_property", "duration"]})

        if ret is None:
            return 0

        try:
            if 'data' in ret:
                return int(ret['data'])

        except json.decoder.JSONDecodeError as e:
            logging.error("Player: {}".format(e))
            return 0

    def getCurrentFile(self):
        if self._isPlaying:
            return self.path
        else:
            return None

    def isPaused(self):
        ret = self._execute({'command': ["get_property", "pause"]})
        if ret is None:
            return False

        if 'data' in ret:
            return ret['data']
        else:
            return None

    def isPlaying(self):
        return self._isPlaying

    #
    # Private methods
    #
    socket = None
    sockPath = None
    def _conectToSocket(self, path):
        #wait for socket file to be created
        while not os.path.exists(path):
            time.sleep(0.1)

        self.sockPath = path
        self.socket = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        try:
            self.socket.connect(path)
            return True
        except:
            return False


    def _execute(self, command):
        self.semaExec.acquire()
        data = json.dumps(command) + "\r\n"
        data = bytes(data, encoding='utf-8')
        try:
            if self.socket:
                self.socket.send(data)
                buf = self.socket.recv(1024)

                if "error" not in str(buf):#we got event see read again... retry
                     buf = self.socket.recv(1024)

                tmp = buf.decode("utf-8").split("\n")

                for line in tmp:
                    result = json.loads(line)

                    if not 'error' in result:
                        continue

                    status = result['error']
                    if status == 'success':
                        self.semaExec.release()
                        return result

                self.semaExec.release()
                return None

            else:
                self.semaExec.release()
                return None
        except Exception as e:
            logging.error(f"MpvPlayerV0: _execute: exception in socket communication = {e}")

            self.semaExec.release()
            return None



        logging.error("Player: error value returned from player...")
        self.semaExec.release()
        return None

    def _command(self, command, *args):
        return self._execute({'command': [command, *args]})

    def close(self):
        self.socket.close()


    def _playWorkThread(self):

        while True:
            if self._conectToSocket(os.path.join(includes.config['tmpdir'],"socket")):
                break

        self._isPlaying = True
        if self.process == None:
            self._isPlaying = False
            self.onPlayEnd(None)
            return

        while self.process.poll() == None:
            time.sleep(1)


        #-------------- End of playback ------------
        self.onPlayEnd(None)
        self._isPlaying = False


    def killPlayer(self):

        if self.process:
            self.process.kill()

        #wait for process to finish
        while self.process is not None and self.process.poll() is None:
            time.sleep(0.25)
