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


def testAnythingHere(event):
    global Script_editStatus, glbEPB_status, Mfm03_S1f02_S2f01_listbox
    listBoxIsSelected = (
        len(Mfm03_S1f02_S2f01_listbox.curselection()) == 1)
    print(listBoxIsSelected)
    if listBoxIsSelected:
        listBoxSelectedIndex = Mfm03_S1f02_S2f01_listbox.curselection()[0]
        print(listBoxSelectedIndex)


def exitProgram(event):
    print("Exit Button pressed")
    GPIO_functions.cleanup()
    # GPIO.cleanup()
    root.quit()

# Manual functions


def EPB_SB_cmdApply():
    EPB_cmdCurrIsSame = (glbEPB_SB_cmd_status.EPB_cur ==
                         glbEPB_SB_cmd_status.EPB_cmd)
    SB_cmdCurrIsSame = (glbEPB_SB_cmd_status.SB_cur ==
                        glbEPB_SB_cmd_status.SB_cmd)
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


def radioDirectSwitch():
    dummy = ""
    if rValueApplyRelease.get() == "Apply":
        manualPowerOn(dummy)
    elif rValueApplyRelease.get() == "Release":
        manualPowerOn(dummy)
    elif rValueApplyRelease.get() == "Off":
        ManualPowerOff(dummy)


def Manual_SB_onOff():
    if SB_rValueApplyRelease.get() == "SB_apply":
        glbEPB_SB_cmd_status.SB_cmd = glbSB_status.SB_apply
        EPB_SB_cmdApply()
    else:
        glbEPB_SB_cmd_status.SB_cmd = glbSB_status.SB_release
        EPB_SB_cmdApply()


# Automatic functions


Auto_exitSignal = threading.Event()


def Auto_cmdApply():
    Auto_cmdCurrIsSame = (glbAuto_cmd_Status.status_cur ==
                          glbAuto_cmd_Status.status_cmd)
    if not (Auto_cmdCurrIsSame):  # Check if cmd is same as cur
        glbAuto_cmd_Status.status_cur = glbAuto_cmd_Status.status_cmd
        Auto_cmd_StatusIsRunning = (
            glbAuto_cmd_Status.status_cmd == glbAutoStatus.running)
        Auto_cmd_StatusIsContinuing = (
            glbAuto_cmd_Status.status_cmd == glbAutoStatus.continuing)
        if (Auto_cmd_StatusIsRunning or Auto_cmd_StatusIsContinuing):
            Auto_start(None)
        print("glbAuto_cmd_Status changed to " + glbAuto_cmd_Status.status_cur)


def Auto_refreshWidgets():

    Mfm02_S1f02_label["text"] = "Cycles : " + \
        str(glbAuto_scriptInfo.currentCycle) + \
        " / " + str(glbAuto_scriptInfo.totalCycles)

    Mfm02_S1f01_label["text"] = "Steps : " + \
        str(glbAuto_scriptInfo.currentStep) + \
        " / " + str(glbAuto_scriptInfo.totalSteps)

    isRunning = (
        (glbAuto_cmd_Status.status_cur == glbAutoStatus.running) or
        (glbAuto_cmd_Status.status_cur == glbAutoStatus.continuing)
    )

    def BtnsStatusChange(normalOrDisabled):
        Nfn01_Mfm01SelectRadio["state"] = normalOrDisabled
        Nfn01_Mfm02SelectRadio["state"] = normalOrDisabled
        Nfn01_Mfm03SelectRadio["state"] = normalOrDisabled
        exitButton["state"] = normalOrDisabled
        Mfm02_S1f02_resetBtn["state"] = normalOrDisabled

    if isRunning:
        StartRadioText = "Running"

    elif glbAuto_cmd_Status.status_cur == glbAutoStatus.finished:
        StartRadioText = "Finished"
    else:
        StartRadioText = "Start"

    if isRunning:
        BtnsStatusChange(DISABLED)
    else:
        BtnsStatusChange(NORMAL)

    Mfm02_S1f02_startRadio["text"] = StartRadioText
    clearListBox(Mfm02_S1f01_listbox)
    readScriptToListbox(Mfm02_S1f01_listbox, glbAuto_scriptInfo.steps)
    Mfm02_S1f01_listbox.selection_clear(0, END)
    Mfm02_S1f01_listbox.selection_set(glbAuto_scriptInfo.currentStep)


