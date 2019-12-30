import mpv
import logging
import queue

from time import sleep, strftime, gmtime
from subprocess import threading

class Player():
    mpvPlayer = None
    endHandler = []
    shutdownHandler = []

    def onPlayEnd(self, args):
        for func in self.endHandler:
            if func:
                func(args)

    def addEndHandler(self, handler):
        self.endHandler.append(handler)

    def onPlayShutdown(self, args):
        for func in self.endHandler:
            if func:
                func(args)

    def addShutdownHandler(self, handler):
        self.shutdownHandler.append(handler)

    def _onUpdateRunTime(self, val):
        pass

    def _onUpdateTotaltime(self, val):
        pass

    #player control functions
    def stop(self):
        self.mpvPlayer.terminate()
        self._running = False
        sleep(2) #safety buffer


    def pause(self):
        self.mpvPlayer.pause = True

    def play(self):
        if self.mpvPlayer.pause:
            self.mpvPlayer.play()

    def seek(self, tSeek):
        self.mpvPlayer.command("seek", tSeek, "absolute")

    def togglePause(self):
        if self.mpvPlayer.pause:
            self.mpvPlayer.pause = False
        else:
            self.mpvPlayer.pause = True


    def _mpvEvent(self, event):
        import time

        if event['event_id'] == mpv.MpvEventID.END_FILE:
            self.onPlayEnd(None)
            self._isPlaying = False
            #self.stop() #to terminate everything properly


        elif event['event_id'] == mpv.MpvEventID.SHUTDOWN:
            self.onPlayShutdown(None)
            self._isPlaying = False
            #self.stop() #to terminate everyting properly


    def start(self, path, tSeek):
        self.mpvPlayer = mpv.MPV(start=tSeek)#, fs="yes")
        print("API Ver = {}".format(self.mpvPlayer.api_version()))
        self.mpvPlayer.register_event_callback(self._mpvEvent)
        self.curFile = path
        self.mpvPlayer.play(path)
        self._onUpdateTotaltime(strftime('%H:%M:%S', gmtime(self.mpvPlayer.duration)))
        self._isPlaying = True

    #player status
    def getRuntime(self):
        try:
            return int(self.mpvPlayer.time_pos)
        except:
            return 0


    def getCurrentFile(self):
        return self.mpvPlayer.path

    def getTotalTime(self):
        return self.mpvPlayer.duration

    def isPaused(self):
        return self.mpvPlayer.pause

    def isPlaying(self):
        #return not self.mpvPlayer.core_idle
        return self._isPlaying
        #return False

    def __init__(self):
        self.curFile = None
        self._isPlaying = False




if __name__ == "__main__":
    import threading

    test = True
    pl = Player()

    for i in range(2):
        print("before")
        pl.start("/tmp/a.mp4", 0)
        #pl.mpvPlayer.toggle_fullscreen()
        sleep(4)
        print(threading.active_count())
        #print(pl.isPaused())
        pl.stop()
        print("after")
        print(threading.active_count())
        #print(pl.mpvPlayer.get_xwindow())
        #pl.togglePause()

        #pl.mpvPlayer.toggle_fullscreen()

        # while test:
        #     sleep(2)
        print(pl.getRuntime()) # causes the problem....
        #     print(pl.isPaused())

            #pl.stop()

        sleep(4)
