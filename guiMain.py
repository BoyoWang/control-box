from Tkinter import *
import RPi.GPIO as GPIO
from time import sleep
import threading

from classes import *
import GPIO_functions as GPIO_functions
import jsonHandle as jsonHandle

# General functions

def readScriptToListbox(listbox, steps):

    def EPB_statusTrans(statusInput):
        if statusInput == glbEPB_status.EPB_apply:
            return " + "
        elif statusInput == glbEPB_status.EPB_release:
            return " - "
        elif statusInput == glbEPB_status.EPB_off:
            return "OFF"

    def SB_statusTrans(statusInput):
        if statusInput == glbSB_status.SB_apply:
            return " + "
        elif statusInput == glbSB_status.SB_release:
            return " - "
    
    
    headerText = "ID|EPB|SB |T"

    listbox.insert(END, headerText)

    for index, step in enumerate(steps):
        text = (
            str(index + 1) + ".|" +
            EPB_statusTrans(step[1]) + "|" +
            SB_statusTrans(step[2]) + "|" +
            str(step[0]) + "s"
        )
        listbox.insert(END, text)


def clearListBox(listbox):
    listbox.delete(0, END)


def exitProgram(event):
    print("Exit Button pressed")
    GPIO_functions.cleanup()
    # GPIO.cleanup()
    root.quit()

# Manual functions

def EPB_SB_cmdApply():
    EPB_cmdCurrIsSame = (glbEPB_SB_cmd_status.EPB_cur == glbEPB_SB_cmd_status.EPB_cmd)
    SB_cmdCurrIsSame = (glbEPB_SB_cmd_status.SB_cur == glbEPB_SB_cmd_status.SB_cmd)
    if not (EPB_cmdCurrIsSame and SB_cmdCurrIsSame):  # Check if cmd is same as cur
        GPIO_functions.outputChange(
            glbEPB_SB_cmd_status.EPB_cmd, 
            glbEPB_SB_cmd_status.SB_cmd, 
            glbEPB_SB_cmd_status.EPB_cur, 
            glbEPB_SB_cmd_status.SB_cur
        )
        glbEPB_SB_cmd_status.EPB_cur = glbEPB_SB_cmd_status.EPB_cmd
        glbEPB_SB_cmd_status.SB_cur = glbEPB_SB_cmd_status.SB_cmd


def manualPowerOn(event):
    if rValueApplyRelease.get() == "Apply":
        glbEPB_SB_cmd_status.EPB_cmd = glbEPB_status.EPB_apply
        EPB_SB_cmdApply()
        Mfm01_S1f01_EPBonOffButton["text"] = "Applying"
        print("Manually applying...")
    elif rValueApplyRelease.get() == "Release":
        glbEPB_SB_cmd_status.EPB_cmd = glbEPB_status.EPB_release
        EPB_SB_cmdApply()
        Mfm01_S1f01_EPBonOffButton["text"] = "Releasing"
        print("Manually releasing...")


def ManualPowerOff(event):
    glbEPB_SB_cmd_status.EPB_cmd = glbEPB_status.EPB_off
    EPB_SB_cmdApply()
    Mfm01_S1f01_EPBonOffButton["text"] = "Off"
    print("Off")


def Manual_SB_onOff():
    if SB_rValueApplyRelease.get() == "SB_apply":
        glbEPB_SB_cmd_status.SB_cmd = glbSB_status.SB_apply
        EPB_SB_cmdApply()
    else:
        glbEPB_SB_cmd_status.SB_cmd = glbSB_status.SB_release
        EPB_SB_cmdApply()


# Automatic functions

class clsScriptInfo():
    def __init__(self,
                 totalCycles=1,
                 importedSteps=[[
                     0.5,
                     glbEPB_status.EPB_off,
                     glbSB_status.SB_release
                 ]]):
        self.totalCycles = totalCycles
        self.totalSteps = len(importedSteps)
        self.steps = importedSteps
        self.currentCycle = 0
        self.currentStep = 0


