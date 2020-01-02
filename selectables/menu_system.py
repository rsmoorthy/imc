import logging
import os
import time
import threading

from time import strftime, gmtime
from kivy.uix.stacklayout import StackLayout
from kivy.uix.label import Label
from kivy.uix.gridlayout import GridLayout

import includes
from selectables.dialog import DialogHandler, DialogButtons
from selectables.dialog import msgAutoRestart
from selectables.selectable_items import SelectLabelBg


class MenuSystem(StackLayout):
    def enable(self, args):
        if len(self.handler.children) > 0:
            return True

        return False

    def getIpAddress(self):
        import socket
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        try:
            s.connect(("8.8.8.8",1))
            myIp = s.getsockname()[0]
        except:
             myIp = "127.0.0.1"

        return myIp

    def callbackPlaySingle(self, args):
        logging.error("MenuSystem: callbackPlaySingle has not been assigned to player...")
        pass

    def getCpuTemp(self):#TODO: for pi we can use the command line tool provided
        dirname = "/sys/class/thermal/"
        dirs = os.listdir("/sys/class/thermal")
        #print(dirs)
        foundCpu = False
        i = 0
        for dir in dirs:
            path = os.path.join(dirname, dir)
            if "thermal_zone" in path:
                try:
                    with open(os.path.join(path, "type"), "r") as f:
                        tmp = f.readlines()
                        for line in tmp:
                            if "x86_pkg_temp" in line:
                                with open(os.path.join(path, "temp"), "r") as f:
                                    tmp = f.readline()

                                return int(tmp) / 1000
                except:
                    return -1


    def updateSystemValues(self):
        while True:
            time.sleep(1)

            temp = self.getCpuTemp()

            if temp < self.tmin:
                self.tmin = temp

            if temp > self.tmax:
                self.tmax = temp

            self.tcur = temp
            self.cpuTemp.text = "CPU:  [color=#0f85a5]{}°C[/color] | [color=#575757]{}°C[/color] | [color=#F15B28]{}°C[/color]".format(self.tmin, self.tcur, self.tmax)

            self.ipAddress.text="IP WiFi:  [color=#0f85a5]{}[/color]".format(self.getIpAddress())

            #Player values
            


    def _autoReplay(self, id):
        try:
            self.callbackPlaySingle(includes.db['mediaPath'], int(includes.db['runtime']))
            self.handler._removeDialog(self.systemCrashedId)
        except:
            logging.error("MenuSystem: could not start playback for auto restart")



    def _reboot(self, args):
        logging.error("TODO: reboot the system")
        #TODO: os.system("/sbin/reboot")

    def _shutdown(self, args):
        logging.error("Thomas:.........{}".format(self.mainMenu))
        self.mainMenu._powerOffShowMenu()

    def closeCrashMessage(self, args):
        if self.systemCrashHandl:
            self.systemCrashHandl(args)


    def __init__(self, **kwargs):
        self.fontSize = kwargs.pop('fontSize', 20)
        self.mainMenu = kwargs.pop("mainMenu", None)
        self.systemCrashedId = -1

        if self.mainMenu is None:
            logging.error("MenuSystem: __init__: mainMenu not defined....")
            return

        super(MenuSystem, self).__init__(**kwargs)


        self.headerMenu = GridLayout(
            rows = 1,
            spacing=[20],
            size_hint_y=None,
            height=50
        )

        temp = self.getCpuTemp()
        self.tmin = temp
        self.tmax = temp
        self.tcur = temp
        self.cpuTemp = Label(
            text="CPU:  [color=#0f85a5]{}°C[/color] | [color=#575757]{}°C[/color] | [color=#F15B28]{}°C[/color]".format(self.tmin, self.tcur, self.tmax),
            size_hint=(None,None),
            width=300,
            height=37.5,
            markup=True,
            font_size=self.fontSize,
        )
        self.headerMenu.add_widget(self.cpuTemp)

        self.ipAddress = Label(
            text="IP WiFi:  [color=#0f85a5]{}[/color]".format(self.getIpAddress()),
            markup=True,
            width=200,
            height=37.5,
            size_hint=(None, None),
            font_size=self.fontSize,
        )
        self.headerMenu.add_widget(self.ipAddress)
        self.add_widget(self.headerMenu)

        self.handler = DialogHandler()

        self.systemCrashedId = None
        self.systemCrashHandl = None




        if includes.db['runtime'] != 0:
            logging.error("------------------Thomas: runtime = {}".format(includes.db['runtime']))
            headerText = "System crashed"
            timeText = time.strftime('%H:%M:%S', time.gmtime(includes.db['runtime']))
            text = "System crashed while playing \n"
            text += "Timestamp = {}".format(timeText)

            nid = self.handler.getNextId()
            #logging.debug("MenuSystem: nid = {}".format(nid))
            tmpDialog = msgAutoRestart(self.handler, self._autoReplay, text, headerText, 90, nid)

            self.handler.add(tmpDialog[0])
            self.systemCrashedId = nid
            self.systemCrashHandl = tmpDialog[1]


        self.add_widget(self.handler)


        self.thread = threading.Thread(target=self.updateSystemValues)
        self.thread.setDaemon(True)
        self.thread.start()
