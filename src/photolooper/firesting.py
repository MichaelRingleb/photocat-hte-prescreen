from pyrolib import PyroDevice


def measure_firesting(port: str) -> dict:
    """
    Measures the firesting on the specified port.

    Args:
        port (str): The port to which the firesting is connected.
        For example: "/dev/ttyUSB0" or "COM3"

    Returns:
        dict: A dictionary containing the measured values.
    """
    firesting = PyroDevice(port)
    result = firesting.measure()
    all_results = {}
    for channel, data in result.items():
        for k, v in data.items():
            all_results[k + "_" + str(channel)] = v
    return all_results