Auto_exitSignal = threading.Event()


def Auto_cmdApply():
    Auto_cmdCurrIsSame = (Auto_cmd_Status.status_cur ==
                          Auto_cmd_Status.status_cmd)
    if not (Auto_cmdCurrIsSame):  # Check if cmd is same as cur
        Auto_cmd_Status.status_cur = Auto_cmd_Status.status_cmd
        Auto_cmd_StatusIsRunning = (
            Auto_cmd_Status.status_cmd == glbAutoStatus.running)
        Auto_cmd_StatusIsContinuing = (
            Auto_cmd_Status.status_cmd == glbAutoStatus.continuing)
        if (Auto_cmd_StatusIsRunning or Auto_cmd_StatusIsContinuing):
            Auto_start(None)
        print("Auto_cmd_Status changed to " + Auto_cmd_Status.status_cur)


def Auto_refreshWidgets():

    Mfm02_S1f02_label["text"] = "Cycles : " + \
        str(ScriptInfo.currentCycle) + \
        " / " + str(ScriptInfo.totalCycles)

    Mfm02_S1f01_label["text"] = "Steps : " + \
        str(ScriptInfo.currentStep) + \
        " / " + str(ScriptInfo.totalSteps)
    
    isRunning = (
        (Auto_cmd_Status.status_cur == glbAutoStatus.running) or 
        (Auto_cmd_Status.status_cur == glbAutoStatus.continuing)
    )
    
    def BtnsStatusChange(normalOrDisabled):
        Nfn01_Mfm01SelectRadio["state"] = normalOrDisabled
        Nfn01_Mfm02SelectRadio["state"] = normalOrDisabled
        Nfn01_Mfm03SelectRadio["state"] = normalOrDisabled
        exitButton["state"] = normalOrDisabled
        Mfm02_S1f02_resetBtn["state"] = normalOrDisabled

    if isRunning:
        StartRadioText = "Running"

    elif Auto_cmd_Status.status_cur == glbAutoStatus.finished:
        StartRadioText = "Finished"
    else:
        StartRadioText = "Start"
    
    if isRunning:
        BtnsStatusChange(DISABLED)
    else:
        BtnsStatusChange(NORMAL)
    
    Mfm02_S1f02_startRadio["text"] = StartRadioText
    clearListBox(Mfm02_S1f01_listbox)
    readScriptToListbox(Mfm02_S1f01_listbox, ScriptInfo.steps)
    Mfm02_S1f01_listbox.selection_clear(0,END)
    Mfm02_S1f01_listbox.selection_set(ScriptInfo.currentStep)


