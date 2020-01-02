'''This is the main loop of the IshaPi player application'''
import logging
from kivy.app import App
from kivy.core.window import Window
from kivy.logger import Logger

from kivy.uix.screenmanager import ScreenManager, Screen, NoTransition

import os
import  http.server
import threading
import subprocess
import requests
import json
from functools import wraps
import time

from kivy.uix.stacklayout import StackLayout
from kivy.core.window import Window
from selectables.imc_tabview import ImcTabview
from selectables.menu_shutdown import MenuShutdown
from selectables.file_list import FileList
from player_core import PlayerCore
from selectables.playlist_viewer import PlaylistMenu

import control_tree
import includes
import audio_fader

from key_handler import KeyHandler
from control_tree import selectId as selectId
from screensaver import ScreenSaver
from ipc import Ipc
from selectables.menu_settings import MenuSettings
from selectables.menu_system import MenuSystem
from selectables.selectable_items import SelectableTabbedPanelHeader, SelectLabelBg

# from menu_video import FileList
# from menu_osd import MenuOSD, OsdController
# from menu_playlist import MenuPlaylist
# from key_handler import KeyHandler
# from dialog import DialogHandler
# from menu_shutdown import MenuShutdown
# import server

Logger.setLevel(logging.DEBUG) #TODO: for debuging Pi App should be able to change this

# Create the differten tab view objects like power off, menu  and screen saver screens
#
class IshaGui(StackLayout):
    '''This is the top object of the Gui'''

    def resize(self, widget, value):
        '''resize callback when width/height are chaning'''
        self.screens.height = Window.height - self.footer.height

    def changeFooterColor(self, mode):
        if mode == 0:
            self.footer.background_color = includes.styles['defaultBg']
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
            #logging.debug("_keyHandler: going to execute command = {}".format(cmd))
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

            #TODO: is this still needed?
            # #add user defined arguments of selectable widget to args passed to callback
            # if self.selectableWidgets[tmpId].user is not None:
            #     for item in self.selectableWidgets[tmpId].user:
            #         args[item] = self.selectableWidgets[tmpId].user[item]

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
            if self.playerControl.isPlaying():
                vol = audio_fader.getVolume()
                audio_fader.audioFadeout(10, 12, 15, 60, 40, 0.1)
                self.playerControl.stop(None)
                audio_fader.setVolume(vol)

            return

        if keycode[1] == "+":
            data = {}
            data['cmd'] = {'func':'volumeUp'}
            return

        if keycode[1] == "-":
            data = {}
            data['cmd'] = {'func':'volumeDown'}
            return

        if keycode[1] == "m":
            data = {"cmd": {"func": "muteToggle"}}
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

        if self.screenSaver.active and self.screenSaver.ena:
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
        self.menuVideo = FileList(
                #id="0",
                rootdir=includes.config['video']['rootdir'],
                enaColor=includes.styles['enaColor0'],
                bar_width=10,
                supportedTypes=includes.config['video']['types'],
                type="video",
                playerStartHandler=includes.playerCore.startPlaylist
        )
        self.setContent(selectId['videos'], self.menuVideo)

        #music File menu
        self.menuMusic = FileList(
                #id="0",
                rootdir=includes.config['music']['rootdir'],
                enaColor=includes.styles['enaColor0'],
                bar_width=10,
                supportedTypes=includes.config['music']['types'],
                type="music",
                playerStartHandler=includes.playerCore.startPlaylist
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
            player_start_handler=includes.playerCore,
        )
        self.setContent(selectId['playlist'], self.menuPlaylist)

        #Setup the settings screen
        self.menuSettings = MenuSettings()
        self.setContent(selectId['settings'], self.menuSettings)

        self.update(None)

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
