import os
import json
import logging
import includes

from kivy.core.window import Window
from kivy.uix.widget import Widget
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.checkbox import CheckBox
from kivy.uix.tabbedpanel import TabbedPanelHeader
from kivy.uix.slider import Slider
from kivy.uix.togglebutton import ToggleButton
from kivy.uix.scrollview import ScrollView
from kivy.uix.gridlayout import GridLayout
from kivy.uix.stacklayout import StackLayout
from kivy.graphics import Rectangle, Color, Line, Ellipse
from kivy.properties import ObjectProperty
from kivy.uix.screenmanager import Screen, ScreenManager
from selectables.images import ImageBg

import includes
from helper import rotateInt

#
# Is this class really going to help us?
#
class Select():
    selected = None
    type = None
    enaColor = ObjectProperty()
    defaultColor = None
    onEnter = None
    user = {}
    hasLeftRight = False

class SelectableTabbedPanelHeader(Select, TabbedPanelHeader):
    def enable(self, args):
        self.selected = True
        self.state = "down"
        return True

    def disable(self, args):
        self.selected = False
        self.state = "normal"
        return True


    def __init__(self, **kwargs):
        self.enaColor = kwargs.pop('enaColor', None)

        super(SelectableTabbedPanelHeader, self).__init__(**kwargs)

        if not self.enaColor:
            self.enaColor = self.background_color

        self.font_size = includes.styles['fontSize']

        self.defaultColor = self.background_color
        self.selected = False
        self.type = "selectabletabbedpanelheader"


class SelectLabel(Label, Select):
    def enable(self, args):
        self.selected = True
        self.color = self.enaColor
        return True

    def disable(self, args):
        self.selected = False
        self.color = self.defaultColor
        return True

    def __init__(self, **kwargs):

        self.enaColor = kwargs.pop('enaColor', None)

        if not self.enaColor:
            self.enaColor = self.defaultColor

        super(SelectLabel, self).__init__(**kwargs)

        self.defaultColor = self.color
        self.selected = False
        self.type = "label"

        self.font_size = includes.styles['fontSize']

        return





class SelectButtonOld(Button, Select):
    btnType = None

    def on_press(self):
        pass

    def enable(self, args):
        self.selected = True

        if self.btnType == "text":
            self.color = self.enaColor

        elif self.btnType == "image":
            self.background_normal = self.imgPath + "_select"

        return True

    def disable(self, args):
        self.selected = False

        if self.btnType == "text":
            self.color = self.defaultColor

        elif self.btnType == "image":
            self.background_normal = self.imgPath

        return True

    def __init__(self, **kwargs):
        self.enaColor = kwargs.pop('enaColor', None)
        self.defaultColor = self.color

        if not self.enaColor:
            self.enaColor = includes.styles['defaultEnaColor']

        self.imgPath = kwargs.pop('imgPath', None)

        if self.imgPath:
            self.btnType = "image"
            self.background_normal = self.imgPath
        else:
            self.btnType = "text"

        super(SelectButton, self).__init__(**kwargs)