def Auto_start(event):

    def autoStep(time, EPB, SB):
        glbEPB_SB_cmd_status.EPB_cmd = EPB
        glbEPB_SB_cmd_status.SB_cmd = SB
        EPB_SB_cmdApply()

        print("step " + str(ScriptInfo.currentStep) + " : " +
              str(time) + " s, " + "EPB : " + EPB + ", SB : " + SB)
        Auto_exitSignal.wait(time)

    def autoFinish():
        glbEPB_SB_cmd_status.EPB_cmd = glbEPB_status.EPB_off
        # glbEPB_SB_cmd_status.SB_cmd = glbSB_status.SB_release
        EPB_SB_cmdApply()

    def Auto_cur_StatusIsRunningOrContinuing():
        Auto_cur_StatusIsRunning = (
            Auto_cmd_Status.status_cur == glbAutoStatus.running)
        Auto_cur_StatusIsContinuing = (
            Auto_cmd_Status.status_cur == glbAutoStatus.continuing)
        return (Auto_cur_StatusIsRunning or Auto_cur_StatusIsContinuing)

    def isLastCycleLastStep():
        ifLastCycle = (ScriptInfo.currentCycle == ScriptInfo.totalCycles)
        ifLastStep = (ScriptInfo.currentStep == ScriptInfo.totalSteps)        
        return ifLastCycle and ifLastStep


    def combineSteps():
        Auto_exitSignal.clear()
        ScriptInfo.totalSteps = len(ScriptInfo.steps)
        while (Auto_cur_StatusIsRunningOrContinuing()):

            if not isLastCycleLastStep(): # check if last cycle last step
                if (ScriptInfo.currentStep + 1) > ScriptInfo.totalSteps:
                    ScriptInfo.currentStep = 0
                if ScriptInfo.currentStep == 0:
                    ScriptInfo.currentCycle += 1

            startStep = ScriptInfo.currentStep
            Auto_refreshWidgets()

            for steps in ScriptInfo.steps[startStep:]:
                if Auto_exitSignal.is_set():
                    break
                else:
                    ScriptInfo.currentStep += 1
                    Auto_refreshWidgets()
                    autoStep(steps[0], steps[1], steps[2])

            if isLastCycleLastStep():
                Auto_cmd_Status.status_cur = glbAutoStatus.finished

            if Auto_exitSignal.is_set():
                break

            Auto_cur_StatusIsRunningOrContinuing()

        if Auto_exitSignal.is_set():
            print("interrupeted!")
            Auto_cmd_Status.status_cur = glbAutoStatus.pause
            autoFinish()
        else:
            autoFinish()
            print("Script finished normally.")

        Auto_refreshWidgets()

    thread = threading.Thread(target=combineSteps)
    thread.start()


def Auto_start_btn(event):
    if Auto_cmd_Status.status_cur == glbAutoStatus.pause:
        Auto_cmd_Status.status_cmd = glbAutoStatus.continuing
    elif Auto_cmd_Status.status_cur == glbAutoStatus.finished:
        Auto_cmd_Status.status_cmd = glbAutoStatus.finished
    else:
        Auto_cmd_Status.status_cmd = glbAutoStatus.running
    Auto_cmdApply()
    Auto_refreshWidgets()


def Auto_quit(event):
    Auto_exitSignal.set()
    print("Stop Buttom Pressed.")
    Auto_refreshWidgets()


def Auto_reset():

    def checkAuto_cur_Status():
        isInit = (Auto_cmd_Status.status_cur == glbAutoStatus.init)
        isPause = (Auto_cmd_Status.status_cur == glbAutoStatus.pause)
        isFinished = (Auto_cmd_Status.status_cur == glbAutoStatus.finished)
        return(isInit or isPause or isFinished)

    if checkAuto_cur_Status():
        ScriptInfo.currentCycle = 0
        ScriptInfo.currentStep = 0
        Auto_cmd_Status.status_cmd = glbAutoStatus.init
        Auto_cmdApply()
        Auto_refreshWidgets()
    
    Mfm02_S1f02_stopRadio.select()

# script functions

def Script_refreshWidgets():
    global Script_editStatus,\
        Mfm03_S1f02_S2f02_S3f01_label,\
        Mfm03_S1f02_S2f02_S3f02_label,\
        Mfm02_S1f01_listbox

    Mfm03_S1f02_S2f02_S3f01_label['text'] = "Cycle : " + \
        str(Script_editStatus.totalCycles)
    
    Mfm03_S1f02_S2f02_S3f02_label['text'] = "Time : " + \
        str(Script_editStatus.stepTime) + " s"

    clearListBox(Mfm03_S1f02_S2f01_listbox)
    readScriptToListbox(Mfm03_S1f02_S2f01_listbox, Script_editStatus.script["steps"])

    
def Script_read():
    global Script_editStatus, Mfm03_S1f02_S2f01_listbox
    Script_editStatus.script = jsonHandle.loadScript()
    Script_editStatus.totalCycles = Script_editStatus.script['totalCycles']
    clearListBox(Mfm03_S1f02_S2f01_listbox)
    Script_refreshWidgets()

