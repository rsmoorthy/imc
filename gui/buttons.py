from gui.images import ImageBg
from kivy.uix.button import Button
from kivy.graphics import Rectangle, Color

class SelectButton(ImageBg):
    '''Not really a button but rather an alpha png with changable background color'''
    def enable(self, args):
        self.background_color = self.enaColor
        return True

    def disable(self, args):
        self.background_color = self.defaultColor
        return True

    def enter(self, args):
        if self.onEnter is not None:
            self.onEnter(args)

    def __init__(self, **kwargs):
        self.onEnter = None
        self.enaColor = kwargs.pop('enaColor', (1,1,1,1))
        super(SelectButton, self).__init__(**kwargs)

        self.defaultColor = self.background_color


class SelectButtonOld(Button):
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
