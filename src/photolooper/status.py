import enum
import os
from pathlib import Path
from typing import Union


class Command(enum.Enum):
    firesting_start = "FIRESTING-START"
    firesting_stop = "FIRESTING-STOP"
    measure = "MEASURE"
    lamp_on = "LAMP-ON"
    lamp_off = "LAMP-OFF"
    other = "OTHER"
    firesting_end = "FIRESTING-END"
    pause = "PAUSE"


class Status(enum.Enum):
    degassing = "DEGASSING"
    prereaction_baseline = "PREREACTION-BASELINE"
    reaction = "REACTION"
    postreaction_baseline = "POSTREACTION-BASELINE"
    other = "OTHER"


def obtain_status(working_directory: Union[str, Path] = "."):
    """
    Obtain the status of the photolooper. This file is written by the
    AutoSuite program.

    Args:
        working_directory (Union[str, Path], optional):
            The working directory. Defaults to ".".

    Returns:
        Status: The status of the photolooper.
    """
    with open(os.path.join(working_directory, "firesting_status.csv"), "r") as handle:
        content = handle.read()

    if "DEGASSING_END" in content:
        return Status.reaction

    if "DEGASSING" in content:
        return Status.degassing

    if "PREREACTION-BASELINE" in content:
        return Status.prereaction_baseline

    if "POSTREACTION-BASELINE" in content:
        return Status.postreaction_baseline

    if "REACTION" in content:
        return Status.reaction

    return Status.other


def obtain_command(working_directory: Union[str, Path] = "."):
    """
    Obtain the command of the photolooper. This file is written by the
    AutoSuite program.

    Args:
        working_directory (Union[str, Path], optional):
            The working directory. Defaults to ".".

    Returns:
        Command: The command of the photolooper.
    """
    with open(os.path.join(working_directory, "command.csv"), "r") as handle:
        content = handle.read()

    if "FIRESTING-START" in content:
        return Command.firesting_start

    if "FIRESTING-STOP" in content:
        return Command.firesting_stop

    if "MEASURE" in content:
        return Command.measure

    if "LAMP-ON" in content:
        return Command.lamp_on

    if "LAMP-OFF" in content:
        return Command.lamp_off

    if "FIRESTING-END" in content:
        return Command.firesting_end

    if "PAUSE" in content:
        return Command.pause

    return Command.other
