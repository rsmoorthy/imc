from selectables.file_list import fileListTest
import selectables.playlist_viewer as plviewer
import sys


if sys.argv[1] == "filelist":
    fileListTest()


if sys.argv[1] == "playlistview":
    plviewer.test()
