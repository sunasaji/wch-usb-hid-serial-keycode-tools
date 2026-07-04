"""ch9329-mouse: run a single CH9329 mouse operation from the command line."""

import argparse

from ...ch9329.device import Ch9329, open_port


def _screen(value):
    if value is None:
        return None
    w, h = value.lower().split("x")
    return int(w), int(h)


def main(argv=None):
    ap = argparse.ArgumentParser(description="Send a CH9329 mouse command")
    ap.add_argument("serial", help="Serial port for the CH9329, e.g. COM1,9600")
    sub = ap.add_subparsers(dest="op", required=True)

    p = sub.add_parser("move", help="move the pointer")
    p.add_argument("x", type=int)
    p.add_argument("y", type=int)
    p.add_argument("-r", "--relative", action="store_true", help="relative move")
    p.add_argument("--screen", help="WxH to treat x/y as screen pixels (absolute)")
    p.add_argument("--wheel", type=int, default=0)

    for name, help_text in (("click", "press and release"),
                            ("down", "press and hold"),
                            ("up", "release")):
        q = sub.add_parser(name, help=help_text)
        q.add_argument("-b", "--button", default="left",
                       help="left/right/middle (default: left)")

    s = sub.add_parser("scroll", help="scroll the wheel")
    s.add_argument("amount", type=int, help="positive=up, negative=down")

    d = sub.add_parser("drag", help="press at start, move to end, release")
    for coord in ("x1", "y1", "x2", "y2"):
        d.add_argument(coord, type=int)
    d.add_argument("-b", "--button", default="left")
    d.add_argument("--screen", help="WxH to treat coordinates as screen pixels")

    args = ap.parse_args(argv)
    dev = Ch9329(open_port(args.serial))

    if args.op == "move":
        if args.relative:
            dev.move_mouse(args.x, args.y, wheel=args.wheel)
        else:
            dev.move_absolute(args.x, args.y, screen=_screen(args.screen), wheel=args.wheel)
    elif args.op == "click":
        dev.click(args.button)
    elif args.op == "down":
        dev.mouse_down(args.button)
    elif args.op == "up":
        dev.mouse_up(args.button)
    elif args.op == "scroll":
        dev.scroll(args.amount)
    elif args.op == "drag":
        dev.drag(args.x1, args.y1, args.x2, args.y2,
                 button=args.button, screen=_screen(args.screen))


if __name__ == "__main__":
    main()
