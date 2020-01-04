'''This is the main loop of the IshaPi player application'''
import logging
import os
import threading
import time
import http.server

from kivy.app import App
from kivy.core.window import Window
from kivy.logger import Logger
from kivy.uix.stacklayout import StackLayout
from kivy.uix.screenmanager import ScreenManager, Screen, NoTransition
from kivy.core.window import Window

from selectables.imc_tabview import ImcTabview
from selectables.menu_shutdown import MenuShutdown
from selectables.file_list import FileList
from selectables.playlist_viewer import PlaylistMenu
from selectables.menu_video_audio import MenuVideoAudio
from selectables.menu_settings import MenuSettings
from selectables.menu_system import MenuSystem
from selectables.selectable_items import SelectLabelBg
from audio_controler import AudioController

import control_tree
import includes
import server

from menu_osd import OsdController
from player_core import PlayerCore
from key_handler import KeyHandler
from control_tree import selectId as selectId
from screensaver import ScreenSaver
from json_handler import  _addJsonSystemcall
from json_handler import  _systemCallbacks


#Logger.setLevel(logging.DEBUG) #TODO: for debuging Pi App should be able to change this

# Create the differten tab view objects like power off, menu  and screen saver screens
#
class IshaGui(StackLayout):
    '''This is the top object of the Gui'''

    def resize(self, widget, value):
        '''resize callback when width/height are chaning'''
        self.screens.height = Window.height - self.footer.height

    def changeFooterColor(self, mode):
        if mode == 0:
            self.footer.enaColor = includes.styles['defaultBg']
        elif mode == 1:
            self.footer.background_color = includes.styles['enaColor0']


    def __init__(self, **kwargs):
        includes.changeFooterColor = self.changeFooterColor

        super(IshaGui, self).__init__(**kwargs)

        self.screens = IshaPiScreens()

        self.footer = SelectLabelBg(
            background_color=includes.colors['black'],
            size_hint_y=None,
            height=includes.styles['pListIndiactorHeight']
        )


        self.screens.size_hint_y = None
        self.screens.height = Window.height - self.footer.height

        self.add_widget(self.screens)
        self.add_widget(self.footer)
        self.bind(height=self.resize)


class IshaPiScreens(ScreenManager):
    def __init__(self, **kwargs):
        super(IshaPiScreens, self).__init__(**kwargs)

        self.transition = NoTransition()
        self.menuScreenSaver = Screen(name="blackscreen")
        self.menuMainScreen = Screen(name="main_menu")
        self.shutdownScreen = Screen(name="shutdown")

        tabIds = [
            control_tree.selectId['system'],
            control_tree.selectId['videos'],
            control_tree.selectId['music'],
            control_tree.selectId['playlist'],
            control_tree.selectId['settings'],
        ]
        self.mainMenu = MainMenu(root=self, idList=tabIds)

        self.menuMainScreen.add_widget(self.mainMenu)
        self.add_widget(self.menuMainScreen)
        self.add_widget(self.menuScreenSaver)
        self.current = "main_menu"


