import mpv_player
import vlc_player
import mpv_player_v0
import time
import threading
import logging

logging.basicConfig(level=logging.DEBUG)

from queue import Queue
from helper import synchronized, createPlayListEntry, checkPlaylist, clipInt

class PlayerCore():
    #Static variables
    #
    playerSync = threading.Semaphore()
    cmdBlock = threading.Semaphore()
    # Callbacks/Hooks that need to be setup from outside
    #
    def screenSaverRun(self, mode):
        '''Needs to activate the screen saver as a black screen for pre/post processing
            mode = 0 screen saver off and disabled
            mode = 1 scren saver enabled and visible
        '''
        logging.warning("PlayerCore: screenSaverRun() not set !!!")

    def activateColorBar(self, mode):
        '''Set the color of color indicator, to show wait state to the user if needed
            mode = 0 default color
            mode = 1 wait color
        '''
        logging.warning("PayerCore: activateColorBar() not set !!!")

    def onPlayEnd(self, args):
        '''This function needs to be registered with the player event handler'''
        #TOOD: send command "end" to state machine
        self._sendCommand({'cmd':'end'})
        #time.sleep(5) #to make sure it has been processed


    # Public methods
    #
    @synchronized(playerSync)
    def getRuntime(self):
        return self.player.getRuntime()

    @synchronized(playerSync)
    def getCurrentFile(self):
        return self.player.getCurrentFile()

    @synchronized(playerSync)
    def getTotalTime(self):
        return self.player.getTotalTime()

    @synchronized(playerSync)
    def isPaused(self):
        return self.player.isPaused()

    @synchronized(playerSync)
    def isPlaying(self):
        return self.player.isPlaying()

    @synchronized(playerSync)
    def pause(self, args):
        self.player.pause()

    @synchronized(playerSync)
    def play(self, args):
        self.player.play()

    @synchronized(playerSync)
    def stop(self, args):
        self._sendCommand({'cmd':'stop'})

    @synchronized(playerSync)
    def seek(self, time):
        self.player.seek(time)

    @synchronized(playerSync)
    def startSingle(self, path, tStart):
        playlist = createPlayListEntry(path, 0, tStart)
        self._sendCommand({'cmd':'play', 'playlist':playlist})
        #sTODO: put playlist in queue for processing

    @synchronized(playerSync)
    def startPlaylist(self, playlist):
        self._sendCommand({'cmd':'play', 'playlist':playlist})

    @synchronized(playerSync)
    def keyEnter(self, args):
        self._sendCommand({'cmd':'enter'})

    @synchronized(playerSync)
    def keyNext(self, args):
        self._sendCommand({'cmd':'next'})

    @synchronized(playerSync)
    def togglePause(self, args):
        self.player.togglePause()

    #@synchronized(playerSync)
    def keyPrevious(self, args):
        self._sendCommand({'cmd':'previous'})

    def _sendCommand(self, cmd):
        self.cmdBlock.acquire()
        self.cmdQueue.put(cmd)


    # Ques command interface to request functions of core player from multipe proceses
    #
    def _playlistWork(self):
        enter = stop = next = previous = play = end = once = False
        state = "idle"
        lastState = "idle"
        entry = None
        entryId = 0
        flags = {}
        flags['next'] = False

        # try:
        cnt = 0
        cnt1 = 0

        while True:
            #read next entry of queue blocking style
            time.sleep(0.01)
            cnt = cnt + 0.01

            if cnt >= 1:
                cnt = 0
                cnt1 = cnt1 + 1

                if self.isPlaying() and (cnt1 % self._runtimeInterval) == 0:
                    runtime = self.getRuntime()
                    path =self.getCurrentFile()

                    if self._db != None and self._writeDb != None:
                        self._db['runtime'] = runtime
                        self._db['mediaPath'] = path
                        self._writeDb()
                    else:
                        logging.error("PlayerCore: wrtieDB callback and db object not set")

            if not self.cmdQueue.empty():
                cmd = self.cmdQueue.get()
                self.cmdQueue.task_done()

                if cmd['cmd'] == "enter":
                    enter = True

                elif cmd['cmd'] == "stop":
                    play = False #stop plalist
                    enter = stop = next = previous = play = end = once = False
                    entry = None
                    entryId = 0
                    state = "idle"
                    play = False
                    self.osdControl(3) #give control back to last main menu itemm
                    self.activateColorBar(0)
                    self.screenSaverRun(2)
                    self.player.stop()

                elif cmd['cmd'] == "previous":
                    previous = True

                elif cmd['cmd'] == "next":
                    next = True

                elif cmd['cmd'] == "end":
                    end = True
                    if self._db != None and self._writeDb != None:
                        self._db['runtime'] = 0
                        self._db['mediaPath'] = path
                        self._writeDb()

                elif cmd['cmd'] == "play":
                    logging.error("------- core plaer: ---- play ")
                    if not play:
                        playlist = cmd['playlist']
                        check = checkPlaylist(playlist)
                        if check[1] == 0:
                            play = True
                            self.osdControl(0) #save current id
                            self.osdControl(1) # switch controls to osd
                        else:
                            logging.error("PlayerCore: playlist format error = {}".format(check))



                self.cmdBlock.release()
            #Debug prints for state
            #
            if state != lastState:
                logging.debug("PlayerCore: state = {} | enter = {} | stop = {} | next = {} | prev = {} | play = {} | end = {} | once = {} |"
                    .format(state, enter, stop, next, previous, play, end, once))

                lastState = state

            #State machine
            #
            if state == "idle":
                if play:
                    state = "pre"
                    end = False
                    entry = playlist[str(entryId)]
                    logging.error("EntryId play: {} / {}".format(entryId, entry))
                    self.osdControl(2)# switch control to playerControl

            elif state == "pre":
                end = False
                if type(entry['pre']) == str and entry['pre'].lower() == "blackscreen":
                    self.activateColorBar(1)
                    self.screenSaverRun(0)
                    state = "preWait"
                    flags['preWait'] = False

                else:
                    state = "play"

            elif state == "preWait":
                end = False
                if enter:
                    enter = False
                    state = "play"

                elif previous:
                    previous = False
                    entryId = clipInt(entryId - 1, 0, 99999)
                    state = "idle"

                elif next:
                    next = False
                    state = "end"

            elif state == "play":
                end = False
                path = entry['path']
                tSeek = entry['start']
                self.player.start(path, tSeek)
                state = "waitEnd"
                self.osdControl(1)# give control back to osd

            elif state == "waitEnd":
                if end:
                    end = False
                    previous = False
                    next = False
                    state = "post"
                    flags['next'] = False

                elif previous:
                    print("waitEnd: previous")
                    previous = False
                    state = "previousWait"
                    self.player.stop()


                elif next and not flags['next']:
                    next = False
                    flags['next'] = True
                    self.player.stop()

            elif state == "previousWait":
                if end:
                    end = False
                    previous = False
                    next = False
                    state = "idle"
                    entryId = clipInt(entryId - 1, 0, 99999)
                    flags['next'] = False


            elif state == "post":
                if type(entry['post']) == str and entry['post'].lower() == "repeat_once" and once == False:
                    once = True
                    state = "play"

                elif type(entry['post']) == str and entry['post'].lower() == "repeat_forever":
                    state = "play"
                    self.player.stop()
                else:
                    state = "end"

            elif state == "end":
                self.activateColorBar(0)

                entryId = entryId + 1
                logging.debug("PLayerCore: entryId = {}".format(entry))
                if entryId >= len(playlist):
                        play = False #stop plalist

                        self.screenSaverRun(1) #Stay on screen saver
                        enter = stop = next = previous = play = end = once = False
                        entry = None
                        entryId = 0
                        self.osdControl(3) #give control back to last main menu itemm

                state = "idle"
                end = False

    # def osdDisable(self, args):
    #     logging.warning("PlayerCore: osdDisable method has not been assigned!!!!")
    #
    # def osdEnable(self, args):
    #     logging.warning("PlayerCore: osdEnable method has not been assigned!!!!")
    def osdControl(self, mode):
        logging.warning("PlayerCore: osdControl method has not been assigned!!!!")


    def __init__(self, **kwargs):
        self._runtimeInterval = kwargs.pop('runtimeInterval', 1)
        self._db = kwargs.pop('db', None)
        self._writeDb = kwargs.pop('writeDb', None)
        #self.player = vlc_player.Player() #TODO: In the fucture we could maske this selection via settings to chooce differernt players.
        self.player = mpv_player_v0.Player() #TODO: In the fucture we could maske this selection via settings to chooce differernt players.
        self.player.addEndHandler(self.onPlayEnd)
        #
        # Set up command interface queue for processing commands.
        #
        self.cmdQueue = Queue()
        self.cmdThread = threading.Thread(target=self._playlistWork)
        self.cmdThread.setDaemon(True)
        self.cmdThread.start()




