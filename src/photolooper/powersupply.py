from rd6006 import RD6006


def change_power(port: str, voltage: float):
    ps = RD6006(port)
    ps.voltage = voltage
    ps.enable


def switch_on(port: str, voltage: float = 0.18):
    return change_power(port, voltage)


def switch_off(port: str):
    """
    Switches off the power supply connected to the specified port.

    Args:
        port (str): The port to which the power supply is connected.

    Returns:
        None
    """
    # Switch the power supply off by setting the voltage to 0
    change_power(port, 0)
