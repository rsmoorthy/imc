from gui.file_list import fileListTest
import gui.playlist_viewer as plviewer
from gui.selectable_items import testImageBg
import sys


if sys.argv[1] == "filelist":
    fileListTest()


if sys.argv[1] == "playlistview":
    plviewer.test()


if sys.argv[1] == "imagebg":
    testImageBg()

if sys.argv[1] == "selectviewItem":
    from gui.select_list_view import TestSelectListviewItem
    TestSelectListviewItem()

if sys.argv[1] == "osdctrl":
    from menu_osd import TestOsdRemoteIf
    TestOsdRemoteIf()

if sys.argv[1] == "volumemain":
    from gui.volume_widget import TestVolumeIndicatorMain as test
    test()
