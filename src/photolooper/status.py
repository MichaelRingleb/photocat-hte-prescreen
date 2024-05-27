import enum


class Command(enum.Enum):
    firesting_start = "FIRESTING-START"
    firesting_stop = "FIRESTING-STOP"
    measure = "MEASURE"
    lamp_on = "LAMP-ON"
    lamp_off = "LAMP-OFF"
    other = "OTHER"


class Status(enum.Enum):
    degassing = "DEGASSING"
    prereaction_baseline = "PREREACTION-BASELINE"
    reaction = "REACTION"
    postreaction_baseline = "POSTREACTION-BASELINE"
    other = "OTHER"
