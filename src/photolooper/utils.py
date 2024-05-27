import sys
import glob
import serial


def serial_ports():
    """Lists serial port names

    Raises:
        EnvironmentError: Unsupported platform

    Returns:
        list: List of serial ports
    """
    if sys.platform.startswith("win"):
        ports = ["COM%s" % (i + 1) for i in range(256)]
    elif sys.platform.startswith("linux") or sys.platform.startswith("cygwin"):
        # this excludes your current terminal "/dev/tty"
        ports = glob.glob("/dev/tty[A-Za-z]*")
    elif sys.platform.startswith("darwin"):
        ports = glob.glob("/dev/tty.*")
    else:
        raise EnvironmentError("Unsupported platform")

    result = []
    for port in ports:
        try:
            s = serial.Serial(port)
            s.close()
            result.append(port)
        except (OSError, serial.SerialException):
            pass
    return result


def check_com_port(port: str) -> bool:
    return port in serial_ports()


if __name__ == "__main__":
    print(serial_ports())
