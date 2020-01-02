from kivy.uix.widget import Widget
from kivy.properties import ObjectProperty
from kivy.graphics import Rectangle, Color

class ImageBg(Widget):
    background_color = ObjectProperty()

    def _posChange(self, widget, value):
        posX = value[0] + self.marginL
        posY = value[1] + self.marginD
        self.img.pos = (posX, posY)
        self.rect.pos = (posX, posY)

    def _sizeChange(self, widget, value):
        self.width = self.marginL + value[0] + self.marginR
        self.height = self.marginL + value[1] + self.marginU

        posX = self.pos[0] + self.marginL
        posY = self.pos[1] + self.marginD

        self.img.pos = (posX, posY)
        self.rect.pos = (posX, posY)

    def _bgChange(self, widget, value):
        posX = self.pos[0] + self.marginL
        posY = self.pos[1] + self.marginD

        self.canvas.clear()

        with self.canvas:
            Color(*value)
            self.rect = Rectangle(size=self.size, pos=(posX, posY))

            Color()
            self.img = Rectangle(source=self.imgSrc, size=self.size, pos=(posX, posY))



    def __init__(self, **kwargs):
        self.imgSrc = kwargs.pop('source', None)
        self.background_color = kwargs.pop('background_color', (1,1,1,1))
        self.marginD, self.marginU, self.marginL, self.marginR = kwargs.pop('margin', (0,0,0,0))

        self.width = self.marginL + self.width + self.marginR
        self.height = self.marginL + self.height + self.marginU

        posX = self.pos[0] + self.marginL
        posY = self.pos[1] + self.marginD

        super(ImageBg, self).__init__(**kwargs)

        with self.canvas:
            Color(*self.background_color)
            self.rect = Rectangle(size=self.size, pos=(posX, posY))

            Color()
            self.img = Rectangle(source=self.imgSrc, size=self.size, pos=(posX, posY))

        self.bind(size=self._sizeChange)
        self.bind(pos=self._posChange)
        self.bind(background_color=self._bgChange)
