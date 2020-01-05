import logging
import threading
import time
import queue
import os
import subprocess

from kivy.graphics import Color, Line, Rectangle
from kivy.app import App
from kivy.uix.widget import Widget
from kivy.uix.stacklayout import StackLayout
from kivy.uix.relativelayout import RelativeLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.properties import ObjectProperty
from kivy.core.window import Window

import includes
from helper import clipInt

from gui.images import ImageBg
from gui.labels import SelectLabelBg

class VolumeIndicator(RelativeLayout):
    value = ObjectProperty()

    def _changeValue(self, widget, value):
        value = clipInt(value, 0, 100)
        size = self.label1.size

        tmp = int(self.max * value / 100)
        self.label1.size = (tmp, size[1])

        if tmp == 0:
            self.image.imgSrc= "atlas://resources/img/pi-player/mute"
        else:
            self.image.imgSrc= "atlas://resources/img/pi-player/volume"

    def __init__(self, **kwargs):
        self.bgColor = kwargs.pop('bgColor', (0, 0, 0, 0))
        self.color = kwargs.pop('color', (1, 0, 0, 0))
        self.highlightColor = kwargs.pop('highlightColor', (0, 1, 0, 0))
        self.source = kwargs.pop('source', None)

        super(VolumeIndicator, self).__init__(**kwargs)

        #All these caluclation are experimental, for this scenario it worked,
        #nothing else has been tested.
        self.size_hint = (None, None)
        self.size = (160, 20)
        self.value = 0


        sizeImage = (20, 20)
        sizePadding = (2, 0)

        gap0 = 10
        barHeight = 16
        barHeight1 = 12
        borderWidth = int((barHeight - barHeight1 )/ 2)

        posLabel0 =(sizePadding[0] + sizeImage[0] + gap0,  int((sizeImage[1] - barHeight)/2))

        widthLabel0 = self.size[0] - sizeImage[0] - 2*sizePadding[0] - gap0
        sizeLabel0 = (widthLabel0, barHeight)

        posLabel1 = (posLabel0[0] + borderWidth, posLabel0[1] + borderWidth)
        sizeLabel1 = (sizeLabel0[0] - 2 * borderWidth, sizeLabel0[1] - 2 * borderWidth)

        self.image = ImageBg(
            background_color=self.bgColor,
            size_hint=(None, None),
            size=sizeImage,
            imgSrc="atlas://resources/img/pi-player/mute",
            pos=sizePadding
        )

        self.label0 = SelectLabelBg(
            background_color=self.color,
            size_hint=(None, None),
            size=sizeLabel0,
            pos=posLabel0,
        )

        self.label1 = SelectLabelBg(
            background_color=self.highlightColor,
            size_hint=(None, None),
            size=(0,12),
            pos=(32,4)
        )

        self.max = 126

        self.add_widget(self.image)
        self.add_widget(self.label0)
        self.add_widget(self.label1)

        self.bind(value=self._changeValue)

#
# Test function for the volume indicator
#
def TestVolumeIndicatorMain():
    from kivy.utils import get_color_from_hex as hexColor
    from time import sleep
    class Test(App):
        def _test(self):
            sleep(2)

            for i in range(-4, 104):
                self.indicator.value = i
                sleep(0.01)

            for i in range(0, 101):
                self.indicator.value = 100-i
                sleep(0.01)


        def build(self):
            self.indicator = VolumeIndicatorMain(
                color =  hexColor('#3d3d3d'),
                highlightColor = hexColor('#0f85a5')
            )


            #Start test thread
            self.th = threading.Thread(target=self._test)
            self.th.setDaemon(True)
            self.th.start()

            return self.indicator

    Test().run()
