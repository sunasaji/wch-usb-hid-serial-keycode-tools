"""ch9350-keysender: read text from stdin and send keycodes to the upper
CH9350L."""

import argparse
import sys
import time

from ...ch9350.device import open_port
from ...ch9350.keysend import RESET_STATUS, SET_STATUS_2, iter_key_reports
from ...ch9350.protocol import to_hex


def _stdin_chars():
    while True:
        c = sys.stdin.read(1)
        if not c:  # EOF
            return
        yield c


def main(argv=None):
    ap = argparse.ArgumentParser(
        description="USB HID Serial Keycode Sender for CH9350L"
    )
    ap.add_argument("upper_serial", help="Serial port for upper CH9350L, e.g. COM1,115200")
    ap.add_argument(
        "--wait-ms",
        type=float,
        default=8.0,
        help="Delay in milliseconds between HID reports. Too short drops "
        "characters; too long is slow. (default: 8)",
    )
    args = ap.parse_args(argv)

    wait = args.wait_ms / 1000.0
    port = open_port(args.upper_serial)
    # Working Status Change Command 1: switch to status 2 to use short commands.
    port.write(SET_STATUS_2)

    count = 0
    try:
        for frame, is_char in iter_key_reports(_stdin_chars()):
            port.write(frame)
            if is_char:
                print(str(count) + ": " + to_hex(frame))
                count += 1
            time.sleep(wait)
    finally:
        # Reset working status to 0 on EOF, Ctrl-C in the stream, or error.
        port.write(RESET_STATUS)


if __name__ == "__main__":
    main()
