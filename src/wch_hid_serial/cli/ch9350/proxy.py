"""ch9350-proxy: forward frames from the lower CH9350L to the upper one."""

import argparse

from ...ch9350.device import iter_lower_frames, open_port, read_response
from ...ch9350.protocol import CMD_STATUS, NO_RESPONSE_COMMANDS, to_hex


def main(argv=None):
    ap = argparse.ArgumentParser(description="USB HID Serial Keycode Proxy for CH9350L")
    ap.add_argument("upper_serial", help="Serial port for upper CH9350L, e.g. COM1,115200")
    ap.add_argument("lower_serial", help="Serial port for lower CH9350L, e.g. COM2,115200")
    args = ap.parse_args(argv)

    upport = open_port(args.upper_serial)
    lowport = open_port(args.lower_serial)

    for frame in iter_lower_frames(lowport):
        cmd = frame[2]
        if cmd == CMD_STATUS:
            # Status request/response: forward and relay the upper's reply.
            upport.write(frame)
            lowport.write(read_response(upport))
            continue
        print("L> " + to_hex(frame))
        upport.write(frame)
        print("U< " + to_hex(frame))
        if cmd not in NO_RESPONSE_COMMANDS and cmd not in (0x83, 0x88):
            upreturn = read_response(upport)
            print("U> " + to_hex(upreturn))
            lowport.write(upreturn)
            print("L< " + to_hex(upreturn))


if __name__ == "__main__":
    main()
