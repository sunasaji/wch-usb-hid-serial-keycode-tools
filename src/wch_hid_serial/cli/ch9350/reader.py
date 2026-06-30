"""ch9350-reader: read serial data from the lower CH9350L and print frames."""

import argparse

from ...ch9350.device import iter_lower_frames, open_port
from ...ch9350.protocol import CMD_STATUS, to_hex


def main(argv=None):
    ap = argparse.ArgumentParser(description="USB HID Serial Keycode Reader for CH9350L")
    ap.add_argument("lower_serial", help="Serial port for lower CH9350L, e.g. COM1,115200")
    args = ap.parse_args(argv)

    port = open_port(args.lower_serial)
    for frame in iter_lower_frames(port):
        if frame[2] == CMD_STATUS:
            continue  # suppress status frames (as the original reader did)
        print(to_hex(frame))


if __name__ == "__main__":
    main()