def Auto_start(event):

    def autoStep(time, EPB, SB):
        glbEPB_SB_cmd_status.EPB_cmd = EPB
        glbEPB_SB_cmd_status.SB_cmd = SB
        EPB_SB_cmdApply()

        print("step " + str(glbAuto_scriptInfo.currentStep) + " : " +
              str(time) + " s, " + "EPB : " + EPB + ", SB : " + SB)
        Auto_exitSignal.wait(time)

    def autoFinish():
        glbEPB_SB_cmd_status.EPB_cmd = glbEPB_status.EPB_off
        # glbEPB_SB_cmd_status.SB_cmd = glbSB_status.SB_release
        EPB_SB_cmdApply()

    def Auto_cur_StatusIsRunningOrContinuing():
        Auto_cur_StatusIsRunning = (
            glbAuto_cmd_Status.status_cur == glbAutoStatus.running)
        Auto_cur_StatusIsContinuing = (
            glbAuto_cmd_Status.status_cur == glbAutoStatus.continuing)
        return (Auto_cur_StatusIsRunning or Auto_cur_StatusIsContinuing)

    def isLastCycleLastStep():
        ifLastCycle = (glbAuto_scriptInfo.currentCycle ==
                       glbAuto_scriptInfo.totalCycles)
        ifLastStep = (glbAuto_scriptInfo.currentStep ==
                      glbAuto_scriptInfo.totalSteps)
        return ifLastCycle and ifLastStep

    def combineSteps():
        Auto_exitSignal.clear()
        glbAuto_scriptInfo.totalSteps = len(glbAuto_scriptInfo.steps)
        while (Auto_cur_StatusIsRunningOrContinuing()):

            if not isLastCycleLastStep():  # check if last cycle last step
                if (glbAuto_scriptInfo.currentStep + 1) > glbAuto_scriptInfo.totalSteps:
                    glbAuto_scriptInfo.currentStep = 0
                if glbAuto_scriptInfo.currentStep == 0:
                    glbAuto_scriptInfo.currentCycle += 1

            startStep = glbAuto_scriptInfo.currentStep
            Auto_refreshWidgets()

            for steps in glbAuto_scriptInfo.steps[startStep:]:
                if Auto_exitSignal.is_set():
                    break
                else:
                    glbAuto_scriptInfo.currentStep += 1
                    Auto_refreshWidgets()
                    autoStep(steps[0], steps[1], steps[2])

            if isLastCycleLastStep():
                glbAuto_cmd_Status.status_cur = glbAutoStatus.finished

            if Auto_exitSignal.is_set():
                break

            Auto_cur_StatusIsRunningOrContinuing()

        if Auto_exitSignal.is_set():
            print("interrupeted!")
            glbAuto_cmd_Status.status_cur = glbAutoStatus.pause
            autoFinish()
        else:
            autoFinish()
            print("Script finished normally.")

        Auto_refreshWidgets()

    thread = threading.Thread(target=combineSteps)
    thread.start()


def Auto_start_btn(event):
    if glbAuto_cmd_Status.status_cur == glbAutoStatus.pause:
        glbAuto_cmd_Status.status_cmd = glbAutoStatus.continuing
    elif glbAuto_cmd_Status.status_cur == glbAutoStatus.finished:
        glbAuto_cmd_Status.status_cmd = glbAutoStatus.finished
    else:
        glbAuto_cmd_Status.status_cmd = glbAutoStatus.running
    Auto_cmdApply()
    Auto_refreshWidgets()


def Auto_quit(event):
    Auto_exitSignal.set()
    print("Stop Buttom Pressed.")
    Auto_refreshWidgets()


