"""ch9329-keysender: read text from stdin and type it via a CH9329."""

import argparse
import sys
import time

from ...ch9329.device import open_port
from ...ch9329.keyboard import iter_text_packets
from ...ch9329.protocol import to_hex


def _stdin_chars():
    while True:
        c = sys.stdin.read(1)
        if not c:  # EOF
            return
        yield c


def main(argv=None):
    ap = argparse.ArgumentParser(
        description="Type text from stdin as USB HID keystrokes via a CH9329"
    )
    ap.add_argument("serial", help="Serial port for the CH9329, e.g. COM1,9600")
    ap.add_argument(
        "--wait-ms",
        type=float,
        default=0.0,
        help="Optional delay in milliseconds after each report (default: 0)",
    )
    ap.add_argument(
        "--quiet", action="store_true", help="Do not print sent packets"
    )
    args = ap.parse_args(argv)

    wait = args.wait_ms / 1000.0
    port = open_port(args.serial)
    for packet in iter_text_packets(_stdin_chars()):
        port.write(packet)
        if not args.quiet:
            print(to_hex(packet))
        if wait:
            time.sleep(wait)


if __name__ == "__main__":
    main()
