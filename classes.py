from Tkinter import *
import tkFont

class clsEPB_status():
    def __init__(self):

        self.EPB_apply = "EPB_apply"
        self.EPB_release = "EPB_release"
        self.EPB_off = "EPB_off"


EPB_status = clsEPB_status()

class clsSB_status():
    def __init__(self):
        self.SB_apply = "SB_apply"
        self.SB_release = "SB_release"


SB_status = clsSB_status()

class clsEPB_SB_cmd_status():
    def __init__(self):
        self.EPB_cur = EPB_status.EPB_off
        self.SB_cur = SB_status.SB_release
        self.EPB_cmd = EPB_status.EPB_off
        self.SB_cmd = SB_status.SB_release

EPB_SB_cmd_status = clsEPB_SB_cmd_status()

class clsAutoStatus():
    def __init__(self):
        self.init = "init"
        self.running = "running"
        self.pause = "pause"
        self.continuing = "continuing"
        self.finished = "finished"

AutoStatus = clsAutoStatus()

class clsAuto_cmd_Status():
    def __init__(self):
        self.status_cur = AutoStatus.init
        self.status_cmd = AutoStatus.init

Auto_cmd_Status = clsAuto_cmd_Status()


root = Tk()


myFont = tkFont.Font(family='Helvetica', size=20, weight='bold')
btnFont = tkFont.Font(family='Helvetica', size=20, weight='bold')
radioFont = tkFont.Font(family='Helvetica', size=18, weight='bold')
nfnRadioFont = tkFont.Font(family='Helvetica', size=10, weight='bold')
labelFont = tkFont.Font(family='Helvetica', size=18, weight='bold')
listboxFont = tkFont.Font(family='Consolas', size=8)


rValueApplyRelease = StringVar()
SB_rValueApplyRelease = StringVar()
MfmSelection = StringVar()
rValueAutoStartStop = StringVar()
# Mfm03_S1f02_S2f02_S3f01_S4f01 Script editor, digits selector for cycles
rValueFrm0302020101 = IntVar()
# Mfm03_S1f02_S2f02_S3f02_S4f01 Script editor, digits selector for time
rValueFrm0302020201 = DoubleVar()
# Mfm03_S1f02_S2f02_S3f03 Script editor, EPB status selector
rValueFrm03020203_1 = StringVar()
# Mfm03_S1f02_S2f02_S3f03 Script editor, SB status selector
rValueFrm03020203_2 = StringVar()


class NaviFrames(Frame):

    def __init__(self, *args, **kwargs):
        Frame.__init__(self, *args, **kwargs)
        self.pack()


class NfnRadios(Radiobutton):

    def __init__(self, *args, **kwargs):
        Radiobutton.__init__(self, *args, **kwargs)
        self["font"] = nfnRadioFont
        self["indicatoron"] = 0
        self.pack(side=LEFT, anchor=W)


class MainFrames(Frame):

    def __init__(self, *args, **kwargs):
        Frame.__init__(self, *args, **kwargs)
        self["highlightbackground"] = "black"
        self["highlightthickness"] = 2
        self.pack(side="top", fill="both", expand=True)

    def show(self):
        self.lift()


class SubFrames1(Frame):

    def __init__(self, *args, **kwargs):
        Frame.__init__(self, *args, **kwargs)
        self["highlightbackground"] = "black"
        self["highlightthickness"] = 1
        self.pack(fill=X)


class SubFrames2(Frame):

    def __init__(self, *args, **kwargs):
        Frame.__init__(self, *args, **kwargs)
        self["highlightbackground"] = "black"
        self["highlightthickness"] = 1
        self.pack(side=LEFT)


class SubFrames3(Frame):

    def __init__(self, *args, **kwargs):
        Frame.__init__(self, *args, **kwargs)
        self["highlightbackground"] = "black"
        self["highlightthickness"] = 1
        self.pack()


class SubFrames4(Frame):

    def __init__(self, *args, **kwargs):
        Frame.__init__(self, *args, **kwargs)
        self["highlightbackground"] = "black"
        self["highlightthickness"] = 1
        self.pack()


class MainButtons(Button):

    def __init__(self, *args, **kwargs):
        Button.__init__(self, *args, **kwargs)
        self["font"] = btnFont
        self.pack(side=LEFT)


class MainRadios(Radiobutton):

    def __init__(self, *args, **kwargs):
        Radiobutton.__init__(self, *args, **kwargs)
        self["font"] = radioFont
        self.pack(anchor=W)


class MainLables(Label):

    def __init__(self, *args, **kwargs):
        Label.__init__(self, *args, **kwargs)
        self["font"] = labelFont
        self.pack(side=TOP, fill=Y, anchor=W)


class MainListboxes(Listbox):

    def __init__(self, *args, **kwargs):
        Listbox.__init__(self, *args, **kwargs)
        self["font"] = listboxFont
        self.pack()