def Script_clear():
    global Script_editStatus, glbEPB_status
    dictTemp = {
        'totalCycles' : 1,
        'steps' : [[0.5, glbEPB_status.EPB_off, glbSB_status.SB_release]]
    }
    Script_editStatus.script = dictTemp
    Script_editStatus.totalCycles = 1
    Script_editStatus.EPB_status = glbEPB_status.EPB_off
    Script_editStatus.glbSB_status = glbSB_status.SB_release
    Script_refreshWidgets()

def Script_save():
    print("")


def Script_addStep():
    global Script_editStatus, glbEPB_status
    tempList = []
    tempList = Script_editStatus.script['steps']
    tempList.append([0.5, glbEPB_status.EPB_release, glbSB_status.SB_release])
    Script_refreshWidgets()


root.title("Brake Control System")

# NaviFrame 01
Nfn01 = NaviFrames(root)

container = Frame(root)
container.pack(side="top", fill="both", expand=True)

# MainFrame 01 : Manual control
Mfm01 = MainFrames(root)

# MainFrame 01 - SubFrames1 01 : EPB manual control power On / Off
Mfm01_S1f01 = SubFrames1(Mfm01)
Mfm01_S1f01_applyReleaseLable = MainLables(
    Mfm01_S1f01, text="EPB apply / release:")
Mfm01_S1f01_EPBonOffButton = MainButtons(Mfm01_S1f01, text="Off")
Mfm01_S1f01_EPBonOffButton.bind('<ButtonRelease-1>', ManualPowerOff)
Mfm01_S1f01_EPBonOffButton.bind('<Button>', manualPowerOn)
Mfm01_S1f01_EPB_applyRadio = MainRadios(
    Mfm01_S1f01, text="Apply", variable=rValueApplyRelease, value="Apply")
Mfm01_S1f01_EPB_applyRadio.select()
Mfm01_S1f01_EPB_releaseRadio = MainRadios(
    Mfm01_S1f01, text="Release", variable=rValueApplyRelease, value="Release")

# MainFrame 01 - SubFrames1 02 : Survice Brake Control Frame
Mfm01_S1f02 = SubFrames1(Mfm01)
Mfm01_S1f02_applyReleaseLable = MainLables(
    Mfm01_S1f02, text="Service brake apply / release:")
Mfm01_S1f02_SB_applyRadio = MainRadios(
    Mfm01_S1f02, text="SB_apply", 
    variable=SB_rValueApplyRelease, value="SB_apply", 
    command=Manual_SB_onOff)
Mfm01_S1f02_SB_releaseRadio = MainRadios(
    Mfm01_S1f02, text="SB_release", 
    variable=SB_rValueApplyRelease, value="SB_release", 
    command=Manual_SB_onOff)
Mfm01_S1f02_SB_releaseRadio.select()

# MainFrame 02 : Automatic control
Mfm02 = MainFrames(root)

# MainFrame 02 - SubFrames1 01 : Step viewer
Mfm02_S1f01 = SubFrames1(Mfm02)
Mfm02_S1f01.pack(fill=NONE, side=LEFT)
Mfm02_S1f01_label = MainLables(Mfm02_S1f01, text="Step : 0 / 0")
Mfm02_S1f01_listbox = MainListboxes(Mfm02_S1f01)

# MainFrame 02 - SubFrames1 02 : Controls
Mfm02_S1f02 = SubFrames1(Mfm02)
Mfm02_S1f02.pack(fill=NONE, side=LEFT)
Mfm02_S1f02_label = MainLables(Mfm02_S1f02, text="Cycle : 0 / 0")
Mfm02_S1f02_label.pack(fill=Y)
Mfm02_S1f02_startRadio = MainRadios(
    Mfm02_S1f02, text="Start", variable=rValueAutoStartStop, 
    value="start", indicatoron=0, 
    command=lambda: Auto_start_btn(None)
)
Mfm02_S1f02_stopRadio = MainRadios(
    Mfm02_S1f02, text="Stop", variable=rValueAutoStartStop, 
    value="stop", indicatoron=0, 
    command=lambda: Auto_quit(None)
)
Mfm02_S1f02_stopRadio.select()
Mfm02_S1f02_resetBtn = MainButtons(
    Mfm02_S1f02, text="Reset", command=Auto_reset)

