import threading
import logging

from kivy.uix.stacklayout import StackLayout
from kivy.uix.gridlayout import GridLayout
from kivy.graphics import Rectangle, Color
from kivy.uix.button import Button
from kivy.app import App

from selectables.selectable_items import Select
from selectables.buttons import SelectButton
import includes


class MenuStrip(StackLayout):
    widgets = []

    def addItem(self, imgPath, id, content, bgColor, enaColor):
        selBtn = SelectButton(
            source=imgPath,
            size_hint_y=None,
            height=60,
            size_hint_x=None,
            width=160,
            background_color=bgColor,
            enaColor=enaColor
        )

        #keep a list of all children for navigation purposes
        d = {
            "btn":selBtn,
            "id":id,
            "content":content
        }

        self.widgets.append(d)

        #add item to the menu so it will be visible
        self.add_widget(selBtn)


    def __init__(self, **kwargs):
        super(MenuStrip, self).__init__(**kwargs)
        self.orientation='lr-tb'
        self.size_hint_x = None
        self.width = 160
        #self.spacing = [0, 8]


class ImcTabview(Select, GridLayout):
    def enable(self, id):
        for widget in self.strip.widgets:
            if int(id) == int(widget['id']):
                widget['btn'].enable(None)
                self.clear_widgets()
                self.add_widget(self.strip)
                if widget['content'] is None:
                    logging.error("MenuContainer: widget content with id = {} is None".format(id))

                self.add_widget(widget['content'])
                self.curWidget = widget
                return

    def disable(self, id):
        for widget in self.strip.widgets:
            if int(id) == int(widget['id']):
                widget['btn'].disable(None)
                return

    def setContent(self, id, content):
        logging.error("Thomas: setContent called")
        for i in range(len(self.strip.widgets)):
            widget = self.strip.widgets[i]

            if int(id) == int(widget['id']):
                logging.error("Set content for id = {} / content = {}".format(id, content))
                self.strip.widgets[i]['content'] = content

                return

    def getMenuBtn(self, id):
        for widget in self.strip.widgets:
            if int(id) == int(widget['id']):
                return widget['btn']

    def update(self, args):
        logging.error("Thomas: update menu container")
        self.clear_widgets()
        self.add_widget(self.strip)
        self.add_widget(self.curWidget['content'])
        logging.error("Thomas: update content = {}".format(self.curWidget['content']))


    def __init__(self, **kwargs):
        idList = kwargs.pop('idList', [0,1,2,3,4])
        self.root = kwargs.pop('root', None)
        logging.error("Thomas: container kwargs = {}".format(kwargs))

        super(ImcTabview, self).__init__(**kwargs)

        self.rows = 1
        self.cols = 2
        self.spacing = [10,0]


        self.strip = MenuStrip()
        bgCol = includes.styles['menuBarColor']
        enaColor = includes.styles['enaColor0']
        imgNames = ['system', 'video', 'music', 'playlist', 'settings']


        for i in range(len(imgNames)):
            tmpPath = "atlas://resources/img/pi-player/" + imgNames[i]
            self.strip.addItem(tmpPath, idList[i], None, bgCol, enaColor)

        self.add_widget(self.strip)
        self.curWidget = self.strip.widgets[0]

        self.bind(size=self.changeSize)


    def changeSize(self, widget, size):
        width0 = self.strip.widgets[0]['btn'].width

        with self.canvas.before:
            Color(*includes.styles['menuBarColor'])
            Rectangle(size=(width0, 2000), pos=self.pos)



#############################
#############################
#############################
class Test(App):
    def testFunc(self):
        import time
        time.sleep(2)

        for i in range(5):
            self.menu.enable(i)
            self.menu.disable(i-1)
            time.sleep(1)





    def build(self):
        #strip = MenuStrip()
        self.menu = ImcTabview()



        workThread = threading.Thread(target=self.testFunc)
        workThread.setDaemon(True)
        workThread.start()

        return self.menu

if __name__ == '__main__':
    Test().run()
