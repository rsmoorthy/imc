from kivy.uix.anchorlayout import AnchorLayout
from kivy.uix.stacklayout import StackLayout
from kivy.app import App
from kivy.core.window import Window
import logging
import os

from gui.labels import SelectLabel
from gui.buttons import SelectButton
from gui.images import ImageBg
import includes
from helper import rotateInt

class MenuShutdown(AnchorLayout):
    def enable(self, args):
        self.widgets[self.wId].disable(None)
        self.wId = rotateInt(self.wId + 1, 0, 2)
        self.widgets[self.wId].enable(None)

    def disable(self, args):
        self.widgets[self.wId].disable(None)
        self.wId = rotateInt(self.wId - 1, 0, 2)
        self.widgets[self.wId].enable(None)

    def enter(self, args):
        self.widgets[self.wId].onEnter()

    def _shutdown(self):
        os.system("sudo poweroff")


    def _reboot(self):
        os.system("sudo reboot")


    def _cancel(self):
        self.screenManger.current = "main_menu"
        self.screenManger.mainMenu.curId = self.lastId
        includes.screenSaver.enable()
        self.widgets[self.wId].disable(None)
        self.wId = 0
        self.widgets[self.wId].enable(None)

    def __init__(self, **kwargs):
        self.screenManger = kwargs.pop('screenManager', None)

        if self.screenManger is None:
            logging.error("MenuShutdown: screen manager is not defined")
            return

        super(MenuShutdown, self).__init__(**kwargs)

        self.stack = StackLayout()

        self.anchor_x = "center"
        self.anchor_y = "center"

        self.btnShutdown = SelectLabel(
            text="Power Off",
            enaColor=includes.styles['defaultEnaColor'],
            size_hint_y=None,
            size_hint_x=None,
            height=50,
            width=200,
        )

        self.btnShutdown.enable(None)

        self.btnReboot = SelectLabel(
            text="Reboot",
            enaColor=includes.styles['defaultEnaColor'],
            size_hint_y=None,
            size_hint_x=None,
            height=50,
            width=200,
        )

        self.btnCancel = SelectLabel(
            text="Cancel",
            enaColor=includes.styles['defaultEnaColor'],
            size_hint_y=None,
            size_hint_x=None,
            height=50,
            width=200,
        )

        self.stack.add_widget(self.btnShutdown)
        self.stack.add_widget(self.btnReboot)
        self.stack.add_widget(self.btnCancel)

        self.stack.size_hint = (None, None)
        self.stack.height = self.btnReboot.height + self.btnShutdown.height
        self.stack.width = self.btnReboot.width
        self.add_widget(self.stack)

        self.wId = 0
        self.widgets = []
        self.widgets.append(self.btnShutdown)
        self.widgets.append(self.btnReboot)
        self.widgets.append(self.btnCancel)

        self.btnShutdown.onEnter = self._shutdown
        self.btnReboot.onEnter = self._reboot
        self.btnCancel.onEnter = self._cancel


#
# Standalone test
#
if __name__ == "__main__":
    from key_handler import KeyHandler
    from kivy.uix.screenmanager import ScreenManager, Screen
    from kivy.uix.label import Label

    class Main(App):
        def selectIdChange(self, args):
            logging.error("Id change back to last one so we can continue...")

        def onPress(self, args):
            name = args[1]

            if name == "up":
                self.menu.disable(None)

            if name == "down":
                self.menu.enable(None)

            if name == "enter":
                self.menu.enter(None)

        def build(self):
            self.handler = KeyHandler()
            self.handler.onPress = self.onPress

            smng = ScreenManager()
            s = Screen(name="main_menu")
            s.add_widget(Label(text="Main menu"))
            smng.add_widget(s)

            self.menu = MenuShutdown(screenManager=smng)#, curSelectId=5)
            self.menu._setLastSelectId = self.selectIdChange
            return self.menu


    main = Main()
    main.run()