# MainFrame 03 : Script Editor
Mfm03 = MainFrames(root)

# MainFrame 03 - SubFrames1 01 : Read / Clear / Save
Mfm03_S1f01 = SubFrames1(Mfm03)
Mfm03_S1f01_readButton = MainButtons(Mfm03_S1f01, text="Read", 
    command=Script_read)
Mfm03_S1f01_clearButton = MainButtons(Mfm03_S1f01, text="Clear", 
    command=Script_clear)
Mfm03_S1f01_saveButton = MainButtons(Mfm03_S1f01, text="Save", 
    command=Script_save)

# MainFrame 03 - SubFrames1 02 : Script Editor Main
Mfm03_S1f02 = SubFrames1(Mfm03)

# MainFrame 03 - SubFrames1 02 - SubFrames2 01 : Step viewer
Mfm03_S1f02_S2f01 = SubFrames2(Mfm03_S1f02)
Mfm03_S1f02_S2f01_label = MainLables(Mfm03_S1f02_S2f01, text="Steps:")
Mfm03_S1f02_S2f01_listbox = MainListboxes(Mfm03_S1f02_S2f01)

# MainFrame 03 - SubFrames1 02 - SubFrames2 02 : Step editor
Mfm03_S1f02_S2f02 = SubFrames2(Mfm03_S1f02)

# MainFrame 03 - SubFrames1 02 - SubFrames2 02 - SubFrames3 01 : Cycle editor
Mfm03_S1f02_S2f02_S3f01 = SubFrames3(Mfm03_S1f02_S2f02)
Mfm03_S1f02_S2f02_S3f01_label = MainLables(
    Mfm03_S1f02_S2f02_S3f01, text="Cycle : 10")

Mfm03_S1f02_S2f02_S3f01_S4f01 = SubFrames4(Mfm03_S1f02_S2f02_S3f01)

Mfm03_S1f02_S2f02_S3f01_S4f01_100Radio = Radiobutton(
    Mfm03_S1f02_S2f02_S3f01_S4f01, text="100", 
    variable=rValueFrm0302020101, value=100)
Mfm03_S1f02_S2f02_S3f01_S4f01_10Radio = Radiobutton(
    Mfm03_S1f02_S2f02_S3f01_S4f01, text="10", 
    variable=rValueFrm0302020101, value=10)
Mfm03_S1f02_S2f02_S3f01_S4f01_1Radio = Radiobutton(
    Mfm03_S1f02_S2f02_S3f01_S4f01, text="1", 
    variable=rValueFrm0302020101, value=1)

Mfm03_S1f02_S2f02_S3f01_S4f01_plusBtn = Button(
    Mfm03_S1f02_S2f02_S3f01_S4f01, text="+")
Mfm03_S1f02_S2f02_S3f01_S4f01_resetBtn = Button(
    Mfm03_S1f02_S2f02_S3f01_S4f01, text="Reset")
Mfm03_S1f02_S2f02_S3f01_S4f01_minusBtn = Button(
    Mfm03_S1f02_S2f02_S3f01_S4f01, text="-")

Mfm03_S1f02_S2f02_S3f01_S4f01_100Radio.grid(row=1, column=1)
Mfm03_S1f02_S2f02_S3f01_S4f01_10Radio.grid(row=1, column=2)
Mfm03_S1f02_S2f02_S3f01_S4f01_1Radio.grid(row=1, column=3)
Mfm03_S1f02_S2f02_S3f01_S4f01_plusBtn.grid(row=2, column=1)
Mfm03_S1f02_S2f02_S3f01_S4f01_resetBtn.grid(row=2, column=2)
Mfm03_S1f02_S2f02_S3f01_S4f01_minusBtn.grid(row=2, column=3)

