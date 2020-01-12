'''
This is the implementation of the media players on screen display
to control the playback of the media files. The main object
is the MenuOSD() class which can be added to Kivy gui applications.

This creates a 50px high button bar, under under it a 5px high
border which color can be changed to display different states of
the software, e.g. the color could be changed to differentiate
between screen saver black screen and waiting for user inout during
playlist processing.
'''
import queue
import threading
import requests
import time
import os
import logging
from multiprocessing.connection import Client
# import pickle
import json

from kivy.uix.stacklayout import StackLayout
from kivy.uix.label import Label
from kivy.app import App
from kivy.core.window import Window
from kivy.uix.gridlayout import GridLayout

from gui.time_selector import TimeSelect
from gui.labels import SelectLabel, SelectLabelBg
from gui.buttons import SelectButton
from gui.volume_widget import VolumeIndicator


import includes
from ipc import Ipc
from key_handler import KeyHandler
from helper import clipInt

from default_requests import imcRequests


class OsdController():
    def left(self, args):
        self.ipc.sendCmd({'cmd':{'func':'left'}}, includes.config['ipcOsdPort'])

    def right(self, args):
        self.ipc.sendCmd({'cmd':{'func':'right'}}, includes.config['ipcOsdPort'])

    def enter(self, args):
        self.ipc.sendCmd({'cmd':{'func':'enter'}}, includes.config['ipcOsdPort'])

    def up(self, args):
        self.ipc.sendCmd({'cmd':{'func':'up'}}, includes.config['ipcOsdPort'])

    def down(self, args):
        self.ipc.sendCmd({'cmd':{'func':'down'}}, includes.config['ipcOsdPort'])

    def mute(self, args):
        self.ipc.sendCmd({'cmd':{'func':'mute'}}, includes.config['ipcOsdPort'])

    def volumeUp(self, args):
        self.ipc.sendCmd({'cmd':{'func':'volumeup'}}, includes.config['ipcOsdPort'])

    def volumeDown(self, args):
        self.ipc.sendCmd({'cmd':{'func':'volumedown'}}, includes.config['ipcOsdPort'])

    def disable(self, args):
        self.ipc.sendCmd({'cmd':{'func':'reset'}}, includes.config['ipcOsdPort'])

    def playPause(self, args):
        self.ipc.sendCmd({'cmd':{'func':'playPause'}}, includes.config['ipcOsdPort'])

    def videoEnd(self, args):
        self.ipc.sendCmd({'cmd':{'func':'videoend'}}, includes.config['ipcOsdPort'])


    def __init__(self):
        self.ipc = Ipc()

def TestOsdRemoteIf():
    import time
    osdc = OsdController()
    fct = [
        #osdc.left,
        osdc.right,
        # osdc.up,
        # osdc.down,
        # osdc.mute,
        # osdc.volumeUp,
        # osdc.volumeDown
    ]
    time.sleep(2)

    for i in range(15):
        osdc.right(None)
        time.sleep(0.5)
        # osdc.enter(None)
        # time.sleep(0.5)


    for i in range(4):
        osdc.up(None)
        time.sleep(0.5)

    for i in range(4):
        osdc.down(None)
        time.sleep(0.5)

    for i in range(11):
        osdc.left(None)
        time.sleep(0.5)


    time.sleep(3)
    logging.error("Mute.....")
    osdc.mute()



# Decorator for handler adding
#
_cmdHandler = {}
def _addHandler(url):
    def inner_decorator(f):
        _cmdHandler[url] = f
        return f
    return inner_decorator

