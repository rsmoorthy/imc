from selectables.file_list import fileListTest
import selectables.playlist_viewer as plviewer
from selectables.selectable_items import testImageBg
import sys


if sys.argv[1] == "filelist":
    fileListTest()


if sys.argv[1] == "playlistview":
    plviewer.test()


if sys.argv[1] == "imagebg":
    testImageBg()

if sys.argv[1] == "selectviewItem":
    from selectables.select_list_view import TestSelectListviewItem
    TestSelectListviewItem()
