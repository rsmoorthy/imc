#!/home/pi/.local/share/virtualenvs/imc-zc-BRSxn/bin/python
import Xlib
import Xlib.display
import logging
import json
import time

import includes
import main_gui
import menu_osd
import os
import sys
from ipc import Ipc

from  subprocess import Popen, threading
from multiprocessing.connection import Listener

class IshaWm():
    displayWidth = None
    displayHeight = None
    display = None
    root = None
    activeWindow = None
    osdWin = None
    windows = {}


    def __init__(self):
        self.display = Xlib.display.Display()
        self.root = self.display.screen().root
        self.displayWidth = self.root.get_geometry().width
        self.displayHeight = self.root.get_geometry().height
        self.root.change_attributes(event_mask = Xlib.X.SubstructureRedirectMask)
        self.handleActive = False
        self.mainGuiMapped = False
        self.osdWin = None
        self.state = 0

    first = True
    mainWin = None
    def handleEvents(self):
        event = self.display.next_event() #TODO: would this block and wait for an event?

        if event.type == Xlib.X.ConfigureRequest:
            window = event.window
            args = { 'border_width': 3 }
            if event.value_mask & Xlib.X.CWX:
                args['x'] = 0 #event.x
            if event.value_mask & Xlib.X.CWY:
                args['y'] = 0 #event.y
            if event.value_mask & Xlib.X.CWWidth:
                args['width'] = event.width
            if event.value_mask & Xlib.X.CWHeight:
                args['height'] = event.height
            if event.value_mask & Xlib.X.CWSibling:
                args['sibling'] = event.above
            if event.value_mask & Xlib.X.CWStackMode:
                args['stack_mode'] = event.stack_mode
            window.configure(**args)


        if event.type == Xlib.X.MapRequest:
            try:
                xClass = event.window.get_wm_class()

                #Make main gui full screen
                if not self.mainGuiMapped or 'main_gui' in xClass[0]:
                    event.window.map()
                    event.window.configure(
                        width=self.displayWidth,
                        height=self.displayHeight,
                        x=0,
                        y=0
                    )
                    self.mainGuiMapped = True
                    self.state = 1
                    self.windows['main_gui'] = event.window

                elif (self.mainGuiMapped or 'menu_osd' in xClass[0]) and self.osdWin is None:
                    osdHeight = 55
                    event.window.map()
                    event.window.configure(
                        width=self.displayWidth,
                        height=osdHeight,
                        x=0,
                        y=self.displayHeight-osdHeight
                    )
                    self.osdWin = event.window
                    self.windows['menu_osd'] = event.window
                    self.osdBackground()

                else:
                    #any other window will be just mapped fullscreen
                    event.window.map()
                    event.window.configure(
                        width=self.displayWidth,
                        height=self.displayHeight,
                        x=0,
                        y=0
                    )
                    self.display.flush()
            except:
                logging.warning("X11WindowManager: some error occured in window mapping...")



    def osdTop(self):
        window = self.windows['menu_osd']
        window.configure(stack_mode=Xlib.X.TopIf)
        self.display.flush()


    def osdBackground(self):
        window = self.windows['menu_osd']
        window.configure(stack_mode=Xlib.X.BottomIf)
        self.display.flush()



    def server(self):
        cmdServer = Ipc()
        cmdServer.serverInit(includes.config['ipcWmPort'])
        while True:
            data = cmdServer.serverGetCmd()
            if 'cmd' in data:
               if 'cmd' in data:
                    cmd = data['cmd']

                    if cmd == 'osdTop':
                        self.osdTop()
                        #logging.error("Bring OSD to the top")

                    elif cmd == 'osdBackground':
                        self.osdBackground()



    def main(self):
        self.thread = threading.Thread(target=self.server)
        self.thread.setDaemon(True)
        self.thread.start()

        self.handleActive = True

        while True:
            self.handleEvents()
            #time.sleep(0.01)


def guiWorker():
    from main import Main
    Main().run()


if __name__ == "__main__":
    if len(sys.argv) == 2 and sys.argv[1] == "main_gui":
        main_gui.run()
        sys.exit(0)
    if len(sys.argv) == 2 and sys.argv[1] == "menu_osd":
        menu_osd.run()
        sys.exit(0)

    wm = IshaWm()
    wmThread = threading.Thread(target=wm.main)
    wmThread.setDaemon(True)
    wmThread.start()

    while not wm.handleActive:
        time.sleep(0.1)


    guiPath = os.path.join(os.path.dirname(os.path.abspath(sys.argv[0])), "main_gui")
    guiPro = Popen([guiPath, "main_gui"], stdin=sys.stdin, stdout=sys.stdout, stderr=sys.stdout)

    while not wm.mainGuiMapped:
        time.sleep(0.1) #Wait so that everything opens in order

    osdPath = os.path.join(os.path.dirname(os.path.abspath(sys.argv[0])), "menu_osd")
    osdPro = Popen([osdPath, "menu_osd"])

    while wm.osdWin == None:
        time.sleep(0.1)

    wm.osdBackground()

    print("Sleep check")
    time.sleep(5)
    wm.osdBackground()
    while guiPro.poll() == None and osdPro.poll() == None:
        time.sleep(1)
        #wm.osdBackground()
        time.sleep(1)
        #wm.osdTop()

    print("Sleep check done")

    if osdPro.poll() == None:
        osdPro.kill()

    if guiPro.poll() == None:
        guiPro.kill()
