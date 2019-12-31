import logging
import os
import json

from kivy.uix.gridlayout import GridLayout
from kivy.uix.stacklayout import StackLayout
from kivy.uix.label import Label
from kivy.graphics import Color, Line
from kivy.uix.relativelayout import RelativeLayout

from selectables.selectable_items import SelectLabelBg
from selectables.file_list import FileList
from selectables.select_list_view import SelectListView
import includes


class PlaylistViewHeader(GridLayout):
    def _changeSize(self, widget, size):
        logging.error("size changed.... {}".format(size))

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
        logging.error(line_width)

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

        logging.error(self.content)
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

    def _updateJsonFiles(self, path):

        #path = os.path.join(includes.config['playlist']['rootdir'], fileName)

        if os.path.isdir(path):
            return
        try:
            with open(path) as playFile:
                self.playlistData = json.load(playFile)
        except:
            logging.error("PlaylistMenu: updateJsonFiles: error in execution, most likely json file format error ....")
            return False

        if self._validateJson(path) < 0:
            logging.error("PlaylistMenu: the Json file for selected playlist is not correct")
            return False

        self.playlistMediaFilesContent.layout.clear_widgets()
        self.playlistMediaFilesContent.wId = 0
        self.playlistMediaFilesContent.widgets = []

        for item in self.playlistData:
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
            self._validateJson(path)

        return None

    def __init__(self, **kwargs):
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












