import enum
import time
from powersupply import switch_off, switch_on
from firesting import measure_firesting
import pandas as pd
from pathlib import Path
from typing import Union
import os


class Command(enum.Enum):
    firesting_start = "FIRESTING-START"
    firesting_stop = "FIRESTING-STOP"
    measure = "MEASURE"
    lamp_on = "LAMP-ON"
    lamp_off = "LAMP-OFF"


class Status(enum.Enum):
    degassing = "DEGASSING"
    prereaction_baseline = "PREREACTION-BASELINE"
    reaction = "REACTION"
    postreaction_baseline = "POSTREACTION-BASELINE"


def obtain_status(working_directory: Union[str, Path] = "."):
    with open(os.path.join(working_directory, "status.csv"), "r") as handle:
        content = handle.read()

    if "DEGASSING" in content:
        return Status.degassing

    if "PREREACTION-BASELINE" in content:
        return Status.prereaction_baseline

    if "REACTION" in content:
        return Status.reaction

    if "POSTREACTION-BASELINE" in content:
        return Status.postreaction_baseline


def obtain_command(working_directory: Union[str, Path] = "."):
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

    return None


def seed_status_and_command_files(working_directory: Union[str, Path] = "."):
    with open(os.path.join(working_directory, "status.csv"), "w") as handle:
        handle.write("Start")

    with open(os.path.join(working_directory, "command.csv"), "w") as handle:
        handle.write("FIRESTING-STOP")


firesting_port = "/dev/tty.usbserial-DA68UH8B"
lamp_port = "COM4"
sleep_time = 1
working_directory = Path(__file__).parent


def main():
    results = []
    switch_off(lamp_port)
    while True:
        command = obtain_command(working_directory=working_directory)
        status = obtain_status(working_directory=working_directory)

        if command == Command.lamp_off:
            switch_off(lamp_port)

        if command == Command.lamp_on:
            switch_on(lamp_port)

        if command == Command.firesting_start:
            firesting_results = measure_firesting(firesting_port)
        else:
            firesting_results = {}

        firesting_results["timestamp"] = time.time()
        firesting_results["status"] = status.value
        firesting_results["command"] = command.value
        results.append(firesting_results)

        df = pd.DataFrame(results)
        df.to_csv("results.csv", index=False)

        time.sleep(sleep_time)


if __name__ == "__main__":
    main()
