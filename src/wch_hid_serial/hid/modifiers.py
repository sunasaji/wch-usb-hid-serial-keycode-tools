"""USB HID keyboard modifier-byte bit flags and name lookup.

These are the bits of the modifier byte in a HID keyboard report (distinct
from the modifier *keycodes* 0xe0..0xe7 in :mod:`keycodes`; use
:func:`keycodes.modifier_bit` to convert a keycode to its bit).
"""

MOD_NONE = 0x00
MOD_LCTRL = 0x01
MOD_LSHIFT = 0x02
MOD_LALT = 0x04
MOD_LGUI = 0x08
MOD_RCTRL = 0x10
MOD_RSHIFT = 0x20
MOD_RALT = 0x40
MOD_RGUI = 0x80
# "GUI" is also called the Windows key.
MOD_LWIN = MOD_LGUI
MOD_RWIN = MOD_RGUI

_NAME_TO_BIT = {
    "ctrl": MOD_LCTRL, "control": MOD_LCTRL, "lctrl": MOD_LCTRL,
    "shift": MOD_LSHIFT, "lshift": MOD_LSHIFT,
    "alt": MOD_LALT, "lalt": MOD_LALT, "option": MOD_LALT,
    "win": MOD_LGUI, "lwin": MOD_LGUI, "gui": MOD_LGUI,
    "super": MOD_LGUI, "meta": MOD_LGUI, "cmd": MOD_LGUI, "command": MOD_LGUI,
    "rctrl": MOD_RCTRL, "rshift": MOD_RSHIFT,
    "ralt": MOD_RALT, "altgr": MOD_RALT, "rwin": MOD_RGUI, "rgui": MOD_RGUI,
}


def modifier_name_to_bit(name):
    """Return the modifier-byte bit for a modifier name (e.g. ``"ctrl"``)."""
    try:
        return _NAME_TO_BIT[name.lower()]
    except KeyError:
        raise ValueError("unknown modifier name: %r" % (name,)) from None


def modifiers_to_byte(names):
    """Combine an iterable of modifier names into a single modifier byte."""
    byte = 0
    for name in names:
        byte |= modifier_name_to_bit(name)
    return byte


def parse_modifiers(spec):
    """Parse a modifier spec into a modifier byte.

    Accepts ``"none"``, a single name (``"shift"``), a ``"+"``-joined combo
    (``"shift+ralt"``), or an iterable of names/ints.
    """
    if isinstance(spec, str):
        if spec.strip().lower() == "none":
            return 0
        parts = spec.split("+")
    else:
        parts = spec
    byte = 0
    for part in parts:
        byte |= part if isinstance(part, int) else modifier_name_to_bit(part)
    return byte
