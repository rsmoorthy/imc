from kivy.uix.gridlayout import GridLayout
import logging

from selectables.playlist_viewer import PlaylistFileView
from selectables.file_list import FileList
from includes import styles

class MenuVideoAudio(PlaylistFileView):
    def keyUp(self, args):
        return self.fList.keyUp(None)

    def keyEnter(self, args):
        return self.fList.keyEnter(None)

    def keyDown(self, args):
        return self.fList.keyDown(None)

    def enable(self, args):
        return self.fList.enable(None)

    def disable(self, args):
        return self.fList.disable(None)

    def keyHome(self, args):
        return self.fList.keyHome(None)

    def keyBack(self, args):
        return self.fList.keyBack(None)

    def _changeSize(self, widget, size):
        self.cont0.size_hint_y = None
        tmp = int((self.height-self.header.height) / styles['selectItemHeight']) + 1
        tmp = tmp * styles['selectItemHeight']
        self.cont0.height = tmp
    #    logging.error(f"Thomas: self.heigt = {self.height} |  header height = {self.header.height} | element height = {styles['selectItemHeight']}")

    def __init__(self, **kwargs):
        self.rootdir = kwargs.pop("rootdir", "/tmp")
        self.enaColor = kwargs.pop('enaColor', (1,0,0,1))
        self.supportedTypes = kwargs.pop('supportedTypes', "mp3,mp4")
        self.handler = kwargs.pop('playerStartHandler', None)
        self.type = kwargs.pop('type', "video")

        self.fList = FileList(
                rootdir=self.rootdir,
                enaColor=self.enaColor,
                bar_width=10,
                supportedTypes=self.supportedTypes,
                type=self.type,
                playerStartHandler=self.handler,
            )

        kwargs['content'] = self.fList

        super(MenuVideoAudio, self).__init__(**kwargs)


        self.bind(size=self._changeSize)
