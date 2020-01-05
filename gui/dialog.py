import logging
from subprocess import threading

from kivy.uix.stacklayout import StackLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.core.window import Window
from kivy.graphics import Rectangle, Color

from gui.labels import SelectLabelBg
from gui.buttons import SelectButton
import includes
from helper import clipInt

#
#Dialogs used in the application
#
def msgAutoRestart(handler, autoReplay, text, headerText, height, dId):

    def closeCallback(args):
        handler._removeDialog(dId)
        includes.db['runtime'] = 0
        includes.writeDb()

    btn = [
        {
            'imgPath':'dialogClose',
            'callback':closeCallback
        },
        {
            'imgPath':'dialogPlay',
            'callback':autoReplay
        }
    ]

    return  ( Dialog(
        borderHeight=includes.styles['dialogBorderHeight'],
        headerHeight=40,
        contentHeight=height,
        headerColor=includes.styles['dialogMsgHead'],
        contentColor=includes.styles['dialogMsgContent'],
        textColor=includes.styles['dialogMsgText'],
        text=text,
        headerText=headerText,
        buttonDesc=btn,
        dId=dId
    ) , closeCallback)




class DialogButtons(GridLayout):
    '''Each dialog can have upto 4 buttons as to control thes system
        like deleting a message, restarting a interrupted video or audio source.
    '''
    btnList = None
    callbackList = None
    bgColor = None
    back = None
    hId = -1
    user = None

    def enter(self, args):
        #args = {}
        #args['id'] = self.id
        self.callbackList[self.hId](args)

    def enable(self, args):
        if self.hId < 0:
            self.hId = 0

        self.btnList[self.hId].enable(None)

    def disable(self, args):
        self.btnList[self.hId].disable(None)
        self.hId = -1


    def left(self, args):
        if self.hId <= 0:
            return True

        if self.hId != -1:
            self.btnList[self.hId].disable(None)

            self.hId = clipInt(self.hId - 1, 0, len(self.btnList)-1)
            self.btnList[self.hId].enable(None)

        return False


    def right(self, args):
        if self.hId != -1:
            self.btnList[self.hId].disable(None)

        self.hId = clipInt(self.hId + 1, 0, len(self.btnList)-1)
        self.btnList[self.hId].enable(None)

    def size_change(self, widget, value):
        if self.back is not None:
            self.back.size = value

    def pos_change(self, widget, value):
        if self.back is not None:
            self.back.pos = value

    def __init__(self, **kwargs):

        self.bgColor = kwargs.pop('bgColor', (1,1,1,1))
        buttonDesc = kwargs.pop('buttonDesc', [{}])
        id = kwargs.pop('id', [{}])

        super(DialogButtons, self).__init__(**kwargs)
        self.rows = 1
        self.spacing = 10
        self.padding = (10,0,0,0)

        with self.canvas:
            Color(*self.bgColor)

            if self.parent is not None:
                tmpWidth = self.parent.width
            else:
                tmpWidth = Window.width

            size = (tmpWidth, self.height)
            self.back = Rectangle(size=size, pos=self.pos)

        self.btnList = []
        self.callbackList = []

        for node in buttonDesc:
            if len(buttonDesc) > 0 and node is not None:
                self.callbackList.append(node['callback'])
                self.btnList.append(
                    SelectButton(
                        source= "atlas://resources/img/pi-player/" + node['imgPath'],
                        height=self.height,
                        size_hint_y=None,
                        size_hint_x=None,
                        width=self.height,
                        background_color=includes.styles['menuBarColor'],
                        enaColor=includes.styles['enaColor0']
                    )
                )

                self.add_widget(self.btnList[-1])


            else:
                return

        self.hId = -1

        self.bind(size=self.size_change)
        self.bind(pos=self.pos_change)


