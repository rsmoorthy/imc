import sys
import os
import logging

from kivy.uix.gridlayout import GridLayout
from kivy.uix.checkbox import CheckBox
from kivy.app import App

from gui.spinners import SelectSpinner, SelectSpinnerBool
from gui.labels import SelectLabel, SelectLabelBg
from gui.buttons import SelectButton

import includes
from helper import rotateInt, getDisplaySize

class MenuSettings(GridLayout):
    widgets = []
    wId = 0
    widName = []
    btnOff = None

    def activate(self, args):
        self.wId = 0
        self.widgets[self.wId].enable(None)

    def deactivate(self, args):
        for widg in self.widgets:
            widg.disable(None)

    def enable(self, args):
        self.wId = rotateInt(self.wId + 1, 0, len(self.widgets)-1)
        self.widgets[self.wId].enable(None)
        self.widgets[self.wId-1].disable(None)

        return False

    def disable(self, args):
        self.wId = rotateInt(self.wId - 1, 0, len(self.widgets)-1)

        if self.wId + 1 < len(self.widgets):
            self.widgets[self.wId+1].disable(None)
        else:
            self.widgets[0].disable(None)

        self.widgets[self.wId].enable(None)

        return False


    def right(self, args):
        return self.widgets[self.wId].right(None)

        return False

    def left(self, args):
        return self.widgets[self.wId].left(None)

        return False


    def enter(self, args):
        self.widgets[self.wId].enter(args)

    def _saveSettings(self, args):
        def creaetEmptyFile(path):
            try:
                open(path, 'x+')
            except FileExistsError:
                pass

        #write imc config file
        includes.config['settings']['screensaverTime'] = self.sliderSaver.getCurrent() + self.stimeStart
        includes.config['settings']['osdTime'] = self.osdTime.getCurrent() + self.stimeStart
        includes.config['settings']['audioSource'] = self.hdmiAudioOut.getCurrent()
        includes.config['settings']['hdmiResolution'] = self.hdmiResolution.getCurrent()
        includes.config['settings']['hdmiBoost'] = self.hdmiBoost.getCurrent()
        includes.config['video']['autoplay'] = str(self.videoAutoplay.getValue()).lower()
        includes.config['music']['autoplay'] = str(self.musicAutoplay.getValue()).lower()
        includes.writeConfig()

        #Read /boot/imc_hdmi.txt
        creaetEmptyFile(includes.config['hdmiCfgPath'])
        try:
            data = []
            with open(includes.config['hdmiCfgPath'], "r") as hdmiCfg:
                data = hdmiCfg.readlines()

            with open(includes.config['hdmiCfgPath'], "w") as hdmiCfg:
                ret = []
                if len(data) > 0:
                    for line in data:
                        if line.startswith("config_hdmi_boost"):
                            ret.append("config_hdmi_boost={}".format(self.hdmiBoost.getCurrent()))
                        else:
                            ret.append(line)
                else:
                    ret.append("config_hdmi_boost={}".format(self.hdmiBoost.getCurrent()))

                hdmiCfg.writelines(ret)
        except:
                logging.error("{}".format(sys.exc_info()))



    def myexit(self, args):
        App.get_running_app().stop()

    def __init__(self, **kwargs):
        self.itemHeight = 75

        super(MenuSettings, self).__init__(**kwargs)

        self.cols = 1

        #
        # Audio / Video settings
        #
        def _updateMusicAutoplay():
            includes.config['music']['autoplay'] = str(self.musicAutoplay.getValue()).lower()

        self.musicAutoplay = SelectSpinnerBool(
                size_hint_x=None,
                width=250,
                size_hint_y=None,
                height=self.itemHeight,
                text="Autostart Music",
                trueHandler=_updateMusicAutoplay,
                falseHandler=_updateMusicAutoplay,
        )
        self.musicAutoplay.setValue(includes.config['music']['autoplay'] == 'true')
        self.widgets.append(self.musicAutoplay)

        #
        # video auto play
        #
        def _updateVideoAutoplay():
            includes.config['video']['autoplay'] = str(self.videoAutoplay.getValue()).lower()

        self.videoAutoplay = SelectSpinnerBool(
                size_hint_x=None,
                width=250,
                size_hint_y=None,
                height=self.itemHeight,
                text="Autostart Video",
                trueHandler=_updateVideoAutoplay,
                falseHandler=_updateVideoAutoplay,
        )
        self.videoAutoplay.setValue(includes.config['video']['autoplay'] == 'true')
        self.widgets.append(self.videoAutoplay)

        #
        # HDMI Audio / Analog audio selector
        #
        def _setAudioOutAnalog():
            os.system("amixer cset numid=3 2")

        def _setAudioOutHdmi():
            os.system("amixer cset numid=3 1")

        def _setAudioOutAuto():
            os.system("amixer cset numid=3 0")

        self.hdmiAudioOut = SelectSpinner(
            size_hint_x=None,
            width=250,
            size_hint_y=None,
            height=self.itemHeight,
            text="Audio Output"
        )

        self.hdmiAudioOut.add("Analog", _setAudioOutAnalog) #Default value
        self.hdmiAudioOut.add("HDMI", _setAudioOutHdmi)
        self.hdmiAudioOut.add("Auto", _setAudioOutAuto)
        self.hdmiAudioOut.switch(str(includes.config['settings']['audioSource']))
        self.widgets.append(self.hdmiAudioOut)

        #
        # HDMI Resolution
        #
        def _changeHdmiResHD():
            os.system("DISPLAY=:0 xrandr -s 1920x1080")


        def _changeHdmiResVGA():
            os.system("DISPLAY=:0 xrandr -s 1280x1024")



        self.hdmiResolution = SelectSpinner(
            size_hint_x=None,
            width=250,
            size_hint_y=None,
            height=self.itemHeight,
            text="HDMI Resolution"
        )
        self.hdmiResolution.add("1920x1080", _changeHdmiResHD) #0
        self.hdmiResolution.add("1280x1024", _changeHdmiResVGA) #1
        self.hdmiResolution.switch(str(includes.config['settings']['hdmiResolution']))
        self.hdmiResolution.executeHandler()
        self.widgets.append(self.hdmiResolution)

        #
        # HDMI Bost setting
        #
        self.hdmiBoost = SelectSpinner(
            size_hint_x=None,
            width=250,
            size_hint_y=None,
            height=self.itemHeight,
            text="HDMI Bost"
        )
        for i in range(12):
            self.hdmiBoost.add(str(i), None) #Default value

        self.hdmiBoost.switch(str(includes.config['settings']['hdmiBoost']))
        self.widgets.append(self.hdmiBoost)

        #
        # Sliders
        #
        self.stimeStart = 5
        self.stimeEnd = 16
        def _updateSaverTime():
            val = self.stimeStart + self.sliderSaver.getCurrent()
            includes.config['settings']['screensaverTime'] = val

        self.sliderSaver = SelectSpinner(
            size_hint_x=None,
            width=250,
            size_hint_y=None,
            height=self.itemHeight,
            text="Screensaver Time"
        )

        for i in range(self.stimeStart, self.stimeEnd):
            self.sliderSaver.add(str(i), _updateSaverTime)

        self.widgets.append(self.sliderSaver)
        #
        # OSD Time
        #
        def _updateOsdTime():
            val = self.stimeStart + self.sliderSaver.getCurrent()
            includes.config['settings']['screensaverTime'] = val

        self.osdTime = SelectSpinner(
            size_hint_x=None,
            width=250,
            size_hint_y=None,
            height=self.itemHeight,
            text="OSD Time"
        )

        for i in range(self.stimeStart, self.stimeEnd):
            self.osdTime.add(str(i), _updateOsdTime)

        self.widgets.append(self.osdTime)

        #
        # Store button
        #
        def _saveLeft(self):
            return True
        self.btnSave = SelectLabel(
            text="Save Settings",
            # background_color=includes.styles['defaultBg'],
            enaColor=includes.styles['defaultEnaColor'],
            size_hint_y=None,
            size_hint_x=None,
            height=200,
            width=200,
        )
        self.btnSave.enter = self._saveSettings
        self.btnSave.left = _saveLeft
        # self.btnSave = SelectButton(
        #     text="Save",
        #     size_hint=(None, None),
        #     enaColor=includes.styles['enaColor0'],
        #     id="-1",
        #     font_size=includes.styles['fontSize']
        # )
        #
        # self.btnSave.enter = self._saveSettings
        # self.btnSave.size_hint_y = None
        # self.btnSave.height = 50
        self.widgets.append(self.btnSave)

        #Headers
        self.headVideoAudio = SelectLabelBg(
            text="Video/Audio Settings",
            background_color=includes.colors['gray'],
            size_hint_y=None,
            height=35
        )

        self.headSystemSettings = SelectLabelBg(
            text="System Settings",
            background_color=includes.colors['gray'],
            size_hint_y=None,
            height=35
        )

        self.headSettingsCtrl = SelectLabelBg(
            text="Settings Controls",
            background_color=includes.colors['gray'],
            size_hint_y=None,
            height=35,
        )

        for item in self.widgets:
            # if item == self.musicAutoplay:
            #     self.add_widget(self.headVideoAudio)
            #
            # if item == self.sliderSaver:#first slider
            #     self.add_widget(self.headSystemSettings)
            #
            # if item == self.btnSave:
            #     self.add_widget(self.headSettingsCtrl)

            self.add_widget(item)


        self.wId = 0
