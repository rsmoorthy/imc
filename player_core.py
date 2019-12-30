import mpv_player
import vlc_player
import mpv_player_v0
import time
import threading
import logging

from queue import Queue
from helper import synchronized, createPlayListEntry, checkPlaylist
# import logging


class PlayerCore():
    #Static variables
    #
    playerSync = threading.Semaphore()

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
        self.cmdQueue.put({'cmd':'end'})


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
        return not self.player.isPlaying()

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
        self.cmdQueue.put({'cmd':'stop'})

    @synchronized(playerSync)
    def seek(self, time):
        self.player.seek(time)

    @synchronized(playerSync)
    def startSingle(self, path, tStart):
        playlist = createPlayListEntry(path, 0, tStart)
        self.cmdQueue.put({'cmd':'play', 'playlist':playlist})
        #sTODO: put playlist in queue for processing

    @synchronized(playerSync)
    def startPlaylist(self, playlist):
        self.cmdQueue.put({'cmd':'play', 'playlist':playlist})

    # Ques command interface to request functions of core player from multipe proceses
    #
    def _playlistWork(self):
        enter = stop = next = previous = play = end = once = False
        state = "idle"
        lastState = "idle"
        entry = None
        entryId = 0

        # try:
        while True:
            #read next entry of queue blocking style
            time.sleep(0.25)
            if not self.cmdQueue.empty():
                cmd = self.cmdQueue.get()

                if cmd['cmd'] == "enter":
                    enter = True

                elif cmd['cmd'] == "stop":
                    play = False #stop plalist
                    self.activateColorBar(0)
                    self.screenSaverRun(0)
                    self.player.stop()
                    enter = stop = next = previous = play = end = once = False
                    entry = None
                    entryId = 0
                    state = "idle"
                    play = False

                elif cmd['cmd'] == "previous":
                    previous = True

                elif cmd['cmd'] == "next":
                    next = True

                elif cmd['cmd'] == "end":
                    end = True

                elif cmd['cmd'] == "play":
                    if not play:
                        playlist = cmd['playlist']
                        check = checkPlaylist(playlist)
                        if check[1] == 0:
                            play = True
                        else:
                            logging.error("PlayerCore: playlist format error = {}".format(check))

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
                    entry = playlist[entryId]
                    logging.debug("EntryyId play: {}".format(entryId))

            elif state == "pre":
                if type(entry['pre']) == str and entry['pre'].lower() == "blackscreen":
                    self.activateColorBar(1)
                    self.screenSaverRun(1)
                    state = "preWait"

                else:
                    state = "play"

            elif state == "preWait":
                if enter:
                    enter = False
                    state = "play"

            elif state == "play":
                path = entry['path']
                tSeek = entry['start']
                self.player.start(path, tSeek)
                state = "waitEnd"

            elif state == "waitEnd":
                if previous:
                    state = "play"
                elif next:
                    state = "end"
                elif end:
                    end = False
                    state = "post"

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
                    entryId = entryId + 1
                    logging.debug("PLayerCore: entryId = {}".format(entry))
                    if entryId >= len(playlist):
                            play = False #stop plalist
                            self.activateColorBar(0)
                            self.screenSaverRun(1) #Stay on screen saver
                            enter = stop = next = previous = play = end = once = False
                            entry = None
                            entryId = 0

                    state = "idle"
                    end = False


    def __init__(self, **kwargs):
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
    # logging.basicConfig(level=logging.DEBUG)
    # import faulthandler
    # faulthandler.enable()

    import time

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

    testEnable = (0,0,0,0,1)

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
        pList.update(createPlayListEntry("/home/thomas/Music/b.mp3", 3,  9*60-10))
        core.startPlaylist(pList)

        time.sleep(2)
        tmp = core.getRuntime()
        print("TMP Rntime = {}".format(tmp))


        waitPlayer()
        waitPlayer()
        waitPlayer()
        waitPlayer()


    #Test5: use faulty playlists



    while True:
        time.sleep(1)
        pass
