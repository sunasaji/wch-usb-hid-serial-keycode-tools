"""CH9329 keyboard: wrap HID keyboard reports in CH9329 command packets.

The CH9329 emulates a USB keyboard, so a keypress needs an explicit press
report followed by a release report. The 8-byte HID report itself comes from
the shared :mod:`wch_hid_serial.hid` layer; here it is wrapped in a CH9329
"keyboard general data" command packet. These functions are pure (no serial
I/O); the device layer and CLI handle the port and any inter-report delay.
"""

from ..hid import iter_text_reports, keyboard_report
from .protocol import CMD_SEND_KB_GENERAL, build_packet


def general_report(modifier=0, keycodes=()):
    """Build the 8-byte keyboard general-data payload (the HID report)."""
    return keyboard_report(modifier, keycodes)


def general_packet(modifier=0, keycodes=()):
    """Build a full CH9329 keyboard general-data command packet."""
    return build_packet(CMD_SEND_KB_GENERAL, general_report(modifier, keycodes))


#: Packet that releases all keys (an all-zero keyboard report).
RELEASE_PACKET = general_packet()


def iter_text_packets(text):
    """Yield CH9329 packets that type ``text`` (press + release per char)."""
    for report in iter_text_reports(text):
        yield build_packet(CMD_SEND_KB_GENERAL, report)
