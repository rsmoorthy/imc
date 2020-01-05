from kivy.uix.screenmanager import Screen, ScreenManager
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from gui.images import ImageBg
from gui.labels import SelectLabel
from helper import rotateInt

import includes

class _SpinElement(Screen):
    def __init__(self, text, handler, **kwargs):
        self.handler = handler
        self.text = text
        fontSize = kwargs.pop("fontSize", 15)
        super(_SpinElement, self).__init__(**kwargs)


        self.label = Label(
            text=self.text,
            font_size=fontSize
        )
        self.add_widget(self.label)


class SelectSpinner(GridLayout):
    def _sizeChange(self, widget, value):
        pass

    def add(self, text, handler):
        element = _SpinElement(
            text, handler,
            fontSize=self.fontSize,
            name=str(len(self.widgets))
        )
        self.widgets.append(element)
        self.manager.add_widget(element)
        self.manager.current = "0"

    def left(self, args):
        if self.isActive:
            self.wId = rotateInt(self.wId - 1, 0, len(self.widgets) - 1)
            self.manager.switch_to(self.widgets[self.wId], direction="left")
            return False

        return True

    def right(self, args):
        if self.isActive:
            self.wId = rotateInt(self.wId + 1, 0, len(self.widgets) - 1)
            self.manager.switch_to(self.widgets[self.wId], direction="right")
            return False

        return True

    def enter(self, args):
        if not self.isActive:
            self.isActive = True
            self.manager.opacity = 1.0
            self.lArrow.opacity = 1.0
            self.rArrow.opacity = 1.0
        else:
            self.isActive = False
            self.manager.opacity = self.opac
            self.lArrow.opacity = self.opac
            self.rArrow.opacity = self.opac
            if self.widgets[self.wId].handler is not None:
                self.widgets[self.wId].handler()

    def enable(self, args):
        self.label.enable(None)


    def disable(self, args):
        self.label.disable(None)
        self.isActive = False
        self.manager.opacity = self.opac
        self.lArrow.opacity = self.opac
        self.rArrow.opacity = self.opac

    def getCurrent(self):
        return int(self.manager.current)

    def switch(self, name):
        for item in self.widgets:
            if item.name == name:
                self.manager.current = name
                self.wId = int(name)

    def executeHandler(self):
        self.widgets[self.wId].handler()

    def __init__(self, **kwargs):
        self.fontSize = kwargs.pop("fontSize", includes.styles['fontSize'])
        self.text = kwargs.pop("text", "no text defined")
        self.opac = kwargs.pop("opac", 0.4)

        super(SelectSpinner, self).__init__(**kwargs)

        self.rows=1
        self.manager = ScreenManager(**kwargs, opacity=self.opac)
        self.widgets = []
        self.wId = 0
        self.isActive = False

        offY = self.height / 2

        self.lArrow = ImageBg(
            size_hint=(None, None),
            width=30/2,
            height=35/2,
            source="atlas://resources/img/pi-player/arrow_left",
            margin=[offY-35/4,0,0,0],
            opacity=self.opac,
            background_color=(0,0,0,0)
        )

        self.rArrow = ImageBg(
            size_hint=(None, None),
            width=30/2,
            height=35/2,
            source="atlas://resources/img/pi-player/arrow_right",
            margin=[offY-35/4,0,0,0],
            opacity=self.opac,
            background_color=(0,0,0,0)
        )

        self.label = SelectLabel(
            text=self.text,
            halign='left',
            valign='middle',
            size_hint=(None, None),
            width=400,#TODO: This should be defined based on the text length and fontSize
            height=self.height,
            font_size=self.fontSize,
            enaColor=includes.colors['oldblue']
        )
        self.label.text_size = (self.label.width - 60, self.label.height)

        self.add_widget(self.label)
        self.add_widget(self.lArrow)
        self.add_widget(self.manager)
        self.add_widget(self.rArrow)

        self.bind(size=self._sizeChange)


class SelectSpinnerBool(SelectSpinner):

    def getValue(self):
        if self.manager.current == "0":
            return False
        else:
            return True

    def setValue(self, value):
        if value:
            self.switch("1")
        else:
            self.switch("0")

    def __init__(self, **kwargs):
        trueName = kwargs.pop('trueName', "True")
        falseName = kwargs.pop('falseName', "False")
        trueHandler = kwargs.pop('trueHandler', None)
        falseHandler = kwargs.pop('falseHandler', None)
        super(SelectSpinnerBool, self).__init__(**kwargs)

        self.add(falseName, falseHandler)
        self.add(trueName, trueHandler)
