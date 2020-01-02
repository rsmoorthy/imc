import logging

from selectables.selectable_items import Select, SelectLabelBg
from selectables.images import ImageBg
from kivy.uix.scrollview import ScrollView
from kivy.properties import ObjectProperty
from kivy.uix.gridlayout import GridLayout
from kivy.uix.stacklayout import StackLayout

import includes

class SelectListViewItem(StackLayout, Select):
    background_color = ObjectProperty(includes.styles['defaultBg'])
    fillerColor = ObjectProperty(includes.styles['defaultFiller'])

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
    enaColor = ObjectProperty(includes.styles['defaultEnaColor'])

    def clearWidgets(self):
        self.layout.clear_widgets()

    def keyDownHook(self, **kwargs):
        pass

    def keyUpHook(self, **kwargs):
        pass

    def activate(self, args):
        self.wId = 0
        self.widgets[0].enable(None)

    def deactivate(self, args):
        for item in self.widgets:
            item.disable(None)

    def keyDown(self, args):
        if isinstance(args, dict):
            increment = args.pop('inc', True)
        else:
            increment = True

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

        self.keyDownHook(wId=self.wId, widget=self.widgets[self.wId])

        return False


    def keyUp(self, args):
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
            self.widgets[self.wId].disable(args)
            self.wId = len(self.widgets)-1
            self.widgets[self.wId].enable(None)
            self.scroll_to(self.widgets[self.wId])
            return True

        self.keyUpHook(wId=self.wId, widget=self.widgets[self.wId])
        return False

    def add(self, text, isDir):

        '''Add a new entry to the list view'''
        if self.showIcon:
            imgWidth = includes.styles['selectItemHeight']
            imgHeight = includes.styles['selectItemHeight']
        else:
            imgWidth, imgHeight = 0, includes.styles['selectItemHeight']

        if not self.showDirs and isDir:
            return

        source = None
        if isDir:
            source = "atlas://resources/img/pi-player/dir"
        else:
            source =  "atlas://resources/img/pi-player/dot"

        #Alternate background color for each row
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
            imgWidth=imgWidth,
            imgHeight=imgHeight,
            widthParent=self.width,
            fillerColor=self.fillerColor,
            showIcon=self.showIcon,
        ))

        self.layout.add_widget(self.widgets[-1])

    def _changePos(self, wid, pos):
        self.pos = pos

    def changeColor(self, wid, value):
        self.widgets[self.wId].label.color = value

    def __init__(self, **kwargs):
        self.widgets = []

        self.enaColor = kwargs.pop('enaColor', (1,0,0,1))
        self.widthParent = kwargs.pop('widthParent', None)
        self.fillerColor = kwargs.pop('fillerColor', None)
        self.showDirs = kwargs.pop('showDirs', True)
        self.itemColor0 = kwargs.pop('itemColor0', includes.styles['itemColor0'])
        self.itemColor1 = kwargs.pop('itemColor1', includes.styles['itemColor1'])
        self.showIcon = kwargs.pop('showIcon', True)

        #self.startId = int(kwargs['id']) + 1 #TODO: is this needed?
        # if not self.startId:
        #     logging.error("start id not set")
        #     return

        super(SelectListView, self).__init__(**kwargs)

        self.wId = 0

        self.layout = GridLayout(cols=1, spacing=0, size_hint_y=None)
        self.layout.bind(minimum_height=self.layout.setter('height'))

        self.add_widget(self.layout)
        self.bind(enaColor=self.changeColor)
        self.bind(pos=self._changePos)
