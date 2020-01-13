#from player import *
import logging
import subprocess
import os
import socket
import json
import time
import queue

import vlc
from  subprocess import Popen, threading

import includes
from helper import mpvParams


class Player():
    process = None
    _isPlaying = False
    path = None
    semaExec = threading.Semaphore()
    endHandler = []

    vlcPlayer = None
    vlcInst = None
    evManager = None
    cmdQueue = None

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
        self.vlcPlayer.stop()

    def pause(self):
        if not self.isPaused():
            self.vlcPlayer.pause()

    def play(self):
        self.vlcPlayer.play()

    def seek(self, tSeek):
        if self.vlcPlayer.is_seekable():
            self.vlcPlayer.set_time(tSeek*1000)


    def togglePause(self):
        self.vlcPlayer.pause()

    def start(self, path, tSeek):
        self.path = path
        self._isPlaying = True

        media = self.vlcInst.media_new(path)
        self.vlcPlayer.set_media(media)

        self.vlcPlayer.play()
        #self.vlcPlayer.set_fullscreen(True)

        #seek must come after file is started
        self.vlcPlayer.set_time(tSeek*1000)
        #self.vlcPlayer.toggle_fullscreen()


    def getRuntime(self):
        return int(self.vlcPlayer.get_time()/1000)

    def getTotalTime(self):
        return int(self.vlcPlayer.get_length()/1000)


    def getCurrentFile(self):
        if self._isPlaying:
            return self.path
        else:
            return None

    def isPaused(self):
        if self.vlcPlayer.is_playing() == 1:
            return False
        elif self.vlcPlayer.is_playing() == 0:
            return True

        return False


    def isPlaying(self):
        return self._isPlaying

    #
    # Private methods
    #
    def _mediaPlayerEnd(self, event):
        self.cmdQueue.put({'cmd':'mediaPlayerEnd'})

    def _worker(self):
        '''Worker thread that receives evenet manager signals'''
        while True:

            tmp = self.cmdQueue.get()
            cmd = tmp['cmd']

            #event manager callbacs cannot call vlc functions so this is why this...
            if cmd == "mediaPlayerEnd":
                self.onPlayEnd(None)
                self._isPlaying = False


    def __init__(self):
        #self.vlcInst = vlc.Instance()
        self.vlcInst = vlc.Instance(['-f'])
        self.vlcPlayer = self.vlcInst.media_player_new()

        self.evManager = self.vlcPlayer.event_manager()
        self.evManager.event_attach(vlc.EventType.MediaPlayerEndReached, self._mediaPlayerEnd)

        self.cmdQueue = queue.Queue()
        self.workThread = threading.Thread(target = self._worker)
        self.workThread.setDaemon(True)
        self.workThread.start()



def test():
    def print_handler(args):
        print("Print Handler called")

    pl = Player()
    pl.addEndHandler(print_handler)

    #for i in range(2):
    pl.start("/mnt/Ishamedia/videos/a.mp4", 50)
    pl.vlcPlayer.toggle_fullscreen()

    time.sleep(4)
    print(pl.isPaused())
    #print(pl.vlcPlayer.get_xwindow())
    #pl.togglePause()

    #pl.vlcPlayer.toggle_fullscreen()

    while pl.isPlaying():
        time.sleep(1)
        print(pl.getRuntime())
        print(pl.getTotalTime())
        print(pl.isPaused())
        print(pl.getCurrentFile())

        #pl.togglePause()
        #pl.pause()
        #time.sleep(3)
        #pl.play()
        #pl.seek(20)
        # pl.togglePause()

    pl.stop()