def Auto_reset():

    def checkAuto_cur_Status():
        isInit = (glbAuto_cmd_Status.status_cur == glbAutoStatus.init)
        isPause = (glbAuto_cmd_Status.status_cur == glbAutoStatus.pause)
        isFinished = (glbAuto_cmd_Status.status_cur == glbAutoStatus.finished)
        return(isInit or isPause or isFinished)

    if checkAuto_cur_Status():
        glbAuto_scriptInfo.currentCycle = 0
        glbAuto_scriptInfo.currentStep = 0
        glbAuto_cmd_Status.status_cmd = glbAutoStatus.init
        Auto_cmdApply()
        Auto_refreshWidgets()

    Mfm02_S1f02_stopRadio.select()

# script functions


def Script_refreshWidgets():
    global Script_editStatus,\
        Mfm03_S1f02_S2f02_S3f01_label,\
        Mfm03_S1f02_S2f02_S3f02_label,\
        Mfm03_S1f02_S2f01_listbox

    Mfm03_S1f02_S2f02_S3f01_label['text'] = "Cycle : " + \
        str(Script_editStatus.totalCycles)

    Mfm03_S1f02_S2f02_S3f02_label['text'] = "Time : " + \
        str(Script_editStatus.stepTime) + " s"

    clearListBox(Mfm03_S1f02_S2f01_listbox)
    readScriptToListbox(Mfm03_S1f02_S2f01_listbox,
                        Script_editStatus.script["steps"])


def Script_read():
    global Script_editStatus, \
        glbAuto_scriptInfo, \
        Mfm03_S1f02_S2f01_listbox, \
        Mfm02_S1f01_listbox

    dictTemp = jsonHandle.loadScript()

    Script_editStatus.script = dictTemp
    Script_editStatus.totalCycles = dictTemp['totalCycles']

    glbAuto_scriptInfo.script = dictTemp
    glbAuto_scriptInfo.totalCycles = dictTemp['totalCycles']
    glbAuto_scriptInfo.steps = dictTemp['steps']

    Script_refreshWidgets()
    Auto_refreshWidgets()


def Script_clear():
    global Script_editStatus, glbEPB_status
    dictTemp = {
        'totalCycles': 1,
        'steps': [[0.5, glbEPB_status.EPB_off, glbSB_status.SB_release]]
    }
    Script_editStatus.script = dictTemp
    Script_editStatus.totalCycles = 1
    Script_editStatus.EPB_status = glbEPB_status.EPB_off
    Script_editStatus.glbSB_status = glbSB_status.SB_release
    Script_refreshWidgets()


def Script_save():
    jsonHandle.saveScript(Script_editStatus.script)
    Script_read()


def Script_cycleModBtns(mode):
    global Script_editStatus, rValueFrm0302020101
    temp = rValueFrm0302020101.get()

    if mode == "plus":
        Script_editStatus.totalCycles += temp
    elif mode == "minus":
        Script_editStatus.totalCycles -= temp
    elif mode == "reset":
        Script_editStatus.totalCycles = 1

    if Script_editStatus.totalCycles < 1:
        Script_editStatus.totalCycles = 1

    Script_editStatus.script['totalCycles'] = Script_editStatus.totalCycles
    Script_refreshWidgets()


def Script_timeModBtns(mode):
    global Script_editStatus, rValueFrm0302020201
    temp = rValueFrm0302020201.get()

    if mode == "plus":
        Script_editStatus.stepTime += temp
    elif mode == "minus":
        Script_editStatus.stepTime -= temp
    elif mode == "reset":
        Script_editStatus.stepTime = 1

    if Script_editStatus.stepTime < 0.01:
        Script_editStatus.stepTime = 0.01

    Script_editStatus.stepTime = round(Script_editStatus.stepTime, 2)

    Script_refreshWidgets()