# class PlaylistViewer(StackLayout, Select):
#     def size_change(self, widget, size):
#         columnWidth0 = size[0] * 0.3
#         columnWidth1 = size[0] - columnWidth0
#
#         headerHeight = includes.styles['playlistHeadHeight']
#
#         self.header0.size = (columnWidth0, headerHeight)
#         self.header1.size = (columnWidth1, headerHeight)
#
#         self.fileList.size = (columnWidth0, size[1])
#         self.files.size = (columnWidth1, size[1])
#
#
#     def pos_change(self, widget, value):
#         pass
#
#
#     def keyDown(self, args):
#         if self.fileList.widgets is None or len(self.fileList.widgets) <= 0:
#             return True
#
#         if self.mode == self._fileList  and len(self.fileList.widgets) > 0:
#             tmpId = self.fileList.wId + 1
#
#             if tmpId == len(self.fileList.widgets):
#                 tmpId = tmpId - 1
#
#             self.updateJsonFiles(self.fileList.widgets[tmpId].text)
#             ret = self.fileList.enable(None)
#
#             return ret
#
#         elif self.mode == self._jsonList:
#             self.files.enable(None)
#             return False
#
#         return False
#
#     def keyUp(self, args):#up
#         if self.fileList.widgets is None or len(self.fileList.widgets) <= 0:
#             return True
#
#         if self.mode == self._fileList and len(self.fileList.widgets) > 0:
#             tmpId = self.fileList.wId - 1
#             if tmpId < 0:
#                 tmpId = 0
#
#
#             self.updateJsonFiles(self.fileList.widgets[tmpId].text)
#
#             return self.fileList.disable(None)
#
#         elif self.mode == self._jsonList:
#             self.files.disable({'disTop':False})
#             return False
#
#         return False
#
#     def disableAll(self, args):
#         for wid in self.fileList.widgets:
#             wid.disable(None)
#
#
#     def keyLeft(self, args):
#         if self.mode == self._fileList:
#
#             return True
#
#         elif self.mode == self._jsonList:
#             self.mode = self._fileList
#
#             for wid in self.files.widgets:
#                 wid.disable({'inc':False})
#
#             self.files.wId = -1
#
#         return False
#
#     def keyRight(self, args):
#         if args is not None:
#             enableFilesView = args.pop('enableFilesView', True)
#         else:
#             enableFilesView = True
#
#         if self.mode == self._fileList and len(self.fileList.widgets) > 0:
#             self.mode = self._jsonList
#
#             self.files.wId = -1
#             if enableFilesView:
#                 self.files.enable(None)
#
#         elif self.mode == self._jsonList:
#             pass
#
#     def _validateJson(self, path):
#         for i in range(len(self.pList)):
#             if not str(i) in self.pList:
#                 msg = "PlayList: playlist file ids not correct, stopped at id = {}\n".format(i)
#                 msg = msg + "\tplist = {} / i = {} \n".format(self.pList, i)
#                 msg = msg + "\tpath = {}".format(path)
#                 logging.error(msg)
#
#                 return -1
#
#         i = 0
#         for item in self.pList:
#             if item != str(i):
#                 msg = "PlayList: playlist ids not in sequential order !\n"
#                 msg = msg + "\tpath = {}\n".format(path)
#                 msg = msg + "\tlist = {}\n".format(self.pList)
#                 msg = msg + "\t i = {}\n".format(i)
#                 logging.error(msg)
#                 return -2
#             i = i + 1
#
#         return 0
#
#
#     def updateJsonFiles(self, text):
#         path = os.path.join(includes.config['playlist']['rootdir'], text)
#
#         if os.path.isdir(path):
#             return
#
#         with open(path) as playFile:
#             self.pList = json.load(playFile)
#
#         if self._validateJson(path) < 0:
#             logging.error("MenuPlaylist: the Json file for selected playlist is not correct")
#             return
#
#         self.files.layout.clear_widgets()
#         self.files.wId = -1
#         self.files.widgets = []
#
#         for item in self.pList:
#             self.files.add(self.pList[item]['name'], False)
#
#
#     def keyEnter(self, args):
#         if args is not None:
#             mode = args.pop('mode', "json")
#         else:
#             mode = "json"
#
#         self.ctrlQueue.put({
#             'cmd':{'mode':mode, 'key':'enter'}})
#
#     _fileList = 0 #Not nice, really needed?
#     _jsonList = 1 #Not nice, really needed?
#
#     def __init__(self, **kwargs):
#         #pList = None #TODO Needed?
#
#
#         self.selId = kwargs.pop('id', None)
#         self.screenmanager = kwargs.pop('screenmanager', None)
#
#         super(MenuPlaylist, self).__init__(**kwargs)
#
#         self.cols = 2
#         self.rows = 2
#
#         columnWidth0 = Window.width * 0.3
#         columnWidth1 = Window.width-columnWidth0
#         headerHeight = includes.styles['playlistHeadHeight']
#         headerText0 = "[b]Playlists[/b]"
#         headerText1 = "[b]Media Files[/b]"
#
#         self.header0 = SelectLabelBg(
#             background_color=includes.styles['headerColor0'],
#             text_size=(columnWidth0-20, headerHeight),
#             text=headerText0,
#             halign="center",
#             valign="middle",
#             size_hint_y=None,
#             size_hint_x=None,
#             height=headerHeight,
#             width=columnWidth0,
#             id="-1",
#             markup=True
#         )
#         self.add_widget(self.header0)
#
#         self.header1 = SelectLabelBg(
#             background_color=includes.styles['headerColor1'],
#             text_size=(columnWidth0-20, headerHeight),
#             text=headerText1,
#             halign="center",
#             valign="middle",
#             size_hint_y=None,
#             size_hint_x=None,
#             height=headerHeight,
#             width=columnWidth1,
#             id="-1",
#             markup=True
#         )
#
#         self.add_widget(self.header1)
#
#         self.fileList = FileList(
#             id=str(int(self.selId)+1),
#             rootdir=includes.config['playlist']['rootdir'],
#             enaColor=includes.styles['enaColor0'],
#             bar_width=10,
#             size_hint_x=None,
#             width=columnWidth0,
#             supportedTypes=includes.config['playlist']['types'],
#             #screenmanager=self.screenmanager,
#             fillerColor=includes.styles['headerColor0'],
#             showDirs=False,
#             selectFirst=False,
#             showIcon=False,
#         )
#
#         self.files = PlaylistJsonList(
#             id=str(int(self.selId) + 5000),
#             enaColor=includes.styles['enaColor1'],
#             bar_width=10,
#             size_hint_x=None,
#             width=columnWidth1,
#             fillerColor=includes.styles['headerColor1'],
#             showIcon=False,
#         )
#
#         self.add_widget(self.fileList)
#         self.add_widget(self.files)
#
#         self.mode = self._fileList
#
#         self.bind(size=self.size_change)
#         self.bind(size=self.pos_change)



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
            time.sleep(2)

            self.menu.playlistFilesContent.keyEnter(None)
            self.menu.playlistFilesContent.keyDown(None)
            self.menu.playlistFilesContent.keyEnter(None)

        def build(self):

            bar_width = 40
            self.header = PlaylistViewHeader(
                line_height=6,
                spacing =  [0,0],
                line_color=includes.colors['oldblue'],
                font_size=includes.styles['fontSize'],
                bar_width=bar_width,
                height=50,
                size_hint_y=None,
            )
            # self.header.size_hint_y = None
            # self.header.height = 50

            self.cont0 = PlaylistFileContent(
                bar_width=bar_width,
                line_color=includes.colors['oldblue'],
            )

            stack = StackLayout()
            stack.add_widget(self.header)
            stack.add_widget(self.cont0)

            self.fview = PlaylistFileView()

            def dummyPlay(self):
                logging.error("Dummy play has been called...")

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
            #return self.fview
            # return stack
            #return self.cont0
            # return self.header

    Main().run()
