import time
from photolooper.powersupply import switch_off, switch_on
from photolooper.firesting import measure_firesting
from photolooper.utils import find_com_port
import pandas as pd
from pathlib import Path
from typing import Union
import os
import yaml
from photolooper.status import Command, Status
import warnings

warnings.filterwarnings(
    "ignore", message="*baud-rate*"
)  # this is one log too much in the PyroScience codebase


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

    # write instruction CSV with some numbers, but set the run to "false"
    config = {
        "run": "false",
        "volume_water": 10,
        "volume_sacrificial_oxidant": 10,
        "volume_ruthenium_solution": 10,
        "volume_buffer_solution_1": 10,
        "volume_buffer_solution_2": 10,
        "degassing_time": 10,
        "measurement_time": 10,
    }

    write_instruction_csv(config, working_directory)


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


def main(global_config_path, experiment_config_path):
    global_configs = read_yaml(global_config_path)
    global_configs["chemspeed_working_dir"] = os.path.normpath(
        global_configs["chemspeed_working_dir"]
    )
    global_configs["instruction_dir"] = os.path.normpath(
        global_configs["instruction_dir"]
    )
    configs = read_yaml(experiment_config_path)

    firestring_port = find_com_port(global_configs["firesting_port"]["name"])
    if firestring_port is None:
        raise Exception("💣 Firesting port not found")

    global_configs["firesting_port"]["port"] = firestring_port

    lamp_port = find_com_port(global_configs["lamp_port"]["name"])
    if lamp_port is None:
        raise Exception("💣 Lamp port not found")

    global_configs["lamp_port"]["port"] = lamp_port

    switch_off(global_configs["lamp_port"]["port"])
    seed_status_and_command_files(global_configs["instruction_dir"])
    for config in configs:
        print("🧪 Working on ", config)

        # if the results file already exists, warn user and add incrementing number to run name
        if os.path.exists(
            os.path.join(
                global_configs["instruction_dir"], f"results_{config['run']}.csv"
            )
        ):
            print(
                f"🚧 Results file for {config['run']} already exists. Adding number to run name"
            )
            config["run"] = config["run"] + str(
                len(os.listdir(global_configs["instruction_dir"])) + 1
            )

        write_instruction_csv(config, global_configs["instruction_dir"])
        results = []
        switch_off(global_configs["lamp_port"]["port"])
        while True and config["run"] == "true":
            command = obtain_command(
                working_directory=global_configs["chemspeed_working_dir"]
            )
            status = obtain_status(
                working_directory=global_configs["chemspeed_working_dir"]
            )

            if command == Command.firesting_end:
                break

            if command == Command.lamp_off:
                switch_off(global_configs["lamp_port"]["port"])

            if command == Command.lamp_on:
                switch_on(global_configs["lamp_port"]["port"], config["voltage"])

            if command != Command.firesting_stop:
                firesting_results = measure_firesting(
                    global_configs["firesting_port"]["port"]
                )
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
            firesting_results["datetime"] = time.strftime("%Y-%m-%d %H:%M:%S")
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

            df[["datetime", "uM_1", "optical_temperature_2", "status"]].to_csv(
                os.path.join(
                    global_configs["instruction_dir"],
                    f"results_summarized_{config['run']}.csv",
                ),
                index=False,
            )

            time.sleep(global_configs["sleep_time"])
