import logging
import os
import json

from kivy.uix.gridlayout import GridLayout
from kivy.uix.stacklayout import StackLayout
from kivy.uix.label import Label
from kivy.graphics import Color, Line
from kivy.uix.relativelayout import RelativeLayout

from gui.labels import SelectLabelBg
from gui.file_list import FileList
from gui.select_list_view import SelectListView
import includes


class PlaylistViewHeader(GridLayout):
    def _changeSize(self, widget, size):

        s = self.line0.size
        line_width = (size[0] - self.label_width - 2*self.spacing[0]) / 2

        self.line0.marginD= int(size[1] / 2 - self.line_height / 2)

        self.line1.marginD= int(size[1] / 2 - self.line_height / 2)

        if self.bar_pos == "right":
            self.line0.size = (line_width, s[1])
            self.line1.size = (line_width-self.bar.width, s[1])
        else:
            self.line0.size = (line_width-self.bar.width, s[1])
            self.line1.size = (line_width, s[1])


    def __init__(self, **kwargs):
        self.line_color = kwargs.pop('line_color', (1,0,0,1))
        self.color = kwargs.pop('color', (1,1,1,1))
        self.text = kwargs.pop('text', "No Name defined")
        self.label_width = kwargs.pop('label_width', 250)
        self.line_height = kwargs.pop('line_height', 5)
        self.font_size = kwargs.pop('font_size', 5)
        self.bar_width = kwargs.pop('bar_width', 25)
        self.bar_pos = kwargs.pop('bar_pos', "right")

        super(PlaylistViewHeader, self).__init__(**kwargs)

        self.rows = 1

        self.label = Label(
            text=self.text,
            size_hint_x=None,
            width=self.label_width,
            font_size=self.font_size
        )

        line_width = (self.label_width - 2*self.spacing[0]) / 2

        self.line0 = SelectLabelBg(
            background_color=self.line_color,
            size_hint=(None,None),
            width=line_width,
            height=self.line_height,
            margin=(22,0,0,0),
        )

        self.line1 = SelectLabelBg(
            background_color=self.line_color,
            size_hint=(None,None),
            width=line_width,
            height=self.line_height,
        )

        self.bar = SelectLabelBg(
            background_color=self.line_color,
            size_hint=(None,None),
            width=self.bar_width,
            height=self.height/2 + self.line_height/2,
        )

        if self.bar_pos == "right":
            self.add_widget(self.line0)
            self.add_widget(self.label)
            self.add_widget(self.line1)
            self.add_widget(self.bar)
        else:
            self.add_widget(self.bar)
            self.add_widget(self.line0)
            self.add_widget(self.label)
            self.add_widget(self.line1)

        self.bind(size=self._changeSize)


class PlaylistFileContent(GridLayout):

    def __init__(self, **kwargs):
        self.defContent = Label(text="Please specify content in PlaylistFileView")
        self.content = kwargs.pop('content', self.defContent)
        self.bar_pos = kwargs.pop('bar_pos', 'right')
        self.line_color = kwargs.pop('line_color', (1,0,0,1))
        self.bar_width = kwargs.pop('bar_width', 25)

        super(PlaylistFileContent, self).__init__(**kwargs)
        self.rows = 1

        self.bar = SelectLabelBg(
            background_color=self.line_color,
            size_hint_x=None,
            width=self.bar_width,
        )

        if self.bar_pos == 'right':
            self.add_widget(self.content)
            self.add_widget(self.bar)
        else:
            self.add_widget(self.bar)
            self.add_widget(self.content)


class PlaylistFileView(StackLayout):

    def __init__(self, **kwargs):
        bar_width = 40
        self.defContent = Label(text="Please specify content in PlaylistFileView")
        self.content = kwargs.pop('content', self.defContent)
        self.bar_pos = kwargs.pop('bar_pos', 'right')
        self.line_color = kwargs.pop('line_color', (1,0,0,1))
        self.line_height = kwargs.pop('line_height', 6)
        self.bar_width = kwargs.pop('bar_width', 25)
        self.font_size = kwargs.pop('font_size', includes.styles['fontSize'])
        self.text = kwargs.pop('text', "unknown text")
        self.label_width= kwargs.pop('label_width', 250)

        super(PlaylistFileView, self).__init__(**kwargs)

        self.header = PlaylistViewHeader(
            line_height=self.line_height,
            line_color=self.line_color,
            font_size=self.font_size,
            bar_width=self.bar_width,
            bar_pos=self.bar_pos,
            height=50,
            size_hint_y=None,
            text=self.text,
            label_width=self.label_width,
        )

        self.cont0 = PlaylistFileContent(
            bar_width=self.bar_width,
            line_color=self.line_color,
            content=self.content,
            bar_pos=self.bar_pos
        )

        self.add_widget(self.header)
        self.add_widget(self.cont0)


