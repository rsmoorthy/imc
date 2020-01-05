import logging
import os
import sys

import includes
from helper import createPlayListEntry
from gui.select_list_view import SelectListView


class FileList(SelectListView):
    #Browser Back key pressed
    #
    def keyBack(self, args):

        if len(self.dirTree) >= 1:
            tmp = self.dirTree.pop(len(self.dirTree)-1)
            path = self._getCurPath()

            self.layout.clear_widgets()
            self.widgets = []

            isSubdir = len(self.dirTree) > 0
            self._addFiles(path, isSubdir)

            return False
        else:
            return True

    # Home key pressed
    #
    def keyHome(self, args):
        if len(self.dirTree) == 0:
            return True

        self.dirTree = []
        self.layout.clear_widgets()
        self.widgets = []
        self._addFiles(self.rootdir, False)

        return False

    def enable(self, args):
        if args is None:
            self.wId = 0

        self.isEnabled = True
        self.widgets[self.wId].enable(None)

    def disable(self, args):
        self.widgets[self.wId].disable(None)

    def keyEnter(self, args):
        #Get the path of currently selected file
        path = self._getCurPath()
        path = os.path.join(path, self.widgets[self.wId].text)



        #jump to previous directory, if we are in any sub directory
        if self.widgets[self.wId].text == "...":
            tmp = self.dirTree.pop(len(self.dirTree)-1)
            path = self.rootdir

            for item in self.dirTree:
                path = os.path.join(path, item)

            self.layout.clear_widgets()
            self.widgets = []

            isSubdir = len(self.dirTree) > 0
            self._addFiles(path, isSubdir)

        #We hit enter on a video/music file so play it
        elif os.path.isfile(path):
            playlist = {}

            # Create playlist, either with a single file or all files in teh directory
            #
            if self.type == "video" or self.type=="audio":
                if includes.config[self.type]['autoplay'] == 'true':
                    dirs, docs = self._getDirsAndDocs(os.path.dirname(path))
                    i = 0

                    found = False
                    for file in docs:
                        tmpPath = os.path.join(os.path.dirname(path), file)

                        if tmpPath == path or found:
                            found = True

                            playlist.update(
                                createPlayListEntry(tmpPath, i, 0)
                            )

                            i = i + 1

                else:
                    playlist.update(
                        createPlayListEntry(path, 0, 0)
                    )

            elif self.type == "playlist":
                if self.plistHook is not None:
                    playlist = self.plistHook(path)

            # Start playback
            #
            if self.playerStartList is not None:
                self.playerStartList(playlist)
            else:
                logging.error("FileList:: no playback handler defined")

        #If we selected directory we jump into it to see the file in it
        elif os.path.isdir(path):
            self.dirTree.append(self.widgets[self.wId].text)

            self.layout.clear_widgets()
            self.widgets = []

            self._addFiles(path, True)

    def _getDirsAndDocs(self, path):
        files = os.listdir(path)
        files.sort()

        dirs = []
        docs = []

        for item in files:
            tmpPath = os.path.join(path, item)
            if os.path.isdir(tmpPath):
                dirs.append(item)
            else:
                if item.lower().endswith(self.supportedTypes):
                    docs.append(item)

        return (dirs, docs)

    def _addFiles(self, path, isSubdir):
        '''
        Function that displays all supported media files and directories which
        are contained within the current directory.

        @path: the absolute path of the current view
        @isSubrid: indicator if the path is a subdirectory of the root, this
                   will allow us to display '...' as first element to go up one level


        1. It checks if the current path is a subdirectory or not
           If so it will add an element with name "..." as the first element
           This is needed for navigation purposes.

        2. Then we list and sort all files and directories in the path
           If it is a folder, we add widgets which display a folder symbol
           If it is a file we add widget which shows a file symbol.
           The text of the labels are set to the name of the files without any
           path information

        '''
        if isSubdir and self.showDirs:
            self.add("...", True)

        dirs = []
        docs = []

        dirs, docs = self._getDirsAndDocs(path)

        #add all directories first
        for item in dirs:
            self.add(item.strip(), isDir=True)

        #then add all the files
        for item in docs:
            self.add(item.strip(), False)

        if len(self.widgets) > 0:
            self.wId = 0
            self.scroll_to(self.widgets[self.wId], animate=False)

            if self.isEnabled:
                self.widgets[self.wId].enable(None)

    def _getCurPath(self):
        '''
        The self.rootdir object contains the root directory of the file list.
        From there we traverse the dirTree list which is a list of all subdirectories
        relative to the root dir in the current view. We combine these to get
        the absolute address
        '''
        path = self.rootdir

        for item in self.dirTree:
            path = os.path.join(path, item)

        return path

    def __init__(self, **kwargs):
        '''Initialize the needed variables and pop all arguments needed from kwargs'''
        self.rootdir = ""
        self.dirTree = []
        self.isEnabled = False

        self.rootdir = kwargs.pop('rootdir', None)

        if not os.path.exists(self.rootdir):
            logging.warning("FileList: root dir does not exist")


        self.showDirs = kwargs.pop('showDirs', True)

        self.supportedTypes = kwargs.pop('supportedTypes', "txt")
        logging.error("Supported files types {}".format(self.supportedTypes))


        self.supportedTypes = tuple(self.supportedTypes.split(','))

        self.type = kwargs.pop('type', "unknown")
        self.playerStartList = kwargs.pop('playerStartHandler', None)
        self.plistHook = kwargs.pop('plistHook', None)

        super(FileList, self).__init__(**kwargs)

        self.widgets = []
        self._addFiles(self.rootdir, False)
        self.wId = 0



def fileListTest():
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

            # #Select first element which should be a directory
            # self.fList.keyDown(None)
            # time.sleep(1)
            #
            # for i in range(55):
            #     self.fList.keyDown(None)
            #     time.sleep(0.1)

            for k in range(3):
                for i in range(2):

                    #enter in that directory
                    self.fList.keyEnter(None)
                    time.sleep(1)

                    #select in the second sub dir
                    self.fList.keyDown(None)
                    time.sleep(1)

                    #enter in second sub dir
                    self.fList.keyEnter(None)
                    time.sleep(1)

                    #go up one directory
                    self.fList.keyBack(None)
                    time.sleep(1)

                    #go up one directory
                    self.fList.keyBack(None)
                    time.sleep(1)

                #enter in that directory
                self.fList.keyEnter(None)
                time.sleep(1)

                #select in the second sub dir
                self.fList.keyDown(None)
                time.sleep(1)

                #enter in second sub dir
                self.fList.keyEnter(None)
                time.sleep(1)

                #go back to root
                self.fList.keyHome(None)
                time.sleep(1)



        def build(self):
            self.fList = FileList(
                id="0",
                rootdir="/mnt/Ishamedia/",
                enaColor=includes.styles['enaColor0'],
                bar_width=10,
                supportedTypes="mp3,mp4,txt",
                type="video"
            )

            from  subprocess import threading

            workThread = threading.Thread(target=self.testFunc)
            workThread.setDaemon(True)
            workThread.start()

            from kivy.uix.stacklayout import StackLayout

            lay = StackLayout()
            lay.add_widget(self.fList)
            return lay

            return self.fList
    Main().run()
