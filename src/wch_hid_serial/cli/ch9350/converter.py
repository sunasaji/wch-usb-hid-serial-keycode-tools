"""ch9350-converter: forward frames from lower to upper CH9350L, converting
some keyboard keycodes via a conversion table."""

import argparse

from ...ch9350.convert import convert_report
from ...ch9350.device import iter_lower_frames, open_port, read_response
from ...ch9350.protocol import (
    CMD_STATUS,
    NO_RESPONSE_COMMANDS,
    is_keyboard_report,
    to_hex,
)


def main(argv=None):
    ap = argparse.ArgumentParser(description="USB HID Serial Keycode Converter for CH9350L")
    ap.add_argument("upper_serial", help="Serial port for upper CH9350L, e.g. COM1,115200")
    ap.add_argument("lower_serial", help="Serial port for lower CH9350L, e.g. COM2,115200")
    args = ap.parse_args(argv)

    upport = open_port(args.upper_serial)
    lowport = open_port(args.lower_serial)

    for frame in iter_lower_frames(lowport):
        cmd = frame[2]
        if cmd == CMD_STATUS:
            upport.write(frame)
            lowport.write(read_response(upport))
            continue
        print("L> " + to_hex(frame))
        if cmd in (0x83, 0x88):
            report_type = frame[4]
            if is_keyboard_report(report_type):
                # frame = HEAD + cmd + len + type + payload + checksum
                payload = frame[5:-1]
                frame = frame[:5] + convert_report(payload)
            upport.write(frame)
            print("U< " + to_hex(frame))
            continue
        upport.write(frame)
        print("U< " + to_hex(frame))
        if cmd not in NO_RESPONSE_COMMANDS:
            upreturn = read_response(upport)
            print("U> " + to_hex(upreturn))
            lowport.write(upreturn)
            print("L< " + to_hex(upreturn))


if __name__ == "__main__":
    main()
