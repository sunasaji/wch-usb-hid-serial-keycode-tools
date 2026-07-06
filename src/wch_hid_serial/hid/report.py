"""Standard 8-byte USB HID keyboard report and text-to-report helpers.

The report ``[modifier, 0x00, key1..key6]`` is the raw HID keyboard report
used both by the CH9328 (sent as-is in mode 3) and by the CH9329 (wrapped in
a command packet), so it lives in the shared HID layer.
"""

from .keycodes import MOD_LEFT_SHIFT, ascii_to_keycode, modifier_bit

_SHIFT = modifier_bit(MOD_LEFT_SHIFT)  # left-shift bit of the modifier byte (0x02)


def keyboard_report(modifier=0, keycodes=()):
    """Build an 8-byte HID keyboard report: ``[modifier, 0x00, key1..key6]``.

    Up to 6 keycodes are used; the report is zero-padded to 6 key slots.
    """
    keys = list(keycodes)[:6]
    keys += [0] * (6 - len(keys))
    return bytes([modifier & 0xff, 0x00] + keys)


#: An all-zero keyboard report that releases every key.
RELEASE_REPORT = keyboard_report()


def iter_text_reports(text):
    """Yield 8-byte HID keyboard reports that type ``text``.

    Each character yields a press report followed by a release report.
    Characters with no keycode (unmapped or non-ASCII) are skipped.
    """
    for ch in text:
        mapping = ascii_to_keycode(ch)
        if mapping is None:
            continue
        shift, keycode = mapping
        modifier = _SHIFT if shift else 0
        yield keyboard_report(modifier, [keycode])  # press
        yield RELEASE_REPORT                          # release