if __name__ == "__main__":
    import time
    from helper import createPlayListEntry

    def screenSaver(mode):
        print("screensaver: mode = " + str(mode))

    def colorbar(mode):
        print("colorbar: mode = " + str(mode))

    def playerstartdummy(path, seek):
        print("player start called...")

    #Initialize the player core
    core = PlayerCore()
    core.activateColorBar = colorbar
    core.screenSaverRun = screenSaver
    #core.player.start = playerstartdummy

    testEnable = (1,0,0,0,0,0,0)

    def waitPlayer():
        while not core.isPlaying():
            time.sleep(0.25)

        while core.isPlaying():
            time.sleep(0.25)
            tmp = core.getRuntime()
            print("TMP Rntime = {}".format(tmp))
            print("CurrentFile = {}".format(core.getCurrentFile()))
            print("Total Time = {}".format(core.getTotalTime()))
            print("Is Pause = {}".format(core.isPaused()))
            print("Is Playing = {}".format(core.isPlaying()))

            #print(str(core.getRuntime()))

        time.sleep(1)

    #Test1: State machine test, single entry
    if testEnable[0] == 1:
        print("\n-------------- Test: Single start ---------------")
        core.startSingle("/home/thomas/Videos/a.mp4", 0)
        waitPlayer()


    #Test: play one file twice
    if testEnable[1] == 1:
        print("\n-------------- Test: Repeat once ---------------")
        pList = createPlayListEntry("/home/thomas/Videos/b.mov", 0, 27)
        pList[0]['post']="repeat_once"
        core.startPlaylist(pList)
        waitPlayer()#first playback
        waitPlayer()#secodn playback

    #Test: play one file until we die
    if testEnable[2] == 1:
        print("\n-------------- Test: Repeat forever ---------------")
        pList = createPlayListEntry("/home/thomas/Videos/b.mov", 0, 29)
        pList[0]['post']="repeat_forever"
        core.startPlaylist(pList)
        waitPlayer()
        waitPlayer()
        waitPlayer()
        waitPlayer()
        core.stop(None)

    #Test: test playlist multiple entries without waiting in between the playback
    if testEnable[3] == 1:
        pList = createPlayListEntry("/home/thomas/Videos/b.mov", 0, 25)
        pList.update(createPlayListEntry("/home/thomas/Videos/a.mp4", 1, 6))
        print(pList)
        core.startPlaylist(pList)
        waitPlayer()
        waitPlayer()

    #Test: Mixed playlist with audio and video
    if testEnable[4] == 1:
        pList = createPlayListEntry("/home/thomas/Videos/b.mov", 0, 25)
        pList.update(createPlayListEntry("/home/thomas/Music/a.mp3", 1, 9*60-10))
        pList.update(createPlayListEntry("/home/thomas/Videos/a.mp4", 2, 6))
        pList.update(createPlayListEntry("/home/thomas/Music/b.mp3", 3,  9*60+40))
        core.startPlaylist(pList)

        time.sleep(2)
        tmp = core.getRuntime()
        print("TMP Rntime = {}".format(tmp))


        waitPlayer()
        waitPlayer()
        waitPlayer()
        waitPlayer()

    #Previous and next control
    #
    if testEnable[5] == 1:
        pList = createPlayListEntry("/home/thomas/Videos/b.mov", 0, 25)
        pList.update(createPlayListEntry("/home/thomas/Music/a.mp3", 1, 9*60-10))
        pList.update(createPlayListEntry("/home/thomas/Videos/a.mp4", 2, 0))
        #pList.update(createPlayListEntry("/home/thomas/Music/b.mp3", 3,  0))
        core.startPlaylist(pList)

        #Firt b.mov is played
        time.sleep(4)

        #Execute previous, which should restart b.mov
        core.keyPrevious(None)
        time.sleep(4)
        # #exectue next which should play a.mp3
        core.keyNext(None)
        time.sleep(4)
        # #execute next which should play a.mp4
        core.keyNext(None)
        time.sleep(4)
        # # #execute next which should play b.mp4
        core.keyNext(None)
        time.sleep(4)
        # # #execute next which should stop the playback as there is nothing
        core.keyNext(None)
        time.sleep(4)

    #Enter key control when waiting in pre=blackscreen t play next
    #
    if testEnable[6] == 1:
        pList = createPlayListEntry("/home/thomas/Videos/b.mov", 0, 25)
        pList.update(createPlayListEntry("/home/thomas/Videos/a.mp4", 1, 6))
        pList[0]['pre'] = "blackscreen"
        pList[1]['pre'] = "blackscreen"
        core.startPlaylist(pList)

        time.sleep(5)
        core.keyEnter(None)

        waitPlayer()

        time.sleep(5)
        core.keyEnter(None)
        waitPlayer()

    while True:
        time.sleep(1)
        pass
