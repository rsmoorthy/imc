from selectables.images import ImageBg
from kivy.graphics import Rectangle, Color

class SelectButton(ImageBg):
    '''Not really a button but rather an alpha png with changable background color'''
    def enable(self, args):
        self.background_color = self.enaColor

    def disable(self, args):
        self.background_color = self.defaultColor

    def __init__(self, **kwargs):
        self.enaColor = kwargs.pop('enaColor', (1,1,1,1))
        super(SelectButton, self).__init__(**kwargs)

        self.defaultColor = self.background_color