# MainFrame 03 - SubFrames1 02 - SubFrames2 02 - SubFrames3 02 : Time editor
Mfm03_S1f02_S2f02_S3f02 = SubFrames3(Mfm03_S1f02_S2f02)
Mfm03_S1f02_S2f02_S3f02_label = MainLables(
    Mfm03_S1f02_S2f02_S3f02, text="Time : 1 s")

Mfm03_S1f02_S2f02_S3f02_S4f01 = SubFrames4(Mfm03_S1f02_S2f02_S3f02)

Mfm03_S1f02_S2f02_S3f02_S4f01_100Radio = Radiobutton(
    Mfm03_S1f02_S2f02_S3f02_S4f01, text="100", 
    variable=rValueFrm0302020201, value=100)
Mfm03_S1f02_S2f02_S3f02_S4f01_10Radio = Radiobutton(
    Mfm03_S1f02_S2f02_S3f02_S4f01, text="10", 
    variable=rValueFrm0302020201, value=10)
Mfm03_S1f02_S2f02_S3f02_S4f01_1Radio = Radiobutton(
    Mfm03_S1f02_S2f02_S3f02_S4f01, text="1", 
    variable=rValueFrm0302020201, value=1)
Mfm03_S1f02_S2f02_S3f02_S4f01_01Radio = Radiobutton(
    Mfm03_S1f02_S2f02_S3f02_S4f01, text="0.1", 
    variable=rValueFrm0302020201, value=0.1)
Mfm03_S1f02_S2f02_S3f02_S4f01_001Radio = Radiobutton(
    Mfm03_S1f02_S2f02_S3f02_S4f01, text="0.01", 
    variable=rValueFrm0302020201, value=0.01)

Mfm03_S1f02_S2f02_S3f02_S4f01_plusBtn = Button(
    Mfm03_S1f02_S2f02_S3f02_S4f01, text="+")
Mfm03_S1f02_S2f02_S3f02_S4f01_resetBtn = Button(
    Mfm03_S1f02_S2f02_S3f02_S4f01, text="Reset")
Mfm03_S1f02_S2f02_S3f02_S4f01_minusBtn = Button(
    Mfm03_S1f02_S2f02_S3f02_S4f01, text="-")

Mfm03_S1f02_S2f02_S3f02_S4f01_100Radio.grid(row=1, column=1)
Mfm03_S1f02_S2f02_S3f02_S4f01_10Radio.grid(row=1, column=2)
Mfm03_S1f02_S2f02_S3f02_S4f01_1Radio.grid(row=1, column=3)
Mfm03_S1f02_S2f02_S3f02_S4f01_01Radio.grid(row=1, column=4)
Mfm03_S1f02_S2f02_S3f02_S4f01_001Radio.grid(row=1, column=5)
Mfm03_S1f02_S2f02_S3f02_S4f01_plusBtn.grid(row=2, column=1)
Mfm03_S1f02_S2f02_S3f02_S4f01_resetBtn.grid(row=2, column=2)
Mfm03_S1f02_S2f02_S3f02_S4f01_minusBtn.grid(row=2, column=3)

# MainFrame 03 - SubFrames1 02 - SubFrames2 02 - SubFrames3 03 : 
# EPB / SB status selector
Mfm03_S1f02_S2f02_S3f03 = SubFrames3(Mfm03_S1f02_S2f02)
Mfm03_S1f02_S2f02_S3f03_EPBLabel = Label(Mfm03_S1f02_S2f02_S3f03, text="EPB :")
Mfm03_S1f02_S2f02_S3f03_EPBApplyRadio = Radiobutton(
    Mfm03_S1f02_S2f02_S3f03, text="Apply", 
    variable=rValueFrm03020203_1, value="apply")
