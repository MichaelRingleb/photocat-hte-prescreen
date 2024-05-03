from pyrolib import PyroDevice


def measure_firesting(port: str) -> dict:
    firesting = PyroDevice(port)
    result = firesting.measure()
    all_results = {}
    for channel, data in result.items():
        for k, v in data.items():
            all_results[k + "_" + str(channel)] = v
    return all_results
