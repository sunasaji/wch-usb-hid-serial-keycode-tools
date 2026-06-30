"""CH9350L key sending: turn text into HID report frames.

In working status 2 ("short command") the host sends 11-byte reports
``57 ab 01 <modifier> 00 <keycode> 00 00 00 00 00`` to the upper CH9350L.
:func:`iter_key_reports` is pure (no serial I/O, no sleeping) so it is easy
to test; the CLI handles the port, inter-report delay and output.
"""

from ..hid.keycodes import MOD_LEFT_SHIFT, ascii_to_keycode, modifier_bit

# Frame constants (short command, working status 2).
EMPTY_REPORT = bytes([0x57, 0xab, 0x01, 0, 0, 0, 0, 0, 0, 0, 0])
NEWLINE_REPORT = bytes([0x57, 0xab, 0x01, 0, 0, 0x28, 0, 0, 0, 0, 0])
RESET_STATUS = bytes([0x57, 0xab, 0x40, 0x00])  # change working status to 0
SET_STATUS_2 = bytes([0x57, 0xab, 0x85, 0x02])  # change working status to 2

_SHIFT_MODIFIER = modifier_bit(MOD_LEFT_SHIFT)  # 0x02

#: Input byte that means "stop" (Ctrl-C / ETX) when read from stdin.
ETX = 3


def _key_report(shift, keycode):
    modifier = _SHIFT_MODIFIER if shift else 0
    return bytes([0x57, 0xab, 0x01, modifier, 0, keycode, 0, 0, 0, 0, 0])


def iter_key_reports(text):
    """Yield ``(frame, is_char)`` report frames for ``text``.

    ``is_char`` is True only for actual character key reports (so the CLI can
    number/print those and stay quiet about inserted empty/newline reports).

    To make two consecutive identical keys register separately, an empty
    report is inserted between them. Unmapped characters (no keycode) are
    skipped. A Ctrl-C (ETX, byte value 3) stops the iteration.
    """
    prev_keycode = None
    for ch in text:
        if ch == "\n":
            yield NEWLINE_REPORT, False
            yield EMPTY_REPORT, False
            continue
        if ord(ch) == ETX:
            return
        mapping = ascii_to_keycode(ch)
        if mapping is None:
            continue
        shift, keycode = mapping
        if keycode == prev_keycode:
            yield EMPTY_REPORT, False
        prev_keycode = keycode
        yield _key_report(shift, keycode), True