Mfm03_S1f02_S2f02_S3f03_EPBReleaseRadio = Radiobutton(
    Mfm03_S1f02_S2f02_S3f03, text="Release", 
    variable=rValueFrm03020203_1, value="release")
Mfm03_S1f02_S2f02_S3f03_EPBOffRadio = Radiobutton(
    Mfm03_S1f02_S2f02_S3f03, text="Off", 
    variable=rValueFrm03020203_1, value="off")
Mfm03_S1f02_S2f02_S3f03_EPBOffRadio.select()

Mfm03_S1f02_S2f02_S3f03_SBLabel = Label(Mfm03_S1f02_S2f02_S3f03, text="SB :")
Mfm03_S1f02_S2f02_S3f03_SBApplyRadio = Radiobutton(
    Mfm03_S1f02_S2f02_S3f03, text="Apply", 
    variable=rValueFrm03020203_2, value="apply")
Mfm03_S1f02_S2f02_S3f03_SBReleaseRadio = Radiobutton(
    Mfm03_S1f02_S2f02_S3f03, text="Release", 
    variable=rValueFrm03020203_2, value="release")
Mfm03_S1f02_S2f02_S3f03_SBReleaseRadio.select()

Mfm03_S1f02_S2f02_S3f03_EPBLabel.grid(row=1, column=1)
Mfm03_S1f02_S2f02_S3f03_EPBApplyRadio.grid(row=1, column=2)
Mfm03_S1f02_S2f02_S3f03_EPBReleaseRadio.grid(row=1, column=3)
Mfm03_S1f02_S2f02_S3f03_EPBOffRadio.grid(row=1, column=4)

Mfm03_S1f02_S2f02_S3f03_SBLabel.grid(row=2, column=1)
Mfm03_S1f02_S2f02_S3f03_SBApplyRadio.grid(row=2, column=2)
Mfm03_S1f02_S2f02_S3f03_SBReleaseRadio.grid(row=2, column=3)

# MainFrame 03 - SubFrames1 02 - SubFrames2 02 - SubFrames3 04 : 
# add / delete step
Mfm03_S1f02_S2f02_S3f04 = SubFrames3(Mfm03_S1f02_S2f02)
Mfm03_S1f02_S2f02_S3f04_addBtn = MainButtons(
    Mfm03_S1f02_S2f02_S3f04, text="Add", command=Script_addStep)
Mfm03_S1f02_S2f02_S3f04_deleteBtn = MainButtons(
    Mfm03_S1f02_S2f02_S3f04, text="delete")


root.wm_geometry("800x600")

Mfm01.place(in_=container, x=0, y=0, relwidth=1, relheight=1)
Mfm02.place(in_=container, x=0, y=0, relwidth=1, relheight=1)
Mfm03.place(in_=container, x=0, y=0, relwidth=1, relheight=1)

Nfn01_Mfm01SelectRadio = NfnRadios(
    Nfn01, text="Manual", 
    variable=MfmSelection, value="Mfm01", command=Mfm01.lift)
Nfn01_Mfm02SelectRadio = NfnRadios(
    Nfn01, text="Automatic", 
    variable=MfmSelection, value="Mfm02", command=Mfm02.lift)
Nfn01_Mfm03SelectRadio = NfnRadios(
    Nfn01, text="Script", 
    variable=MfmSelection, value="Mfm03", command=Mfm03.lift)
Nfn01_Mfm01SelectRadio.select()

Mfm01.show()

exitButton = Button(root, text="Exit", font=myFont, height=2, width=6)
exitButton.bind('<Button-1>', exitProgram)
exitButton.pack(side=BOTTOM)


# functions to execute after windows is loaded
impoortedSteps = jsonHandle.loadScript()
Script_read()

ScriptInfo = clsScriptInfo(
    impoortedSteps['totalCycles'], 
    impoortedSteps['steps']
)

Auto_refreshWidgets()
Script_refreshWidgets()

root.mainloop()