class SelectSlider(Select, GridLayout):
    label = None
    slider = None
    valLabel = None

    def enable(self, args):
        self.selected = True
        self.label.color = self.enaColor

        return True

    def disable(self, args):
        self.selected = False
        self.label.color = self.defaultColor
        self.slider.opacity = self.sliderOpac
        self.unlocked = False
        return True

    def enter(self, args):
        if not self.unlocked:
            self.unlocked = True
            self.slider.opacity = 1
        else:
            self.unlocked = False
            self.slider.opacity = self.sliderOpac

    def left(self, args):
        if self.unlocked:
            self.decrement(None)
            return False

        return True

    def right(self, args):
        if self.unlocked:
            self.increment(None)

        return False



    def increment(self, args):
        val = self.slider.value

        if val == self.slider.max:
            return

        val = val + 1

        self.slider.value = val
        self.valLabel.text = str(val)+"s"

    def decrement(self, args):
        val = self.slider.value

        if val == self.slider.min:
            return

        val = val - 1

        self.slider.value = val
        self.valLabel.text = str(val)+"s"

    def __init__(self, **kwargs):

        #remove all kwargs argment which shall not be passed to child
        self.id = kwargs.pop('id', None)
        if not self.id:
            print("SelectSlider::init::id is not defined")
            return

        self.enaColor = kwargs.pop('enaColor', None)
        if not self.enaColor:
            print("SelectSlider::init::enaColor is not defined")
            return

        self.value = kwargs.pop('value', None)
        text = kwargs.pop('text', "!!!Empty Name in slider!!!")
        textSize = kwargs.pop('fontSize', "20sp")

        #call super only after additional arguments have been popped
        super(SelectSlider, self).__init__(**kwargs)

        self.label = Label(
            text=text,
            halign='left',
            size_hint=(None, None),
            width=400,
            height=50,
            font_size=textSize
        )
        self.label.text_size = (self.label.width - 60, self.label.height)

        self.slider = Slider(
            min=-0,
            max=20,
            value=self.value,
            size_hint=(None, None),
            width=200,
            height=50
        )
        self.sliderOpac = 0.4
        self.slider.opacity = self.sliderOpac

        val = self.slider.value
        self.valLabel = Label(
            text=str(val)+'s',
            size_hint=(None, None),
            width=60,
            height=50,
            font_size=textSize
        )

        self.selected = False
        self.type = "selectslider"
        self.defaultColor = self.label.color

        self.rows = 1
        self.cols = 3

        self.add_widget(self.label)
        self.add_widget(self.slider)
        self.add_widget(self.valLabel)

        self.hasLeftRight = True
        self.unlocked = False


class SelectLabelBg(SelectLabel):
    background_color = ObjectProperty(includes.styles['defaultBg'])
    isEnabled = False


    def size_change(self, widget, value):
        self.back.size = value
        logging.error("SelectlabelBg size change")
        self.text_size = (value[0], self.text_size[1])

        self.width = self.marginL + value[0] + self.marginR
        self.height = self.marginL + value[1] + self.marginU

        posX = self.pos[0] + self.marginL
        posY = self.pos[1] + self.marginD

        self.back.pos = (posX, posY)

    def pos_change(self, widget, value):
        #self.back.pos = value

        posX = value[0] + self.marginL
        posY = value[1] + self.marginD
        self.back.pos = (posX, posY)

    def enable(self, args):
        if not self.isEnabled:
            self.tmpColor = self.background_color
            self.background_color = self.enaColor# includes.colors['darkblue']
            self.isEnabled = True

    def disable(self, args):
        if self.isEnabled:
            self.background_color = self.tmpColor
            self.isEnabled = False


    def updateBg(self, widget, value):
        with self.canvas.before:
            Color(*value)
            self.back = Rectangle(size=self.size, pos=self.pos)

    def __init__(self, **kwargs):
        self.background_color = kwargs.pop('background_color', includes.styles['defaultBg'])
        self.marginD, self.marginU, self.marginL, self.marginR = kwargs.pop('margin', (0,0,0,0))

        super(SelectLabelBg, self).__init__(**kwargs)

        self.width = self.marginL + self.width + self.marginR
        self.height = self.marginL + self.height + self.marginU

        posX = self.pos[0] + self.marginL
        posY = self.pos[1] + self.marginD

        with self.canvas.before:
            Color(*self.background_color)
            self.back = Rectangle(size=self.size, pos=(posX, posY))

        self.bind(size=self.size_change)
        self.bind(pos=self.pos_change)
        self.bind(background_color=self.updateBg)
        self.bind(enaColor=self.updateBg)



