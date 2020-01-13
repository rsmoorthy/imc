#
# This code is experimental not complete yet
#
import vlc
from time import sleep
import queue
from subprocess import threading


test = True


class Player():
    vlcPlayer = None
    vlcInst = None
    evManager = None
    cmdQueue = None
    endHandler = []

    #event callback for other applications
    def isPlaying(self):
        return True

    def onPlayEnd(self, args):
        for func in self.endHandler:
            if func:
                func(args)

    def addEndHandler(self, handler):
        self.endHandler.append(handler)

    def _mediaPlayerEnd(self, event):
        self.cmdQueue.put({'cmd':'mediaPlayerEnd'})


    def _worker(self):
        '''Worker thread that receives evenet manager signals'''
        while True:
            sleep(0.5)
            tmp = self.cmdQueue.get()
            print(tmp)
            cmd = tmp['cmd']

            #event manager callbacs cannot call vlc functions so this is why this...
            if cmd == "mediaPlayerEnd":
                #self.vlcPlayer.release()
                self.vlcPlayer.stop()
                self.onPlayEnd(None)


    #player control functions
    def stop(self):
        if self.vlcPlayer.is_playing:
            self.vlcPlayer.stop()

    def pause(self):
        if self.vlcPlayer.is_playing:
            self.vlcPlayer.pause()

    def play(self):
        self.vlcPlayer.play()

    def seek(self, tSeek):
        if self.vlcPlayer.is_seekable() and self.vlcPlayer.is_playing():
            self.vlcPlayer.set_time(tSeek*1000)

    def togglePause(self):
        self.vlcPlayer.pause()

    def start(self, path, tSeek):
        media = self.vlcInst.media_new(path)
        self.vlcPlayer.set_media(media)

        self.vlcPlayer.play()
        #self.vlcPlayer.set_fullscreen(True)

        #seek must come after file is started
        self.vlcPlayer.set_time(tSeek*1000)
        self.vlcPlayer.toggle_fullscreen()

    def killPlayer(self):
        if self.vlcPlayer.is_playing:
            self.vlcPlayer.stop()

    #player status
    def getRuntime(self):
        return self.vlcPlayer.get_time()

    def getCurrentTotalTime(self):
        pass

    def isPaused(self):
        if self.vlcPlayer.is_playing() == 1:
            return False
        elif self.vlcPlayer.is_playing() == 0:
            return True

        return None

    def __init__(self):
        self.vlcInst = vlc.Instance(['-f'])
        self.vlcPlayer = self.vlcInst.media_player_new()

        self.evManager = self.vlcPlayer.event_manager()
        self.evManager.event_attach(vlc.EventType.MediaPlayerEndReached, self._mediaPlayerEnd)

        self.cmdQueue = queue.Queue()
        self.workThread = threading.Thread(target = self._worker)
        self.workThread.setDaemon(True)
        self.workThread.start()




if __name__ == "__main__":

    pl = Player()

    for i in range(2):
        pl.start("/tmp/a.mp4", 0)
        pl.vlcPlayer.toggle_fullscreen()
        sleep(4)
        print(pl.isPaused())
        print(pl.vlcPlayer.get_xwindow())
        #pl.togglePause()

        pl.vlcPlayer.toggle_fullscreen()

        while test:
            sleep(2)
            print(pl.getRuntime())
            print(pl.isPaused())

            #pl.stop()

        sleep(4)
