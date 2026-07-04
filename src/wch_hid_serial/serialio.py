"""Shared serial-port helpers used by the chip backends."""

import serial


def open_port(spec):
    """Open a serial port from a ``"name[,baudrate]"`` spec.

    Example: ``open_port("COM1,115200")`` or ``open_port("/dev/ttyUSB0")``.
    If the baud rate is omitted, pyserial's default (9600) is used.
    """
    parts = spec.split(",")
    kwargs = {}
    if len(parts) > 1 and parts[1]:
        kwargs["baudrate"] = int(parts[1])
    return serial.Serial(parts[0], **kwargs)