def Script_addStep():
    global Script_editStatus, glbEPB_status, Mfm03_S1f02_S2f01_listbox

    listBoxIsSelected = (
        len(Mfm03_S1f02_S2f01_listbox.curselection()) == 1)
    if listBoxIsSelected:
        listBoxSelectedIndex = Mfm03_S1f02_S2f01_listbox.curselection()[0]

    stepTime = Script_editStatus.stepTime
    EPB = rValueFrm03020203_1.get()
    SB = rValueFrm03020203_2.get()
    tempList = Script_editStatus.script['steps']
    if listBoxIsSelected:
        tempList.insert(listBoxSelectedIndex, [stepTime, EPB, SB])
    else:
        tempList.append([stepTime, EPB, SB])
    Script_refreshWidgets()


def Script_delStep():
    global Script_editStatus, Mfm03_S1f02_S2f01_listbox

    listBoxIsSelected = (
        len(Mfm03_S1f02_S2f01_listbox.curselection()) == 1)
    if listBoxIsSelected:
        listBoxSelectedIndex = Mfm03_S1f02_S2f01_listbox.curselection()[0]

    steps = Script_editStatus.script['steps']
    stepAmt = len(steps)

    if listBoxIsSelected and (stepAmt > 1):
        steps.pop(listBoxSelectedIndex-1)
    elif stepAmt > 1:
        steps.pop(-1)
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
Mfm01_S1f01_EPB_applyRadio = MainRadios(
    Mfm01_S1f01, text="Apply", command=radioDirectSwitch, indicatoron=0,
    variable=rValueApplyRelease, value="Apply", width=7, height=2)
Mfm01_S1f01_EPB_offRadio = MainRadios(
    Mfm01_S1f01, text="Off", command=radioDirectSwitch, indicatoron=0,
    variable=rValueApplyRelease, value="Off", width=7, height=2)
Mfm01_S1f01_EPB_offRadio.select()
Mfm01_S1f01_EPB_releaseRadio = MainRadios(
    Mfm01_S1f01, text="Release", command=radioDirectSwitch, indicatoron=0,
    variable=rValueApplyRelease, value="Release", width=7, height=2)


# MainFrame 01 - SubFrames1 02 : Survice Brake Control Frame
Mfm01_S1f02 = SubFrames1(Mfm01)
Mfm01_S1f02_applyReleaseLable = MainLables(
    Mfm01_S1f02, text="Service brake apply / release:")
Mfm01_S1f02_SB_applyRadio = MainRadios(
    Mfm01_S1f02, text="SB_apply", indicatoron=0,
    variable=SB_rValueApplyRelease, value="SB_apply",
    command=Manual_SB_onOff, width=11, height=2)
Mfm01_S1f02_SB_releaseRadio = MainRadios(
    Mfm01_S1f02, text="SB_release", indicatoron=0,
    variable=SB_rValueApplyRelease, value="SB_release",
    command=Manual_SB_onOff, width=11, height=2)
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
    variable=rValueFrm0302020101, value="100")
Mfm03_S1f02_S2f02_S3f01_S4f01_10Radio = Radiobutton(
    Mfm03_S1f02_S2f02_S3f01_S4f01, text="10",
    variable=rValueFrm0302020101, value="10")
Mfm03_S1f02_S2f02_S3f01_S4f01_1Radio = Radiobutton(
    Mfm03_S1f02_S2f02_S3f01_S4f01, text="1",
    variable=rValueFrm0302020101, value="1")
Mfm03_S1f02_S2f02_S3f01_S4f01_1Radio.select()

Mfm03_S1f02_S2f02_S3f01_S4f01_plusBtn = Button(
    Mfm03_S1f02_S2f02_S3f01_S4f01, text="+",
    command=lambda: Script_cycleModBtns('plus'))
Mfm03_S1f02_S2f02_S3f01_S4f01_resetBtn = Button(
    Mfm03_S1f02_S2f02_S3f01_S4f01, text="Reset",
    command=lambda: Script_cycleModBtns('reset'))
