"""CH9328 support: UART-to-USB-HID keyboard (keyboard only, no mouse).

The CH9328 is a simpler WCH chip than the CH9329: it has no command framing
or checksum, and its working mode is chosen by hardware pins (not by
software):

- Modes 0-2: send plain ASCII text; the chip converts it to keystrokes.
- Mode 3: send raw 8-byte HID keyboard reports (transparent transmission).

Datasheet: https://wch-ic.com/downloads/CH9328DS1_PDF.html
"""

from ..hid import keyboard_report, iter_text_reports, RELEASE_REPORT
from .device import open_port, Ch9328

__all__ = [
    "keyboard_report",
    "iter_text_reports",
    "RELEASE_REPORT",
    "open_port",
    "Ch9328",
]