class PlaylistMenu(GridLayout):
    _MODE_FILE = 0
    _MODE_MEDIA = 1


    def keyBack(self, args):
        self.keyLeft(args)

    def keyHome(self, args):
        self.isEnabled  = False
        self.playlistMediaFilesContent.deactivate(None)
        self.playlistFilesContent.disable(None)


    def keyEnter(self, args):
        if self.isEnabled:
            if self.mode == self._MODE_FILE:
                self.playlistFilesContent.keyEnter(None)

            elif self.mode == self._MODE_MEDIA:
                tmpData = self.playlistData
                newPlaylist = {}
                tmpRange = range(self.playlistMediaFilesContent.wId, len(self.playlistData))

                k = 0
                for i in tmpRange:
                    newPlaylist[str(k)] = (self.playlistData[str(i)])
                    k = k + 1

                self.player_start_handler(newPlaylist)




    def keyUp(self, args):
        if self.isEnabled:
            if self.mode == self._MODE_FILE:
                self.playlistFilesContent.keyUp(None)

            elif self.mode == self._MODE_MEDIA:
                self.playlistMediaFilesContent.keyUp(None)

    def keyDown(self, args):
        if self.isEnabled:
            if self.mode == self._MODE_FILE:
                self.playlistFilesContent.keyDown(None)

            elif self.mode == self._MODE_MEDIA:
                self.playlistMediaFilesContent.keyDown(None)

    def keyLeft(self, args):
        if self.isEnabled:
            if self.mode == self._MODE_FILE:
                return True

            elif self.mode == self._MODE_MEDIA:
                self.mode = self._MODE_FILE
                self.playlistMediaFilesContent.deactivate(None)
                self.playlistFilesContent.enable(False)


        return False

    def keyRight(self, args):
        if self.isEnabled:
            widCnt = len(self.playlistMediaFilesContent.widgets)

            if self.mode == self._MODE_FILE and widCnt > 0:
                self.mode = self._MODE_MEDIA
                self.playlistFilesContent.disable(None)
                self.playlistMediaFilesContent.activate(None)

            elif self.mode == self._MODE_MEDIA:
                self.mode = self._MODE_FILE

        return False

    def enable(self, args):
        self.mode = self._MODE_FILE
        self.isEnabled = True
        self.playlistFilesContent.enable(None)

    def disable(self,args):
        self.playlistFilesContent.disable(None)

        self.isEnabled = False


    def _updateJsonFiles(self, path):

        if os.path.isdir(path):
            return

        try:
            with open(path) as playFile:
                self.playlistData = json.load(playFile)
        except:
            logging.error("PlaylistMenu: updateJsonFiles: error in execution, most likely json file format error. path=".format(path))
            return False

        if self._validateJson(path) < 0:
            logging.error("PlaylistMenu: the Json file for selected playlist is not correct")
            return False

        self.playlistMediaFilesContent.layout.clear_widgets()
        self.playlistMediaFilesContent.wId = 0
        self.playlistMediaFilesContent.widgets = []

        for item in self.playlistData:
            if not os.path.isabs(self.playlistData[item]['path']):
                tmpPath = os.path.join(os.path.dirname(path), self.playlistData[item]['path'])
                self.playlistData[item]['path'] = tmpPath

            self.playlistMediaFilesContent.add(self.playlistData[item]['name'], False)

        return True


    def _validateJson(self, path):
        for i in range(len(self.playlistData)):
            if not str(i) in self.playlistData:
                msg = "PlayList: playlist file ids not correct, stopped at id = {}\n".format(i)
                msg = msg + "\tplaylistData = {} / i = {} \n".format(self.playlistData, i)
                msg = msg + "\tpath = {}".format(path)
                logging.error(msg)

                return -1

        i = 0
        for item in self.playlistData:
            if item != str(i):
                msg = "PlayList: playlist ids not in sequential order !\n"
                msg = msg + "\tpath = {}\n".format(path)
                msg = msg + "\tlist = {}\n".format(self.playlistData)
                msg = msg + "\t i = {}\n".format(i)
                logging.error(msg)
                return -2
            i = i + 1

        return 0


    def _playlistFilesOnEnter(self, path):
        '''This function is called when we press enter on the playlist file list
        It must return the dict object of the playlist that should be played'''
        ret = self._updateJsonFiles(path)
        if ret:
            return self.playlistData

        return None


    def _update_media_files(self, **kwargs):
        widget = kwargs.pop('widget', None)
        wId = kwargs.pop("wId", -1)

        path = self.playlistFilesContent._getCurPath()
        path = os.path.join(path, widget.text)

        if os.path.isdir(path) or widget.text == "...":
            self.playlistMediaFilesContent.clearWidgets()
            return

        ret = self._updateJsonFiles(path)

    def __init__(self, **kwargs):
        self.isEnabled = False

        self.line_color0 = kwargs.pop('line_color_playlist', (1,0,0,1))
        self.line_color1 = kwargs.pop('line_color_media', (1,0,0,1))
        self.highlight_color = kwargs.pop('highlight_color', (1,0,0,1))
        self.line_height = kwargs.pop('line_height', 6)
        self.bar_width = kwargs.pop('bar_width', 25)
        self.font_size = kwargs.pop('font_size', includes.styles['fontSize'])
        self.rootdir = kwargs.pop('rootdir', "")
        self.supported_types = kwargs.pop('supported_types', "txt")
        self.player_start_handler = kwargs.pop('player_start_handler', None)

        super(PlaylistMenu, self).__init__(**kwargs)
        self.rows = 1
        self.spacing = [10, 0]

        self.playlistFilesContent = FileList(
            rootdir=self.rootdir,
            enaColor=self.highlight_color,
            bar_width=10,
            supportedTypes=self.supported_types,
            type="playlist",
            plistHook=self._playlistFilesOnEnter,
            playerStartHandler=self.player_start_handler,
        )
        self.playlistFilesContent.keyDownHook = self._update_media_files
        self.playlistFilesContent.keyUpHook = self._update_media_files

        self.playlistMediaFilesContent = SelectListView(
            enaColor=self.highlight_color,
            bar_width=10,
        )

        self.playlistFiles = PlaylistFileView(
            line_color=self.line_color0,
            line_height=self.line_height,
            font_size=self.font_size,
            bar_width=self.bar_width,
            text="Playlist",
            label_width=150,
            content=self.playlistFilesContent,
        )

        self.mediaFiles = PlaylistFileView(
            bar_pos="left",
            line_color=self.line_color1,
            line_height=self.line_height,
            font_size=self.font_size,
            bar_width=self.bar_width,
            text="Media Files",
            label_width=200,
            content=self.playlistMediaFilesContent,
        )

        self.add_widget(self.playlistFiles)
        self.add_widget(self.mediaFiles)


