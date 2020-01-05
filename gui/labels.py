from kivy.uix.label import Label
from kivy.properties import ObjectProperty
from kivy.graphics import Rectangle, Color

import includes


class SelectLabel(Label):
    enaColor = ObjectProperty()

    def enable(self, args):
        self.selected = True
        self.color = self.enaColor
        return True

    def disable(self, args):
        self.selected = False
        self.color = self.defaultColor
        return True

    def __init__(self, **kwargs):

        self.enaColor = kwargs.pop('enaColor', (1,0,0,1))

        super(SelectLabel, self).__init__(**kwargs)

        self.defaultColor = self.color
        self.selected = False
        self.type = "label"

        self.font_size = includes.styles['fontSize']

        return

class SelectLabelBg(SelectLabel):
    background_color = ObjectProperty(includes.styles['defaultBg'])
    isEnabled = False


    def size_change(self, widget, value):
        self.back.size = value
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