class Dialog(GridLayout):

    def enable(self, args):
        return self.btn.enable(args)

    def disable(self, args):
        return self.btn.disable(args)

    def enter(self, args):
        return self.btn.enter(args)

    def right(self, args):
        return self.btn.right(args)

    def left(self, args):
        return self.btn.left(args)

    def __init__(self, **kwargs):
        self.contentColor = kwargs.pop('contentColor', (1, 1, 1, 1))
        self.textColor = kwargs.pop('textColor', (1, 1, 1, 1))
        self.headerColor = kwargs.pop('headerColor', (1, 1, 1, 1))
        self.headerHeight = kwargs.pop('headerHeight', 50)
        self.contentHeight = kwargs.pop('contentHeight', 100)
        self.headerText = kwargs.pop('headerText', "No header text")
        self.text = kwargs.pop('text', "No content text")
        self.borderHeight = kwargs.pop('borderHeight', 2)
        self.sidebarWidth = kwargs.pop('sidebarWidth', 40)
        self.buttonDesc = kwargs.pop('buttonDesc', None)
        self.dId = kwargs.pop('dId', -1)

        super(Dialog, self).__init__()

        self.cols = 1

        if self.buttonDesc is not None:
            self.rows = 4
        else:
            self.rows = 3

        self.headerContent = SelectLabelBg(
            background_color=self.headerColor,
            text=self.headerText,
            size_hint_y=None,
            height=self.headerHeight,
            color=self.textColor,
            valign="middle",
            halign="left",
            padding=[20, 0]
        )

        self.add_widget(self.headerContent)

        self.content = SelectLabelBg(
            background_color=self.contentColor,
            text=self.text,
            color=self.textColor,
            halign="justify",
            valign="top",
            size_hint_y=None,
            height=self.contentHeight,
            padding=[20, 0]
        )
        self.add_widget(self.content)

        if self.buttonDesc is not None:
            self.btn = DialogButtons(
                buttonDesc=self.buttonDesc,
                bgColor=self.contentColor,
                size_hint_y=None,
                height=40,
                id=self.id
            )
            self.add_widget(self.btn)
            self.height = self.headerHeight + self.contentHeight


class DialogHandler(StackLayout):
    dialogList = []
    wId = -1
    sema = None
    logfile = None

    def getNextId(self):
        return len(self.dialogList)

    def right(self, args):
        if self.wId >= 0 and len(self.dialogList) != 0:
            self.dialogList[self.wId].right(args)

    def left(self, args):
        if self.wId >= 0 and len(self.dialogList) != 0:
            ret = self.dialogList[self.wId].left(args)
            return ret

    def disable(self, args):

        if self.wId >= 0 and self.wId < len(self.dialogList):
            self.dialogList[self.wId].disable(args)
            self.wId = self.wId - 1
            self.wId = clipInt(self.wId, -1, len(self.dialogList)-1)


            if self.wId >= 0:
                self.dialogList[self.wId].enable(args)

        if self.wId < 0 or len(self.dialogList) == 0:
            self.wId = -1
            return True

        return False

    def enable(self, args):
        if len(self.dialogList) == 0:
            return True

        if self.wId < 0:
            self.wId = 0
            self.dialogList[self.wId].enable(args)

        elif self.wId >= 0 and self.wId < len(self.dialogList):
            self.dialogList[self.wId].disable(args)
            self.wId = self.wId + 1
            self.wId = clipInt(self.wId, 0, len(self.dialogList)-1)
            self.dialogList[self.wId].enable(args)

        return False


    def enter(self, args):
        if self.wId >= 0 and self.wId <= len(self.dialogList) and len(self.dialogList) > 0:
            self.dialogList[self.wId].enter(args)

            if len(self.dialogList) == 0:
                return True

        return False

    def _updateView(self):
        self.clear_widgets()

        i = 0
        for widget in self.dialogList:
            self.add_widget(widget)

    def _removeDialog(self, dialogId):
        logging.debug("Dialog: called")
        if len(self.dialogList) <= 0:
            logging.debug("Dialog: remove: dialog list empty")
            return

        for i in range(len(self.dialogList)):
            logging.debug("Dialog: find id = {}".format(self.dialogList[i].id))
            if self.dialogList[i].dId == dialogId:
                logging.debug("Dialog: id found so remove now")
                widget = self.dialogList.pop(i)
                break

        self._updateView()
        for item in self.dialogList:
            item.disable(None)

        self.wId = clipInt(self.wId - 1, 0, len(self.dialogList)-1)


        if len(self.dialogList) > 0:
            self.dialogList[self.wId].enable(None)

    def add(self, dialog):
        self.dialogList.append(dialog)
        self._updateView()


    def __init__(self, **kwargs):
        super(DialogHandler, self).__init__(**kwargs)

        #self.cols = 1
        self.dialogList = []
        self.wId = -1
        self.sema = threading.Semaphore()


