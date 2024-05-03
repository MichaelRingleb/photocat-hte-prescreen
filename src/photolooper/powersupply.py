from rd6006 import RD6006


def change_power(port: str, voltage: float, current: float):
    ps = RD6006(port)
    ps.voltage = voltage
    ps.current = current
    ps.enable()


def switch_on(port: str, voltage: float = 0.18):
    return change_power(port, 5, voltage)


def switch_off(port: str):
    return change_power(port, 0, 0)
