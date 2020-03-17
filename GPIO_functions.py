import RPi.GPIO as GPIO
from classes import EPB_status as EPB_status, SB_status as SB_status


GPIO.setwarnings(False)

outputChannels = {
    "EPB_plus": 40,
    "EPB_Minus": 38,
    "SB": 36
}

chan_list = list(outputChannels.values())

GPIO.setmode(GPIO.BOARD)
GPIO.setup(chan_list, GPIO.OUT)
GPIO.output(chan_list, GPIO.LOW)


def outputChange(EPB_cmd=None, SB_cmd=None, EPB_cur=EPB_status.EPB_off, SB_cur=SB_status.SB_release):

    global EPB_status, SB_status

    # check the final state first
    if EPB_cmd is None:
        EPB_cmd_final = EPB_cur
    else:
        EPB_cmd_final = EPB_cmd

    if SB_cmd is None:
        SB_cmd_final = SB_cur
    else:
        SB_cmd_final = SB_cmd

    # Assign the GPIO state for each port
    if EPB_cmd_final == EPB_status.EPB_apply:
        EPB_plusRelay = GPIO.HIGH
        EPB_minusRelay = GPIO.LOW
    elif EPB_cmd_final == EPB_status.EPB_release:
        EPB_plusRelay = GPIO.LOW
        EPB_minusRelay = GPIO.HIGH
    elif EPB_cmd_final == EPB_status.EPB_off:
        EPB_plusRelay = GPIO.LOW
        EPB_minusRelay = GPIO.LOW

    if SB_cmd_final == SB_status.SB_apply:
        SB_relay = GPIO.HIGH
    elif SB_cmd_final == SB_status.SB_release:
        SB_relay = GPIO.LOW

    # GPIO change execution
    GPIO.output(
        (outputChannels["EPB_plus"], outputChannels["EPB_Minus"], outputChannels["SB"]),
        (EPB_plusRelay, EPB_minusRelay, SB_relay))


def cleanup():
    GPIO.cleanup()
    print("GPIO.cleanup() executed!")