#
# Debug/Test application for manual testing
#
from kivy.app import App
from subprocess import threading
import time
class TestDialogButtons(App):
    widget = None

    def _taskThread(self):
        tSleep = 0.5

        time.sleep(2)
        for i in range(5):


            #Just enable the list, firts button should be highlighted
            self.widget.enable(None)
            time.sleep(tSleep)

            #move to next button on the right
            self.widget.right(None)
            self.widget.enter(None)
            time.sleep(tSleep)

            #enable the list a second time, this should not change anything
            self.widget.enable(None)
            time.sleep(tSleep)

            #move back to the first button
            self.widget.left(None)
            self.widget.enter(None)
            time.sleep(tSleep)

            #disable buttons
            self.widget.disable(None)
            time.sleep(tSleep)

        self.widget.enable(None)

        for i in range(5):
            self.widget.left(None)
            self.widget.enter(None)
            time.sleep(tSleep)

        for i in range(5):
            self.widget.right(None)
            self.widget.enter(None)
            time.sleep(tSleep)

        for i in range(5):
            self.widget.left(None)
            self.widget.enter(None)
            time.sleep(tSleep)


    def close(self, args):
        logging.error("TestDialogButtons: close button executed")

    def smallPlay(self, args):
        logging.error("TestDialogButtons: smallPlay button executed")

    def build(self):
        buttonDesc = [
            {
                'callback': self.close,
                'imgPath' : "close"
            },
            {
                'callback': self.smallPlay,
                'imgPath' : "small_play"
            }
        ]

        self.widget = DialogButtons(
            buttonDesc=buttonDesc,
            size_hint_y=None,
            height=37.5
        )

        self.thread = threading.Thread(target=self._taskThread)
        self.thread.setDaemon(True)
        self.thread.start()


        return self.widget

class TestInfoDialog(App):

    def build(self):
        widget = InfoDialog(headerText="Thomas", text="ich bin ein text", height=100, closeCallback=None, id=1)

        return widget.dialog


class DialogMain(App):
    '''This is just a Kivy app for testing the dialog widgets on its own'''
    def build(self):

        self.handler = DialogHandler()
        id = self.handler.getNextId()
        tmpDialog = msgAutoRestart(self.handler, "This is content text", "I am the header", 90, id)
        self.handler.add(tmpDialog)



        self.thread = threading.Thread(target=self._taskThread)
        self.thread.setDaemon(True)
        self.thread.start()

        return self.handler


    def _taskThread(self):
        time.sleep(2)
        tSleep = 1

        self.handler.enable(None)
        time.sleep(tSleep)

        self.handler.enter(None)
        time.sleep(tSleep)


        #######
        return

        #Enable first element and then disable
        logging.info("Test: Enable first and disable first")
        self.handler.enable(None)
        time.sleep(tSleep)

        self.handler.disable(None)
        time.sleep(tSleep)

        #Eneable first and second element and then disable only once --> 1st is enabled
        logging.info("Test: Enable first and secodn and disable second")
        self.handler.enable(None)
        time.sleep(tSleep)

        self.handler.enable(None)
        time.sleep(tSleep)

        self.handler.disable(None)
        time.sleep(tSleep)

        #enable 4 times even though we have only one three elements
        logging.info("Test: Enable 1,2,3 and 4,5 event though 4,5 not exits")
        self.handler.enable(None)
        time.sleep(tSleep)

        self.handler.enable(None)
        time.sleep(tSleep)

        self.handler.enter(None)
        time.sleep(tSleep)

        self.handler.disable(None)
        time.sleep(tSleep)

        self.handler.enter(None)
        time.sleep(tSleep)

        self.handler.enter(None)
        time.sleep(tSleep)

        self.handler.logfile.close()
        return


if __name__ == "__main__":
    DialogMain().run()
    #TestDialogButtons().run()
    #TestInfoDialog().run()