class SelectListViewItem(StackLayout, Select):
    background_color = ObjectProperty(includes.styles['defaultBg'])
    fillerColor = ObjectProperty(includes.styles['defaultFiller'])

    image = None
    label = None
    filler = None
    isDir = False
    user = {}

    def resize(self, widget, value):
        self.label.width = self.parent.width-self.imgWidth-self.filler.width
        self.label.text_size = (self.label.width-20, self.imgHeight)
        pass

    def enable(self, args):
        self.label.enable(args)

    def disable(self, args):
        self.label.disable(args)

    def __init__(self, **kwargs):
        self.source = kwargs.pop('source', None)
        self.enaColor = kwargs.pop('enaColor', includes.styles['defaultEnaColor'])
        self.padding_top = kwargs.pop('padding_top', 0)
        self.background_color = kwargs.pop('background_color', includes.styles['defaultBg'])
        self.text = kwargs.pop('text', "undefined text")
        self.id = kwargs.pop('id', "undefined id")
        self.imgWidth = kwargs.pop('imgWidth', 100)
        self.imgHeight = kwargs.pop('imgHeight', 100)
        self.widthParent = kwargs.pop('widthParent', None)
        self.isDir = kwargs.pop('isDir', False)
        self.user = kwargs.pop('user', None)
        self.showIcon = kwargs.pop('showIcon', True)

        #set the layout hight to fit the image height
        self.height = self.imgHeight + 2*self.padding_top
        self.size_hint_y = None

        super(SelectListViewItem, self).__init__(**kwargs)

        self.filler = SelectLabelBg(
            size_hint_x=None,
            width=10,
            size_hint_y=None,
            height=self.imgHeight,
            id="-1",
            text_size=(0, 0),
            background_color=self.fillerColor
        )
        self.add_widget(self.filler)

        if self.source and self.showIcon:
            self.image = ImageBg(
                background_color=self.background_color,
                width=self.imgWidth,
                size_hint=(None, None),
                height=self.imgHeight,
                source=self.source
            )
            self.add_widget(self.image)

        elif not self.source and self.showIcon:
            self.image = SelectLabelBg(
                width=self.imgWidth,
                size_hint=(None, None),
                height=self.imgHeight,
                background_color=self.background_color,
            )
            self.add_widget(self.image)

        labelWidth = self.widthParent-self.imgWidth-self.filler.width
        self.label = SelectLabelBg(
            background_color=self.background_color,
            text_size=(labelWidth-20, self.imgHeight),
            enaColor=self.enaColor,
            text=self.text,
            halign="left",
            valign="middle",
            size_hint_y=None,
            height=self.imgHeight,
            size_hint_x=None,
            width=labelWidth,
            id=self.id
        )

        self.add_widget(self.label)
        self.bind(width=self.resize)


