"""CH9328 serial device: send keystrokes to a CH9328.

The CH9328's working mode is selected by hardware pins, not by software, so
use the methods that match the pin-selected mode:

- Mode 3 (raw HID reports): :meth:`Ch9328.send_report` / :meth:`Ch9328.type_text`
- Modes 0-2 (ASCII passthrough): :meth:`Ch9328.send_ascii`

Datasheet: https://wch-ic.com/downloads/CH9328DS1_PDF.html
"""

import time

from ..hid import RELEASE_REPORT, iter_text_reports, keyboard_report
from ..serialio import open_port

__all__ = ["open_port", "Ch9328"]


class Ch9328:
    """Send data to a CH9328 over a serial port (``serial.Serial``)."""

    def __init__(self, port):
        self.port = port

    # --- mode 3: raw 8-byte HID reports -----------------------------------
    def send_report(self, modifier=0, keycodes=()):
        """Send one raw 8-byte HID keyboard report (mode 3)."""
        self.port.write(keyboard_report(modifier, keycodes))

    def release_keys(self):
        """Send an all-zero HID report to release every key (mode 3)."""
        self.port.write(RELEASE_REPORT)

    def type_text(self, text, wait=0.0):
        """Type ``text`` as raw HID reports (press+release per char, mode 3).

        ``wait`` is an optional delay in seconds after each report.
        """
        for report in iter_text_reports(text):
            self.port.write(report)
            if wait:
                time.sleep(wait)

    # --- modes 0-2: ASCII passthrough -------------------------------------
    def send_ascii(self, text):
        """Send ``text`` as ASCII bytes for CH9328 modes 0-2.

        The chip itself converts the ASCII to keystrokes, so this just writes
        the bytes. Raises ``UnicodeEncodeError`` for non-ASCII characters.
        """
        self.port.write(text.encode("ascii"))