class MenuOSD(StackLayout):
    '''On Screen Display (fixed height 50px (button height) + 5px (status border))'''

    def _sendPostRequest(self, data):
        try:
            ip = includes.config['httpServerIp']['ip']
            port = includes.config['httpServerIp']['port']

            url = 'http://{}:{}'.format(ip, port)
            req = requests.post(url, data=json.dumps(data))

            if req.status_code != 200:
                logging.error("_sendPostRequest: crequest error:: ret val = {}".format(req.status_code))

            return req
        except:
            return None

    @_addHandler("left")
    def left(self, state):

        ret = self.widgets[self.wId].disable(None)
        if ret:
            self.wId = clipInt(self.wId - 1, 0, len(self.widgets)-1)
            self.widgets[self.wId].enable(None)

        return state

    @_addHandler("right")
    def right(self, state):
        if self.widgets[self.wId] == self.runtime:
            self.widgets[self.wId].enable(None)
        else:

            self.widgets[self.wId].disable(None)
            self.wId = clipInt(self.wId + 1, 0, len(self.widgets)-1)
            ret = self.widgets[self.wId].enable(None)

        return state

    @_addHandler("enter")
    def enter(self, args):
        self.widgets[self.wId].enter(None)

    @_addHandler("up")
    def up(self, args):
        if self.widgets[self.wId] == self.runtime:
            self.runtime.up(None)


    @_addHandler("down")
    def down(self, args):
        if self.widgets[self.wId] == self.runtime:
            self.runtime.down(None)

    def _getVolume(self):
        try:
            req = imcRequests['Application']['GetProperties']
            ret = self._sendPostRequest(req).json()
            return int(ret['result']['volume'])
        except:
            return -1

    @_addHandler("mute")
    def mute(self, args):
        self.volumeTmp.value = self._getVolume()

    @_addHandler("volumeup")
    def volumeUp(self, args):
        self.volumeTmp.value = self._getVolume()

    @_addHandler("volumedown")
    def volumedown(self, args):
        self.volumeTmp.value = self._getVolume()

    def _visible(self, opac):
        for item in self.widgets:
            item.opacity = opac

        self.runtime.opacity = opac
        self.timeDivider.opacity = opac
        self.totaltime.opacity = opac

    def _osdWindowFront(self):
        logging.error("Thomas: _osdWindowFront")
        self.ipc.sendCmd({'cmd':'osdTop'},  includes.config['ipcWmPort'])

    def _osdWindowBack(self):
        logging.error("Thomas: _osdWindowBack")
        self.ipc.sendCmd({'cmd':'osdBackground'}, includes.config['ipcWmPort'])

    def _osdguiManager(self):
        '''
            Handles the display of all gui elements of the osd like displaying
            of elements based on idle timers etc. This state machine is non
            blocking so that it can be integrated in the same thread as the
            key handling
        '''
        lastTime = time.time()
        tValUpdate = time.time()
        volTime = 0 #time.time()
        volIsVisible = False
        state = "idle"
        lastState = "NONE"
        isVisible = False
        x11Visible = False
        while True:
            time.sleep(0.05)

            if volIsVisible or isVisible:
                if not x11Visible:
                    self._osdWindowFront()
                    x11Visible = True

            elif not volIsVisible and not isVisible:
                if x11Visible:
                    self._osdWindowBack()
                    x11Visible = False

            if time.time() - volTime < includes.config['settings']['osdTime']:
                if not volIsVisible:
                    self.volume.opacity = 1.0
                    self._osdWindowFront()
                    volIsVisible = True
            else:
                if self.volumeTmp.value != 0:
                    if volIsVisible:
                        self.volume.opacity = 0.0
                        volIsVisible = False
                        self._osdWindowBack()
                else:
                    if not volIsVisible:
                        volIsVisible = True
                        self.volume.opacity = 1.0
                        self._osdWindowFront()


            if int(time.time() - tValUpdate) > 0.8 and isVisible:
                self._setTimer()
                tValUpdate = time.time()

            if not self.ctrlQueue.empty():
                cmd = self.ctrlQueue.get()
                self.ctrlQueue.task_done()
                cmdVal = cmd['cmd']['func']

                if cmdVal == "reset":
                    state = "idle"
                    if self.widgets[self.wId] == self.runtime:
                        self.runtime.clear(None)
                    else:
                        self.widgets[self.wId] .disable(None)

                    self._visible(0.0)
                    self._osdWindowBack()
                    isVisible = False
                    continue

                elif cmdVal == "mute" or cmdVal == "volumeup" or cmdVal == "volumedown":
                    _cmdHandler[cmdVal](self, state)
                    volTime = time.time()
                    self._osdWindowFront()
                    continue

                elif cmdVal == "videoend":
                    self._osdWindowBack()
                    state = "idle"
                    cmd = None
                    self._visible(0.0)
                    isVisible = False
                    continue
                elif cmdVal == "playPause":
                    self.onEnterPlayPause(None)
                    continue

                lastTime = time.time()

                #Update the symbol of player button alternate play pause symbol
                self.btnPlayPause.imgSrc = self._getPlayPauseSource()

            else:
                cmd = None

            if state == "idle" and cmd is not None:
                #if not isVisible:
                isVisible = True
                self._visible(1.0)
                self._osdWindowFront()
                state = "visible"
                self.wId = 0
                self.widgets[0].enable(None)

            elif state == "visible":
                if cmd is not None:
                    tmpState = _cmdHandler[cmd['cmd']['func']](self, state)

                elif (time.time() - lastTime) > includes.config['settings']['osdTime']:
                    state = "idle"
                    if self.widgets[self.wId] == self.runtime:
                        self.runtime.clear(None)
                    else:
                        self.widgets[self.wId].disable(None)

                    self._visible(0.0)
                    self._osdWindowBack()
                    isVisible = False



    def _keyHandler(self):
        cmdServer = Ipc()
        cmdServer.serverInit(includes.config['ipcOsdPort'])

        while True:
            data = cmdServer.serverGetCmd()
            if 'cmd' in data:
                self.ctrlQueue.put(data)


    def onEnterPlayPause(self, args):
        try:
            '''Callback function which needs to execute pause fct of player'''
            if self._playerIsPlaying() and not self._playerIsPaused():
                self._sendPostRequest(imcRequests['Player']['Pause'])
            else:
                self._sendPostRequest(imcRequests['Player']['Play'])

            self.btnPlayPause.imgSrc = self._getPlayPauseSource()
        except:
            pass


    def onEnterPrevious(self, args):
        '''called when previous button on OSD is pressed'''
        self._sendPostRequest(imcRequests['Player']['Previous'])
        self.btnPrevious.disable(None)

    def onEnterNext(self, args):
        '''called when next button on OSD is pressed'''
        self._sendPostRequest(imcRequests['Player']['Next'])
        self.btnNext.disable(None)

    def onEnterStop(self, args):
        self._sendPostRequest(imcRequests['Player']['Stop'])
        self.btnStop.disable(None)
        self._osdWindowBack()

    def onEnterTimeselect(self, args):
        try:
            req = imcRequests['Player']['Seek']
            req['params']['start'] = self.runtime.getTimeInSec()
            self._sendPostRequest(req)

            self.ctrlQueue.put({'cmd':{'func':'reset'}})
        except:
            pass

    def _setTimer(self):
        try:
            req = imcRequests['Player']['GetProperties']
            req['params']['properties'] = ["time", "totaltime"]

            ret = self._sendPostRequest(req).json()


            time = ret['result']['time']
            tTime = ret['result']['totaltime']

            self.runtime.text = f"{time['hours']:02d}:{time['minutes']:02d}:{time['seconds']:02d}"
            self.totaltime.text = f"{tTime['hours']:02d}:{tTime['minutes']:02d}:{tTime['seconds']:02d}"
        except:
            pass


    def _playerIsPlaying(self):
        try:
            ret = self._sendPostRequest(imcRequests['Player']['IsPlaying']).json()
            if "result" in ret:
                return ret['result'] == 'True'
            else:
                return False
        except:
            return False

    def _playerIsPaused(self):
        try:
            ret = self._sendPostRequest(imcRequests['Player']['IsPaused']).json()
            if "result" in ret:
                return ret['result'] == 'True'
            else:
                return False
        except:
            return False

    def _getPlayPauseSource(self):
        if self._playerIsPlaying() and not self._playerIsPaused():
            srcPlay = "atlas://resources/img/pi-player/pause"
        else:
            srcPlay = "atlas://resources/img/pi-player/play"

        return srcPlay

    def changeSize(self, widget, value):
        '''resize the child attributes if widht or height changes'''
        winCenter = int(value[0] / 2)#int(Window.width / 2)
        delta = int((self.runtime.width + self.totaltime.width + self.timeDivider.width) / 2)
        winBoundaryLeft = winCenter - delta
        winBoundaryRight = winCenter + delta

        self.gap0.width = winBoundaryLeft-(5*self.btnNext.width)

        #-10 is for 10pixel gap on right side
        self.gap.width = value[0] - winCenter - delta - self.volume.width - 10

    def _addAllWidgets(self):
        '''Add all widgets to the OSD and hide them with opacity = 0'''
        self.widgets.append(self.btnPlayPause)
        self.widgets.append(self.btnStop)
        self.widgets.append(self.btnPrevious)
        self.widgets.append(self.btnNext)

        for wid in self.widgets:
             self.add_widget(wid)

        self.timeSelectId = len(self.widgets)

        self.add_widget(self.gap0)
        self.add_widget(self.runtime)
        self.widgets.append(self.runtime)
        self.add_widget(self.timeDivider)
        self.add_widget(self.totaltime)
        self.add_widget(self.gap)

        self.add_widget(self.volume)
        self.add_widget(self.colorIndicator)


    def __init__(self, **kwargs):
        self.widgets = []
        self.isVisible = False

        super(MenuOSD, self).__init__()

        self.btnPrevious = SelectButton(
            source="atlas://resources/img/pi-player/previous",
            size_hint_y=None,
            size_hint_x=None,
            height=50,
            width=50,
            enaColor=includes.styles['enaColor0'],
            background_color=includes.styles['defaultBg'],
            id=str(3)
        )
        self.btnPrevious.opacity = 0

        self.btnNext = SelectButton(
            source="atlas://resources/img/pi-player/next",
            size_hint_y=None,
            size_hint_x=None,
            height=50,
            width=50,
            enaColor=includes.styles['enaColor0'],
            background_color=includes.styles['defaultBg'],
            id=str(0)
        )
        self.btnNext.opacity = 0


        srcPlayPause = self._getPlayPauseSource()

        self.btnPlayPause = SelectButton(
            source=srcPlayPause,
            size_hint_y=None,
            size_hint_x=None,
            height=50,
            width=50,
            enaColor=includes.styles['enaColor0'],
            background_color=includes.styles['defaultBg'],
            id=str(2)
        )
        self.btnPlayPause.opacity = 0

        self.btnStop = SelectButton(
            source="atlas://resources/img/pi-player/stop",
            size_hint_y=None,
            size_hint_x=None,
            height=50,
            width=50,
            enaColor=includes.styles['enaColor0'],
            background_color=includes.styles['defaultBg'],
            id=str(3)
        )
        self.btnStop.opacity = 0

        self.runtime = TimeSelect(
            text="00:00:00",
            id=str(3),
            height=50,
            width=120,
            size_hint=(None, None)
        )
        self.runtime.opacity = 0

        self.timeDivider = SelectLabelBg(
            #text="|",
            width=3,
            height=50,
            size_hint=(None, None),
            background_color=includes.colors['oldblue'],
            size_hint_x=None,
        )
        self.timeDivider.opacity = 0

        self.totaltime = TimeSelect(
            text='{}'.format("11:22:33"),
            id=str(3),
            height=50,
            width=120,
            size_hint=(None, None),
            padding=[8,0,0,0]
        )
        self.totaltime.opacity = 0

        self.gap0 = SelectLabelBg(
            size_hint_y=None,
            size_hint_x=None,
            height=50,
            width=10,
            #background_color=(1,0,1,0.5)
        )
        self.gap0.opacity = 0

        self.gap = SelectLabelBg(
            size_hint_y=None,
            size_hint_x=None,
            height=50,
            #background_color=(0,1,1,0.5),
            width=10
        )
        self.gap.opacity = 0

        self.volumeTmp = VolumeIndicator(
            bgColor=includes.styles['defaultBg'],
            color = includes.colors['imcLigthGray'],
            highlightColor = includes.styles['enaColor0'],
        )
        self.volumeTmp.value = self._getVolume()

        #This grid layout is needed to aligh the VolumeIndicator as current implementation
        #has fixed dimensions ant this woild lool odd, just a work arround to position
        #the indicator nicely
        self.volume = GridLayout(
            rows=1,
            size_hint=(None, None),
            width=160,
            height=50,
            padding=[0, 15, 0 , 0],
        )
        self.volume.add_widget(self.volumeTmp)


        #add a colored 5px indicator bar at the bottom of the OSD to show status
        self.colorIndicator = SelectLabelBg(
            # height=50,#includes.styles['pListIndiactorHeight'],
            # size_hint_y=None,
            size_hint_x=None,
            width=Window.width,
            background_color=includes.colors['black'],
            id="-1",
            text=""
        )


        self._addAllWidgets()

        self.height = 50 + 5
        self.size_hint_y = None

        self.bind(size=self.changeSize)
        self.isVisible = False

        #Thread and queue handling
        self.ctrlQueue = queue.Queue()
        self.thread = threading.Thread(target=self._osdguiManager)
        self.thread.setDaemon(True)
        self.thread.start()

        self.wId = 0
        self.osdCtrl = OsdController()

        #self.btnPlay.onEnter =  self.onEnterPlay
        self.btnPlayPause.onEnter =  self.onEnterPlayPause
        self.btnPrevious.onEnter =  self.onEnterPrevious
        self.btnNext.onEnter = self.onEnterNext
        self.btnStop.onEnter =  self.onEnterStop
        self.runtime.onEnter = self.onEnterTimeselect

        #Server setup to control GUI elements on the OSD such as the volume indicator
        self.serverTr = threading.Thread(target=self._keyHandler)
        self.serverTr.setDaemon(True)
        self.serverTr.start()

        self.ipc = Ipc()


class OSDMain(App):

    def build(self):
        self.osd = MenuOSD()
        #self.osd._jsonCmdCallback = self.jsonCmdCallback
        return self.osd


#If we start OSD as standalone we use http request to control functions
def run():
    main = OSDMain()
#    Window.size = (Window.width, 50)
    main.run()

if __name__ == "__main__":
   run()
