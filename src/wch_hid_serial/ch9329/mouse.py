"""CH9329 mouse: build relative and absolute mouse command packets.

All functions are pure (no serial I/O). Button values are a bitmask
(bit0 left, bit1 right, bit2 middle).
"""

from .protocol import CMD_SEND_MS_ABS, CMD_SEND_MS_REL, build_packet

# Mouse button bitmask.
BUTTON_LEFT = 0x01
BUTTON_RIGHT = 0x02
BUTTON_MIDDLE = 0x04

#: CH9329 absolute-coordinate resolution (12-bit: 0..4095).
ABS_RANGE = 4096

_BUTTON_NAMES = {"left": BUTTON_LEFT, "right": BUTTON_RIGHT, "middle": BUTTON_MIDDLE}


def button_mask(button):
    """Return a button bitmask from an int mask or a name (left/right/middle)."""
    if isinstance(button, int):
        return button & 0xff
    try:
        return _BUTTON_NAMES[button.lower()]
    except KeyError:
        raise ValueError("unknown mouse button: %r" % (button,)) from None


def scale_abs(px, py, screen_width, screen_height):
    """Map screen pixel coordinates to CH9329 absolute coordinates (0..4095)."""
    x = (ABS_RANGE * px) // screen_width if screen_width else 0
    y = (ABS_RANGE * py) // screen_height if screen_height else 0
    return min(0x0fff, max(0, x)), min(0x0fff, max(0, y))


def _clamp_i8(v):
    return max(-128, min(127, int(v))) & 0xff


def relative_packet(x=0, y=0, buttons=0, wheel=0):
    """Build a relative-mouse packet.

    ``x``/``y``/``wheel`` are signed 8-bit movements (clamped to -128..127).
    Positive ``x`` moves right; positive ``y`` moves down (USB HID
    convention).
    """
    data = bytes([0x01, buttons & 0xff, _clamp_i8(x), _clamp_i8(y), _clamp_i8(wheel)])
    return build_packet(CMD_SEND_MS_REL, data)


def absolute_packet(x, y, buttons=0, wheel=0):
    """Build an absolute-mouse packet.

    ``x``/``y`` are 0..4095 device coordinates (0,0 = top-left). Callers that
    work in screen pixels should scale first: ``x = 4096 * px // screen_w``.
    """
    x &= 0x0fff
    y &= 0x0fff
    data = bytes([0x02, buttons & 0xff,
                  x & 0xff, (x >> 8) & 0xff,
                  y & 0xff, (y >> 8) & 0xff,
                  _clamp_i8(wheel)])
    return build_packet(CMD_SEND_MS_ABS, data)
