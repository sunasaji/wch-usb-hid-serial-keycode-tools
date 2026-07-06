"""ch9328-keysender: read text from stdin and type it via a CH9328.

Pick ``--mode`` to match the CH9328's pin-selected working mode:
``hid`` sends raw 8-byte HID reports (mode 3), ``ascii`` sends the text as-is
(modes 0-2, where the chip converts ASCII to keystrokes).
"""

import argparse
import sys
import time

from ...ch9328.device import open_port
from ...hid import iter_text_reports


def _stdin_chars():
    while True:
        c = sys.stdin.read(1)
        if not c:  # EOF
            return
        yield c


def main(argv=None):
    ap = argparse.ArgumentParser(
        description="Type text from stdin as USB HID keystrokes via a CH9328"
    )
    ap.add_argument("serial", help="Serial port for the CH9328, e.g. COM1,9600")
    ap.add_argument(
        "--mode",
        choices=["hid", "ascii"],
        default="hid",
        help="hid: raw 8-byte HID reports (chip mode 3); "
        "ascii: send text as-is (chip modes 0-2). (default: hid)",
    )
    ap.add_argument(
        "--wait-ms",
        type=float,
        default=0.0,
        help="hid mode: optional delay in milliseconds after each report",
    )
    ap.add_argument("--quiet", action="store_true", help="do not print sent reports")
    args = ap.parse_args(argv)

    port = open_port(args.serial)
    if args.mode == "ascii":
        # The chip converts ASCII to keystrokes; just pass the bytes through.
        port.write(sys.stdin.read().encode("ascii", errors="ignore"))
        return

    wait = args.wait_ms / 1000.0
    for report in iter_text_reports(_stdin_chars()):
        port.write(report)
        if not args.quiet:
            print(report.hex(" "))
        if wait:
            time.sleep(wait)


if __name__ == "__main__":
    main()
