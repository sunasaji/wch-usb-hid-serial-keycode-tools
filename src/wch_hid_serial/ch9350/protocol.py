"""CH9350L serial protocol: frame constants and pure helpers.

A CH9350L frame starts with the two-byte head ``57 ab`` followed by a
command byte. The frames this package handles:

* ``57 ab 82 <status>``                       -- status request/response
* ``57 ab {83|88} <len> <type> <payload...> <checksum>`` -- HID report
* ``57 ab <cmd> ...``                          -- other commands

The HID report payload is ``[connection-info][modifier][reserved]
[keys...][seq-num]`` and ``<len>`` counts the bytes from ``<type>`` to
``<checksum>`` inclusive.
"""

HEAD = bytes([0x57, 0xab])

CMD_STATUS = 0x82
CMD_HID_REPORT = (0x83, 0x88)

# Commands sent to the upper CH9350L that produce no response frame.
NO_RESPONSE_COMMANDS = frozenset({0x81, 0x84, 0x85, 0x86, 0x87, 0x40})


def checksum(data):
    """8-bit sum checksum of ``data`` (bytes)."""
    return sum(data) & 0xff


def is_keyboard_report(report_type):
    """True if a HID report ``report_type`` byte denotes a keyboard report.

    Keyboard report descriptors have a high nibble of 1 (e.g. ``0x12``);
    mouse reports use 2 (e.g. ``0x22``).
    """
    return (report_type >> 4) == 0x1


def to_hex(data):
    """Format bytes as space-separated hex, e.g. ``"57 ab 82 00"``."""
    return data.hex(" ")
