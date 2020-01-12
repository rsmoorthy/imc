import logging

from gui.labels import SelectLabelBg
from kivy.uix.stacklayout import StackLayout
from kivy.properties import ObjectProperty

import includes
from helper import clipInt

class TimeSelect(StackLayout):
    text = ObjectProperty("00:00:00")

    def getTimeInSec(self):
        hours = int(self.hour0.text) * 10 + int(self.hour1.text)
        min = int(self.min0.text) * 10 + int(self.min1.text)
        sec = int(self.sec0.text) * 10 + int(self.sec1.text)
        return (hours * 3600 + min * 60 + sec)


    def _changeText(self, widget, value):
        if self.wId < 0 or self.wId >= len(self.widgets): #only when nothing is selected text is updated
            self.hour0.text = value[0]
            self.hour1.text = value[1]

            self.min0.text = value[3]
            self.min1.text = value[4]

            self.sec0.text = value[6]
            self.sec1.text = value[7]

    def enable(self, args):
        return self.right(args)

    def disable(self, args):
        return self.left(args)

    def clear(self, args):
        self.wId = -1
        for widget in self.widgets:
            if widget.isEnabled:
                widget.disable(None)

    def enter(self, args):
        self.onEnter(args)


    def onEnter(self, args):
        pass #empty callback can be set by top level module

    def up(self, args):
        value = int(self.widgets[self.wId].text)
        value = clipInt(value + 1, 0 , 9)
        self.widgets[self.wId].text = str(value)

    def down(self, args):
        value = int(self.widgets[self.wId].text)
        value = clipInt(value - 1, 0 , 9)
        self.widgets[self.wId].text = str(value)

    def left(self, args):
        if self.wId == 0:
            self.widgets[self.wId].disable(None)
            self.wId = -1
            return True
        else:
            if self.wId >= len(self.widgets):#this means we pressed overflowed right boundary
                self.wId = self.wId - 1
                self.widgets[self.wId].enable(None)
            elif self.wId > 0:
                self.widgets[self.wId].disable(None)
                self.wId = clipInt(self.wId - 1, 0, len(self.widgets)-1)
                self.widgets[self.wId].enable(None)

        return False

    lastIsDisabled = False
    def right(self, args):

        if self.wId < 0:
            self.wId = 0
            self.widgets[self.wId].enable(None)

        else:
            self.widgets[self.wId].disable(None)
            self.wId = clipInt(self.wId + 1, 0, len(self.widgets)-1)
            self.widgets[self.wId].enable(None)

            if self.wId == len(self.widgets)-1:
                return True

        return False

    def _setValues(self):
        pass

    def __init__(self, **kwargs):

        super(TimeSelect, self).__init__(**kwargs)

        numWidth = 16
        colWidth = 8
        numheight=self.height

        self.widgets = []
        self.wId = -1
        selWidget = None

        self.hour0 = SelectLabelBg(
            background_color=includes.styles['defaultBg'],
            enaColor=includes.styles['defaultEnaColor'],
            text=self.text[0],
            size_hint=(None, None),
            height=numheight,
            width=numWidth
        )

        self.hour1 = SelectLabelBg(
            background_color=includes.styles['defaultBg'],
            enaColor=includes.styles['defaultEnaColor'],
            text=self.text[1],
            size_hint=(None, None),
            height=numheight,
            width=numWidth
        )

        self.colon0= SelectLabelBg(
            background_color=includes.styles['defaultBg'],
            enaColor=includes.styles['defaultEnaColor'],
            text=":",
            size_hint=(None, None),
            height=numheight,
            width=colWidth
        )

        self.min0 = SelectLabelBg(
            background_color=includes.styles['defaultBg'],
            enaColor=includes.styles['defaultEnaColor'],
            text=self.text[3],
            size_hint=(None, None),
            height=numheight,
            width=numWidth
        )

        self.min1 = SelectLabelBg(
            background_color=includes.styles['defaultBg'],
            enaColor=includes.styles['defaultEnaColor'],
            text=self.text[4],
            size_hint=(None, None),
            height=numheight,
            width=numWidth
        )

        self.colon1= SelectLabelBg(
            background_color=includes.styles['defaultBg'],
            enaColor=includes.styles['defaultEnaColor'],
            text=":",
            size_hint=(None, None),
            height=numheight,
            width=colWidth
        )

        self.sec0 = SelectLabelBg(
            background_color=includes.styles['defaultBg'],
            enaColor=includes.styles['defaultEnaColor'],
            text=self.text[6],
            size_hint=(None, None),
            height=numheight,
            width=numWidth
        )

        self.sec1 = SelectLabelBg(
            background_color=includes.styles['defaultBg'],
            enaColor=includes.styles['defaultEnaColor'],
            text=self.text[7],
            size_hint=(None, None),
            height=numheight,
            width=numWidth
        )

        self.widgets.append(self.hour0)
        self.widgets.append(self.hour1)
        self.widgets.append(self.min0)
        self.widgets.append(self.min1)
        self.widgets.append(self.sec0)
        self.widgets.append(self.sec1)

        self.add_widget(self.hour0)
        self.add_widget(self.hour1)
        self.add_widget(self.colon0)
        self.add_widget(self.min0)
        self.add_widget(self.min1)
        self.add_widget(self.colon1)
        self.add_widget(self.sec0)
        self.add_widget(self.sec1)

        self.bind(text=self._changeText)


#
#---------------------------------------------------------------------
#
from kivy.app import App
from subprocess import threading
import time

class TestTimeSelect(App):
    obj = None

    def testThread(self):
        logging.error("Starting test.... obj = {}".format(self.obj))
        time.sleep(1)

        logging.error("testThread: first right....")

        for i in range(6):
            ret = self.obj.right(None)
            #time.sleep(1)

            for k in range(9):
                self.obj.up(None)
                time.sleep(0.1)

        logging.error("Last Ret right1 = {}".format(ret))
        ret = self.obj.right(None)
        ret = self.obj.right(None)
        time.sleep(1)
        logging.error("Last Ret right2 = {}".format(ret))
        ret = self.obj.left(None)
        logging.error("Last Ret right3 = {}".format(ret))


        for i in range(6):
            for k in range(9):
                self.obj.down(None)
                time.sleep(0.1)

            ret = self.obj.left(None)

        logging.error("Last Ret left1 = {}".format(ret))
        time.sleep(1)
        ret = self.obj.left(None)
        ret = self.obj.left(None)
        ret = self.obj.left(None)
        time.sleep(1)
        # logging.error("Last Ret left2 = {}".format(ret))
        ret = self.obj.right(None)
        # logging.error("Last Ret left3 = {}".format(ret))

        time.sleep(1)
        self.obj.text = "91:82:73"



    def build(self):
        self.obj = TimeSelect()

        thread = threading.Thread(target=self.testThread)
        thread.setDaemon(True)
        thread.start()


        return self.obj




if __name__ == "__main__":
    TestTimeSelect().run()
