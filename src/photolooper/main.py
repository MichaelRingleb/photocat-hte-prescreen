import time
from photolooper.powersupply import switch_off, switch_on
from photolooper.firesting import measure_firesting
from photolooper.utils import check_com_port
import pandas as pd
from pathlib import Path
from typing import Union
import os
import yaml
from photolooper.status import Command, Status

# import termplotlib as tpl


def obtain_status(working_directory: Union[str, Path] = "."):
    with open(os.path.join(working_directory, "firesting_status.csv"), "r") as handle:
        content = handle.read()

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

    return Command.other


def seed_status_and_command_files(working_directory: Union[str, Path] = "."):
    with open(os.path.join(working_directory, "firesting_status.csv"), "w") as handle:
        handle.write("Start")

    with open(os.path.join(working_directory, "command.csv"), "w") as handle:
        handle.write("FIRESTING-STOP")


def read_yaml(yaml_file: Union[str, Path]) -> list:
    with open(yaml_file, "r") as handle:
        return yaml.safe_load(handle)


def write_instruction_csv(config: dict, instruction_dir: Union[str, Path] = "."):
    column_order = [
        "run",
        "volume_water",
        "volume_sacrificial_oxidant",
        "volume_ruthenium_solution",
        "volume_buffer_solution_1",
        "volume_buffer_solution_2",
        "degassing_time",
        "measurement_time",
    ]
    df = pd.DataFrame([config])
    df = df[column_order]
    df.to_csv(
        os.path.join(instruction_dir, "values_for_experiment.csv"), index=False, sep=","
    )


def main(config_dir: Union[str, Path] = "."):
    global_configs = read_yaml(os.path.join(config_dir, "setup.yml"))
    global_configs["chemspeed_working_dir"] = os.path.normpath(
        global_configs["chemspeed_working_dir"]
    )
    global_configs["instruction_dir"] = os.path.normpath(
        global_configs["instruction_dir"]
    )
    configs = read_yaml(os.path.join(config_dir, "experiments.yml"))

    if not check_com_port(
        global_configs["firesting_port"].port, global_configs["firesting_port"].name
    ):
        raise Exception("Firesting port not found")

    if not check_com_port(
        global_configs["lamp_port"].port, global_configs["lamp_port"].name
    ):
        raise Exception("Lamp port not found")

    switch_off(global_configs["lamp_port"])
    seed_status_and_command_files(global_configs["instruction_dir"])
    for config in configs:
        print("Working on ", config)
        write_instruction_csv(config, global_configs["instruction_dir"])
        results = []
        switch_off(global_configs["lamp_port"])
        while True:
            command = obtain_command(
                working_directory=global_configs["chemspeed_working_dir"]
            )
            status = obtain_status(
                working_directory=global_configs["chemspeed_working_dir"]
            )

            if command == Command.firesting_end:
                break

            if command == Command.lamp_off:
                switch_off(global_configs["lamp_port"])

            if command == Command.lamp_on:
                switch_on(global_configs["lamp_port"], config["voltage"])

            if command != Command.firesting_stop:
                firesting_results = measure_firesting(global_configs["firesting_port"])
                print(
                    f"uO2: {firesting_results['uM_1']} optical temperature: {firesting_results['optical_temperature_2']}"
                )
                # fig = tpl.figure()
                # fig.plot(
                #     firesting_results["uM_1"],
                #     firesting_results["optical_temperature_2"],
                # )
                # fig.show()

            else:
                firesting_results = {}

            firesting_results["timestamp"] = time.time()
            firesting_results["status"] = status.value
            firesting_results["command"] = command.value
            results.append(firesting_results)

            df = pd.DataFrame(results)
            df.to_csv(
                os.path.join(
                    global_configs["log_dir"], f"results_{config['name']}.csv"
                ),
                index=False,
            )

            time.sleep(global_configs["sleep_time"])