Mfm03_S1f02_S2f02_S3f01_S4f01_minusBtn = Button(
    Mfm03_S1f02_S2f02_S3f01_S4f01, text="-",
    command=lambda: Script_cycleModBtns('minus'))

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
Mfm03_S1f02_S2f02_S3f02_S4f01_1Radio.select()

Mfm03_S1f02_S2f02_S3f02_S4f01_plusBtn = Button(
    Mfm03_S1f02_S2f02_S3f02_S4f01, text="+",
    command=lambda: Script_timeModBtns('plus'))
Mfm03_S1f02_S2f02_S3f02_S4f01_resetBtn = Button(
    Mfm03_S1f02_S2f02_S3f02_S4f01, text="Reset",
    command=lambda: Script_timeModBtns('reset'))
Mfm03_S1f02_S2f02_S3f02_S4f01_minusBtn = Button(
    Mfm03_S1f02_S2f02_S3f02_S4f01, text="-",
    command=lambda: Script_timeModBtns('minus'))

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
    variable=rValueFrm03020203_1, value=glbEPB_status.EPB_apply)
Mfm03_S1f02_S2f02_S3f03_EPBReleaseRadio = Radiobutton(
    Mfm03_S1f02_S2f02_S3f03, text="Release",
    variable=rValueFrm03020203_1, value=glbEPB_status.EPB_release)
Mfm03_S1f02_S2f02_S3f03_EPBOffRadio = Radiobutton(
    Mfm03_S1f02_S2f02_S3f03, text="Off",
    variable=rValueFrm03020203_1, value=glbEPB_status.EPB_off)
Mfm03_S1f02_S2f02_S3f03_EPBOffRadio.select()

Mfm03_S1f02_S2f02_S3f03_SBLabel = Label(Mfm03_S1f02_S2f02_S3f03, text="SB :")
Mfm03_S1f02_S2f02_S3f03_SBApplyRadio = Radiobutton(
    Mfm03_S1f02_S2f02_S3f03, text="Apply",
    variable=rValueFrm03020203_2, value=glbSB_status.SB_apply)
Mfm03_S1f02_S2f02_S3f03_SBReleaseRadio = Radiobutton(
    Mfm03_S1f02_S2f02_S3f03, text="Release",
    variable=rValueFrm03020203_2, value=glbSB_status.SB_release)
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
    Mfm03_S1f02_S2f02_S3f04, text="Add",
    command=Script_addStep)
Mfm03_S1f02_S2f02_S3f04_deleteBtn = MainButtons(
    Mfm03_S1f02_S2f02_S3f04, text="delete",
    command=Script_delStep)


root.wm_geometry("800x600")

Mfm01.place(in_=container, x=0, y=0, relwidth=1, relheight=1)
Mfm02.place(in_=container, x=0, y=0, relwidth=1, relheight=1)
Mfm03.place(in_=container, x=0, y=0, relwidth=1, relheight=1)

Nfn01_Mfm01SelectRadio = NfnRadios(
    Nfn01, text="Manual", width=11,
    variable=MfmSelection, value="Mfm01", command=Mfm01.lift)
Nfn01_Mfm02SelectRadio = NfnRadios(
    Nfn01, text="Automatic", width=11,
    variable=MfmSelection, value="Mfm02", command=Mfm02.lift)
Nfn01_Mfm03SelectRadio = NfnRadios(
    Nfn01, text="Script", width=11,
    variable=MfmSelection, value="Mfm03", command=Mfm03.lift)
Nfn01_Mfm01SelectRadio.select()

Mfm01.show()

exitButton = Button(root, text="Exit", font=myFont, height=2, width=6)
exitButton.bind('<Button-1>', exitProgram)
exitButton.pack(side=BOTTOM)

# testButton = Button(root, text="Test", font=myFont, height=2, width=6)
# testButton.bind('<Button-1>', testAnythingHere)
# testButton.pack(side=BOTTOM)


# functions to execute after windows is loaded
Script_read()


Auto_refreshWidgets()
Script_refreshWidgets()

root.mainloop()
