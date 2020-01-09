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
        self.state = 0

    first = True
    mainWin = None
    def handleEvents(self):
        if self.display.pending_events() > 0:
            event = self.display.next_event()
        else:
            return

        if event.type == Xlib.X.ConfigureRequest:
            window = event.window
            args = { 'border_width': 3 }
            if event.value_mask & Xlib.X.CWX:
                args['x'] = event.x
            if event.value_mask & Xlib.X.CWY:
                args['y'] = event.y
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
            xClass = event.window.get_wm_class()
            self.windows[xClass[0]] = event.window
            logging.error(f"Thomas: map xClass = {xClass}")

            #Make main gui full screen
            if 'main_gui' in xClass[0]:
                event.window.map()
                event.window.configure(
                    width=self.displayWidth,
                    height=self.displayHeight,
                    x=0,
                    y=0
                )
                self.mainGuiMapped = True
                self.state = 1

            elif 'menu_osd' in xClass[0]:
                osdHeight = 55
                event.window.map()
                event.window.configure(
                    width=self.displayWidth,
                    height=osdHeight,
                    x=0,
                    y=self.displayHeight-osdHeight
                )
                self.osdWin = event.window
                self.osdBackground()

            else:
                #any other window will be just mapped fullscreen
                event.window.map()
                event.window.configure(
                    width=self.displayWidth,
                    height=self.displayHeight,
                    x=0,
                    y=self.displayHeight-osdHeight
                )



    def osdTop(self):
        try:
            window = self.windows['menu_osd']
            window.configure(stack_mode=Xlib.X.TopIf)
            self.display.sync()
        except:
            pass

    def osdBackground(self):
        try:
            window = self.windows['menu_osd']
            window.configure(stack_mode=Xlib.X.BottomIf)
            self.display.sync()
        except:
            pass


    def server(self):
        address = ('localhost', includes.config['ipcWmPort'])     # family is deduced to be 'AF_INET'
        listener = Listener(address, authkey=b'secret password')

        while True:
            #logging.error('before')
            conn = listener.accept()
            #logging.error('connection accepted from {}'.format(listener.last_accepted))

            while True:
                #logging.error('data =')
                try:
                    msg = conn.recv()
                    data = json.loads(msg)
                    #logging.error('data = {}'.format(data))

                    if 'cmd' in data:
                        cmd = data['cmd']

                        if cmd == 'osdTop':
                            self.osdTop()
                            #logging.error("Bring OSD to the top")

                        elif cmd == 'osdBackground':
                            self.osdBackground()
                            #logging.error("Bring OSD to the bot")

                except EOFError as e:
                    break

        listener.close()

    def main(self):

        self.thread = threading.Thread(target=self.server)
        self.thread.setDaemon(True)
        self.thread.start()

        self.handleActive = True

        while True:
            self.handleEvents()
            time.sleep(0.25)


def guiWorker():
    from main import Main
    Main().run()


if __name__ == "__main__":
    if len(sys.argv) == 2 and sys.argv[1] == "main_gui":
        print("Starting main_gui")
        main_gui.run()
        sys.exit(0)
    if len(sys.argv) == 2 and sys.argv[1] == "menu_osd":
        print("Starting menu_osd")
        menu_osd.run()
        sys.exit(0)

    wm = IshaWm()
    wmThread = threading.Thread(target=wm.main)
    wmThread.setDaemon(True)
    wmThread.start()

    while not wm.handleActive:
        time.sleep(0.1)


    guiPath = os.path.join(os.path.dirname(os.path.abspath(sys.argv[0])), "main_gui")
    guiPro = Popen(['python', guiPath, "main_gui"], stdin=sys.stdin, stdout=sys.stdout, stderr=sys.stdout)

    print("Started guiPro", sys.argv, guiPro, guiPath)
    while not wm.mainGuiMapped:
        time.sleep(0.1) #Wait so that everything opens in order
    print("Completed guiPro")

    osdPath = os.path.join(os.path.dirname(os.path.abspath(sys.argv[0])), "menu_osd")
    osdPro = Popen(['python', osdPath, "menu_osd"])
    print("Started osdPro")
    while wm.osdWin == None:
        time.sleep(0.1)
    print("Completed osdPro")


    print("Sleep check")
    time.sleep(5)
    while guiPro.poll() == None and osdPro.poll() == None:
        time.sleep(1)
    print("Sleep check done")

    if osdPro.poll() == None:
        osdPro.kill()

    if guiPro.poll() == None:
        guiPro.kill()