class SelectListView(Select, ScrollView):
    tmp = []
    layout = None
    widgets = []
    startId = None
    wId = -1 # id of the currently selected entry
    dir = "down"
    enaColor = ObjectProperty(includes.styles['defaultEnaColor'])
    headerText = None
    header = None
    topTextVisible = None

    def enter(self, args):
        logging.info("SelectListView: enter callback triggered")

    def left(self, args):
        self.widgets[self.wId].disable(None)
        self.wId = 0

    def activate(self, args):
        self.wId = 0
        self.widgets[0].enable(None)

    def enable(self, args):
        if isinstance(args, dict):
            increment = args.pop('inc', True)
        else:
            increment = True

        logging.error("Thomas:wid = {}".format(self.wId))
        if self.wId < len(self.widgets) - 1:
            if increment:
                self.wId = self.wId + 1

            self.widgets[self.wId].enable(None)
            self.scroll_to(self.widgets[self.wId])

            if self.wId > 0:
                self.widgets[self.wId-1].disable(args)

        elif self.wId == len(self.widgets)-1:
            self.widgets[self.wId].disable(args)
            self.wId = 0
            self.widgets[self.wId].enable(None)
            self.scroll_to(self.widgets[self.wId])



        return False # never returns true as there nothing we need to do when we come to end of list


    def disable(self, args):
        if isinstance(args, dict):
            increment = args.pop('inc', True)
            disTop = args.pop('disTop', True)
        else:
            increment = True
            disTop = True

        if self.wId >= 1:
            self.widgets[self.wId].disable(None)

            if increment:
                self.wId = self.wId - 1

            self.widgets[self.wId].enable(None)
            self.scroll_to(self.widgets[self.wId])

        else:
            # if disTop:
            #     self.widgets[self.wId].disable(None)
            #
            #     if self.selectFirst:
            #         self.wId = 0
            #     else:
            #         self.wId = -1
            self.widgets[self.wId].disable(args)
            self.wId = len(self.widgets)-1
            self.widgets[self.wId].enable(None)
            self.scroll_to(self.widgets[self.wId])


            return True
        return False

    def add(self, text, isDir):
        tmpId = str(len(self.widgets) + self.startId)

        if self.showIcon:
            imgWidth, imgHeight = includes.styles['selectItemHeight'], includes.styles['selectItemHeight'] #image height defines the hight of the element
        else:
            imgWidth, imgHeight = 0, includes.styles['selectItemHeight'] #image height defines the hight of the element


        if not self.showDirs and isDir:
            return

        source = None
        if isDir:
            source = "atlas://resources/img/pi-player/dir"
            #imgWidth, imgHeight = includes.styles['selectItemHeight'], includes.styles['selectItemHeight']
        else:
            source =  "atlas://resources/img/pi-player/dot"

        bg = None
        if len(self.widgets) % 2 == 0:
            bg = self.itemColor0
        else:
            bg = self.itemColor1

        if not self.fillerColor:
            self.fillerColor = bg

        self.widgets.append(SelectListViewItem(
            enaColor=self.enaColor,
            source=source,
            background_color=bg,
            text=text,
            id=tmpId,
            imgWidth=imgWidth,
            imgHeight=imgHeight,
            widthParent=self.width,
            fillerColor=self.fillerColor,
            isDir=isDir,
            showIcon=self.showIcon,
        ))

        self.layout.add_widget(self.widgets[-1])


    def update(self, widget, val):
        for item in self.layout.children:
            item.width = self.width


    def __init__(self, **kwargs):
        self.enaColor = kwargs.pop('enaColor', None)
        if not self.enaColor:
            logging.error("start id not set")
            return

        self.startId = int(kwargs['id']) + 1
        if not self.startId:
            logging.error("start id not set")
            return

        self.widthParent = kwargs.pop('widthParent', None)
        self.fillerColor = kwargs.pop('fillerColor', None)
        self.headerText = kwargs.pop('headerText', None)
        self.showDirs = kwargs.pop('showDirs', True)
        self.selectFirst = kwargs.pop('selectFirst', True)

        self.itemColor0 = kwargs.pop('itemColor0', includes.styles['itemColor0'])
        self.itemColor1 = kwargs.pop('itemColor1', includes.styles['itemColor1'])
        self.showIcon = kwargs.pop('showIcon', True)

        super(SelectListView, self).__init__(**kwargs)

        self.isSelectable = True

        if self.selectFirst:
            self.wId = 0
        else:
            self.wId = -1

        self.layout = GridLayout(cols=1, spacing=0, size_hint_y=None)
        self.layout.bind(minimum_height=self.layout.setter('height'))

        #TODO: this causes not all files to be displayed is this needed for anything?
        #self.size_hint_y = None
        #self.height = Window.height-100

        self.add_widget(self.layout)
        self.bind(enaColor=self.changeColor)
        self.bind(width=self._changeSize)
        self.bind(pos=self._changePos)

    def _changeSize(self, wid, size):
        self.height = Window.height-100

    def _changePos(self, wid, pos):
        self.pos = pos

    def changeColor(self, wid, value):
        self.widgets[self.wId].label.color = value


class PlaylistJsonList(SelectListView):
    def updateList(self, args):
        if args is None:
            return

        if "currentWidget" in args:
            tmp = args['currentWidget']
            text = tmp.widgets[tmp.wId].text

            path = os.path.join(includes.config['playlist']['rootdir'], text)
            with open(path) as playFile:
                data = json.load(playFile)

            self.layout.clear_widgets()
            self.wId = 0
            self.widgets = []

            for item in data:
                self.add(data[item]['name'], False)


class SelectCheckBox(Select, StackLayout):
    def enable(self, args):
        self.label.enable(args)

    def disable(self, args):
        self.label.disable(args)

    def left(self, args):
        return True

    def right(self, args):
        return True

    def enter(self, args):
        self.checkbox.active = not self.checkbox.active

    def __init__(self, **kwargs):
        text = kwargs.pop('text', "undefined")
        enaColor = kwargs.pop('enaColor')
        #height = kwargs.pop('height')
        super(SelectCheckBox, self).__init__(**kwargs)

        self.label = SelectLabel(
            text=text,
            halign='left',
            valign='middle',
            size_hint=(None, None),
            width=400,#TODO: This should be defined based on the text length and fontSize
            height=self.height,
            # height=height,
            font_size=includes.styles['fontSize'],
            enaColor=enaColor,
        )

        self.checkbox = CheckBox(height=self.height)
        self.checkbox.size_hint = (None, None)
        self.checkbox.width = 50
        self.label.text_size = (self.label.width - 60, self.label.height)

        self.add_widget(self.label)
        self.add_widget(self.checkbox)


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


