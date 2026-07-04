"""CH9329 keyboard: build keyboard reports and type text.

The CH9329 emulates a USB keyboard, so a keypress needs an explicit press
report followed by a release report. These functions are pure (no serial
I/O); the device layer and CLI handle the port and any inter-report delay.
"""

from ..hid.keycodes import MOD_LEFT_SHIFT, ascii_to_keycode, modifier_bit
from .protocol import CMD_SEND_KB_GENERAL, build_packet

_SHIFT = modifier_bit(MOD_LEFT_SHIFT)  # 0x02


def general_report(modifier=0, keycodes=()):
    """Build the 8-byte keyboard general-data payload.

    ``modifier`` is the modifier byte, ``keycodes`` is up to 6 HID keycodes.
    """
    keys = list(keycodes)[:6]
    keys += [0] * (6 - len(keys))
    return bytes([modifier & 0xff, 0x00] + keys)


def general_packet(modifier=0, keycodes=()):
    """Build a full CH9329 keyboard general-data command packet."""
    return build_packet(CMD_SEND_KB_GENERAL, general_report(modifier, keycodes))


#: Packet that releases all keys (an all-zero keyboard report).
RELEASE_PACKET = general_packet()


def iter_text_packets(text):
    """Yield CH9329 packets that type ``text`` (press + release per char).

    Characters with no keycode (unmapped or non-ASCII) are skipped. Newline
    is handled like any other character (HID keycode 0x28).
    """
    for ch in text:
        mapping = ascii_to_keycode(ch)
        if mapping is None:
            continue
        shift, keycode = mapping
        modifier = _SHIFT if shift else 0
        yield general_packet(modifier, [keycode])  # press
        yield RELEASE_PACKET                        # release