class MainMenu(ImcTabview):

    _keyHandledMextId = False
    def _keyHandler(self, cmdList):
        #cmdList is a list of dictonaries containing the command being executed
        #cmdList can be specified as None in control tree which means nothing to do
        if cmdList is None:
            return

        for cmd in cmdList:
            #Check if cmd is also a list, if so recursively we will execute
            if isinstance(cmd, list):
                self._keyHandler(cmd)
                continue

            #last entry, this will stop execution
            if 'nextid' in cmd and  not self._keyHandledMextId:
                self._keyHandledMextId = True
                self.curId = cmd['nextid']
                return

            if not all(k in cmd for k in ("id", "func")):
                cmd = "_keyHandler: You did not specify id/func for tree elemnt "
                cmd = cmd + "with id = {} ".format(self.curId)
                logging.error(cmd)
                return

            tmpId = cmd['id']
            func = cmd['func']

            #args attribute is optional, can be used when we want to pass something to callback
            args = {}
            if 'args' in cmd:
                args = cmd['args']

            #Execute build in fucntions/object functions
            ret = getattr(self.selectableWidgets[tmpId], func)(args)

            if ret and 'true' in cmd: #execute ret functions if specified
                self._keyHandler(cmd['true'])

            if not ret and 'false' in cmd: #execute ret functions if specified
                self._keyHandler(cmd['false'])

    def _powerOffShowMenu(self):
        includes.screenSaver.disable()
        self.root.current = "shutdown"
        self.selectableWidgets[selectId['powermenu']].lastId = self.curId
        self.curId = selectId['powermenu']

    def _globalKeyHandler(self, keycode):
        """Key handler for global keys like volume up / volume down /mute etc."""

        if keycode[1] == "pgdown":
            if includes.playerCore.isPlaying():
                vol = self.audioController.getVolume()
                self.audioController.audioFadeout(10, 12, 15, 60, 40, 0.1)
                self.playerControl.stop(None)
                self.audioController.setVolume(vol)

            return

        if keycode[1] == "+":
            self.audioController.volumeUp()
            return

        if keycode[1] == "-":
            self.audioController.volumeDown()
            return

        if keycode[1] == "m":
            self.audioController.mute()
            return

        if keycode[1] == "power":
            if self.root.current != "shutdown":
                self._powerOffShowMenu()
            return


    # Callback function triggered by the key handler. This is triggered when
    #keyboard key is pressed.
    def _keyDown(self, keycode):
        '''Callback function for keyboard events. All key handling is done here.'''
        ret = self.keyDownSemaphore.acquire(False)

        msg = "Menu: Key Pressed [{}] ".format(keycode)
        msg = msg + "on element with curId = {}".format(self.curId)
        logging.debug(msg)

        if self.curId != selectId['osd']:
            if self.screenSaver.active and self.screenSaver.ena :
                self.screenSaver.resetTime()
                self.keyDownSemaphore.release()
                return 0

            self.screenSaver.resetTime()

        self._globalKeyHandler(keycode)

        if keycode[1] in self.controlTree[self.curId]:
            self._keyHandledMextId = False #prepare keyHandler function
            self._keyHandler(self.controlTree[self.curId][keycode[1]])
            self.keyDownSemaphore.release()
            return 0

        self.keyDownSemaphore.release()
        return -1

    # Osd related things
    #
    def osdDisable(self, args):
        '''Switch control back to last element after OSD was displayed'''
        self.curId = self.lastId

    def osdEnable(self, mode):
        '''Before switching to the OSD remember the current selected element'''
        self.lastId = self.curId
        self.curId = selectId[mode]

    @_addJsonSystemcall("_cmdMuteToggle")
    def _cmdMuteToggle(self, args):
        self.selectableWidgets[selectId['osd']].enable(None)
        self.ipc.sendCmd({'cmd':{'func':'muteToggle'}}, includes.config['ipcOsdPort'])


    def _server(self):
        ip = includes.config['httpServerIp']['ip']
        port = includes.config['httpServerIp']['port']
        self.httpd = http.server.HTTPServer((ip, int(port)), server.WebServer)

        try:
            self.httpd.serve_forever()
        except KeyboardInterrupt:
            pass
        finally:
            self.httpd.server_close()

    def __init__(self, **kwargs):
        self.selectableWidgets = {}
        self.keyDownSemaphore = threading.Semaphore()
        self.curId = 0
        self.controlTree = control_tree.CONTROL_TREE


        super(MainMenu, self).__init__(**kwargs)

        #setup the screen saver and also make it available as global object
        self.screenSaver = ScreenSaver(self.root, "blackscreen", "main_menu")
        includes.screenSaver = self.screenSaver

        #Setup the player core as global object
        includes.playerCore = PlayerCore(
            runtimeInterval=includes.config['settings']['runtimeInterval'],
            writeDb=includes.writeDb,
            db=includes.db
        )
        includes.playerCore.activateColorBar = includes.changeFooterColor
        includes.playerCore.screenSaverRun = self.screenSaver.start
        includes.playerCore.osdEnable = self.osdEnable
        includes.playerCore.osdDisable = self.osdDisable
        self.selectableWidgets[selectId['playerCore']] = includes.playerCore


        #Shutdown screen setup
        self.menuShutdown = MenuShutdown(screenManager=self.root)
        self.shutdownScreen = Screen(name="shutdown")
        self.shutdownScreen.add_widget(self.menuShutdown)
        self.root.add_widget(self.shutdownScreen)
        self.selectableWidgets[selectId['powermenu']] = self.menuShutdown

        #setup key handler
        self.keyHandler = KeyHandler()
        self.keyHandler.onPress = self._keyDown

        #System Menu setup
        self.menuSystem = MenuSystem(mainMenu=self)
        self.menuSystem.callbackPlaySingle = includes.playerCore.startSingle
        self.setContent(selectId['system'], self.menuSystem)

        #TODO:
        #for navigatiing in the system menu. TODO: This functionality should be moved to the menu system itself
        self.selectableWidgets[selectId['systemMsg']] = self.menuSystem.handler
        # self.selectableWidgets[selectId['systemBtn']] = self.menuSystem.btn

        #Video FIle menu
        self.menuVideo = MenuVideoAudio(
                #id="0",
                rootdir=includes.config['video']['rootdir'],
                enaColor=includes.styles['enaColor0'],
                bar_width=0,
                supportedTypes=includes.config['video']['types'],
                type="video",
                playerStartHandler=includes.playerCore.startPlaylist,
                line_color=includes.colors['imcBlue'],
                text="Video Files"
        )
        self.setContent(selectId['videos'], self.menuVideo)

        #music File menu
        self.menuMusic = MenuVideoAudio(
                #id="0",
                rootdir=includes.config['music']['rootdir'],
                enaColor=includes.styles['enaColor0'],
                bar_width=0,
                supportedTypes=includes.config['music']['types'],
                type="music",
                playerStartHandler=includes.playerCore.startPlaylist,
                line_color=includes.colors['imcBlue'],
                text="Music Files"
        )
        self.setContent(selectId['music'], self.menuMusic)

        #playlist menu
        self.menuPlaylist = PlaylistMenu(
            line_color_playlist=includes.colors['imcBlue'],
            line_color_media=includes.colors['imcLigthGray'],
            highlight_color=includes.styles['enaColor0'],
            line_height=6,
            bar_width=35,
            font_size=includes.styles['fontSize'],
            rootdir=includes.config['playlist']['rootdir'],
            supported_types=includes.config['playlist']['types'],
            player_start_handler=includes.playerCore.startPlaylist,
        )
        self.setContent(selectId['playlist'], self.menuPlaylist)

        #Setup the settings screen
        self.menuSettings = MenuSettings()
        self.setContent(selectId['settings'], self.menuSettings)

        self.update(None)

        #audio controller
        self.audioController = AudioController(
            includes.config['settings']['volIncVal'],
            self.volumeIndicator,
            False
        )

        vol = self.audioController.getVolume()

        _systemCallbacks['getVolume'] = self.audioController._getVolume
        self.volumeIndicator.value = vol

        #Setup the selectable widget object for key handling
        self.selectableWidgets[selectId['settings']] = self.getMenuBtn(selectId['settings'])
        self.selectableWidgets[selectId['videos']] = self.getMenuBtn(selectId['videos'])
        self.selectableWidgets[selectId['music']] = self.getMenuBtn(selectId['music'])
        self.selectableWidgets[selectId['playlist']] = self.getMenuBtn(selectId['playlist'])
        self.selectableWidgets[selectId['system']] = self.getMenuBtn(selectId['system'])
        self.selectableWidgets[selectId['root']] = self
        self.selectableWidgets[selectId['settingsMenu']] = self.menuSettings
        self.selectableWidgets[selectId['vFiles']] = self.menuVideo
        self.selectableWidgets[selectId['mFiles']] = self.menuMusic
        self.selectableWidgets[selectId['pFiles']] = self.menuPlaylist
        self.selectableWidgets[selectId['osd']] = OsdController()
        self.selectableWidgets[selectId['audioCtrl']] = self.audioController

        #Setup the server
        self.serverThread = threading.Thread(target=self._server)
        self.serverThread.setDaemon(True)
        self.serverThread.start()

        #prepare system for execution....
        self.screenSaver.enable()


        #Try to enable the start widget
        try:
            self.selectableWidgets[self.curId].enable(None)
        except Exception as allExceptions:
            logging.error("Menu: cannot find default widget...")

# Create the Kivy application
#
class Main(App):
    '''This is the main class for the IshaPi Player'''
    def build(self):
        return IshaGui()

def run():
    Main().run()

if __name__ == "__main__":
    run()