class SelectSpinner(GridLayout, Select):
    def _sizeChange(self, widget, value):
        logging.error("ImageBg: size change = {}".format(value))

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
        )

        self.rArrow = ImageBg(
            size_hint=(None, None),
            width=30/2,
            height=35/2,
            source="atlas://resources/img/pi-player/arrow_right",
            margin=[offY-35/4,0,0,0],
            opacity=self.opac,
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

#
#TODO: not needed might be removed
#
class SelectToggleButton(ToggleButton):
        btnType = None

        def on_press(self):
            pass

        def enable(self, args):
            self.selected = True

            if self.btnType == "text":
                self.color = self.enaColor

            elif self.btnType == "image":
                self.background_normal = self.imgPath + "_select"

            return True

        def disable(self, args):
            self.selected = False

            if self.btnType == "text":
                self.color = self.defaultColor

            elif self.btnType == "image":
                self.background_normal = self.imgPath

            return True

        def __init__(self, **kwargs):
            self.enaColor = kwargs.pop('enaColor', None)
            self.defaultColor = self.color

            if not self.enaColor:
                self.enaColor = includes.styles['defaultEnaColor']

            self.imgPath = kwargs.pop('imgPath', None)

            if self.imgPath:
                self.btnType = "image"
                self.background_normal = self.imgPath
            else:
                self.btnType = "text"

            super(SelectToggleButton, self).__init__(**kwargs)



def testImageBg():
    from kivy.app import App
    import threading
    import time
    from kivy.utils import get_color_from_hex as hexColor
    class Test(App):
        def _worker(self):
            for i in range(10):
                logging.error("worker thread")
                time.sleep(1)
                self.image.background_color = hexColor('#0f85a5')
                time.sleep(1)
                self.image.background_color = hexColor('#2c2c2c')

        def build(self):
            global test

            self.thread = threading.Thread(target=self._worker)
            self.thread.setDaemon(True)
            self.thread.start()




            self.image = ImageBg(
                source="/tmp/a.png",
                background_color=hexColor('#0f85a5'),
                size_hint_y=None,
                height=60,
                size_hint_x=None,
                width=160
            )

            return self.image

    Test().run()


if __name__ == "__main__":
    from kivy.app import App
    import threading
    import time

    test = "SelectToggleButton"
    class Test(App):
        def _worker(self):
            global test
            time.sleep(3)

            if test == "SelectSpinner":
                self.spin.enter(None)

                for i in range(6):
                    self.spin.left(None)
                    time.sleep(1)

                for i in range(6):
                    self.spin.right(None)
                    time.sleep(1)

                self.spin.enter(None)

            if test =="SelectToggleButton":

                for i in range(20):
                    logging.error("Start: SelectToggleButton")
                    time.sleep(1)
                    self.toggleBtn.value = "down"
                    time.sleep(1)
                    self.toggleBtn.value = "up"


        def spinnerPrint(self):
            print("Spinnder handler called")

        def build(self):
            global test

            self.thread = threading.Thread(target=self._worker)
            self.thread.setDaemon(True)
            self.thread.start()

            if test == "SelectSpinner":
                self.spin = SelectSpinner(
                    size_hint_x=None,
                    width=250,
                    size_hint_y=None,
                    height=150,
                    text="HDMI Resolution"
                )
                self.spin.add("thomas", self.spinnerPrint)
                self.spin.add("is", self.spinnerPrint)
                self.spin.add("doof", self.spinnerPrint)

                return self.spin

            if test == "SelectToggleButton":
                self.toggleBtn = SelectToggleButton(text="mandfred")
                return self.toggleBtn


    main = Test()
    main.run()