def test():
    '''
    Standalone test:
    List and traverse /mnt/Ishamedia
    '''
    from kivy.core.window import Window
    from kivy.app import App

    class Main(App):
        def testFunc(self):
            import time
            time.sleep(0.5)

            self.menu.enable(None)
            time.sleep(0.5)

            self.menu.keyEnter(None)
            time.sleep(0.5)

            self.menu.keyDown(None)
            time.sleep(0.5)

            self.menu.keyRight(None)
            time.sleep(0.5)


            for i in range(9):
                self.menu.keyDown(None)
                time.sleep(0.5)

            self.menu.keyLeft(None)
            time.sleep(2)


            for i in range(10):
                self.menu.keyLeft(None)
                time.sleep(0.5)


            for i in range(10):
                self.menu.keyRight(None)
                time.sleep(0.5)


            self.menu.keyHome(None)
            time.sleep(0.5)
            #self.menu.playlistFilesContent.keyEnter(None)

        def build(self):

            def dummyPlay(self):
                logging.error("PlaylistViewer: Dummy play has been called...")

            self.menu = PlaylistMenu(
                line_color_playlist=includes.colors['imcBlue'],
                line_color_media=includes.colors['imcLigthGray'],
                highlight_color=includes.colors['oldblue'],
                line_height=6,
                bar_width=35,
                font_size=includes.styles['fontSize'],
                rootdir=includes.config['playlist']['rootdir'],
                supported_types=includes.config['playlist']['types'],
                player_start_handler=dummyPlay,
            )


            from  subprocess import threading

            workThread = threading.Thread(target=self.testFunc)
            workThread.setDaemon(True)
            workThread.start()


            return self.menu


    Main().run()
