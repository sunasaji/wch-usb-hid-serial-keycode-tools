"""CH9350L keyboard keycode conversion.

The converter rewrites the keys in a CH9350L keyboard report payload
according to a lookup table (input keycode -> output keycode), recomputing
the output modifier byte and checksum. A keycode is a 1-byte USB HID scan
code. Output keycodes in the table may be modifier keys (0xe0..0xe7), a
normal key, or ``0x00`` to drop the input key.

See https://gist.github.com/MightyPork/6da26e382a7ad91b5496ee55fdc73db2
for the keycode list.
"""

from ..hid.keycodes import MODIFIER_BASE, is_modifier, modifier_bit
from .protocol import checksum

# Default conversion table (input keycode -> output keycode):
#   0x39 Caps     -> 0xe0 Left Ctrl
#   0x8a Henkan   -> 0xe0 Left Ctrl
#   0x8b MuHenkan -> 0xe2 Left Alt
DEFAULT_TABLE = {
    0x39: 0xe0,
    0x8a: 0xe0,
    0x8b: 0xe2,
}


def convert_report(payload, table=DEFAULT_TABLE):
    """Convert a keyboard report payload and append a recomputed checksum.

    ``payload`` is the report bytes ``[connection-info][modifier][reserved]
    [keys...][seq-num]``. Returns the converted payload followed by the
    recalculated checksum byte (i.e. the bytes that follow the report-type
    byte in a frame).
    """
    max_key_num = len(payload) - 4  # exclude connection-info/modifier/reserved/seq-num
    conn_info = payload[0]
    inmod = payload[1]
    seq = payload[-1]
    out_keys = []
    out_key_count = 0
    outmod = 0x00

    # Each set bit of the input modifier byte is keycode 0xe0..0xe7.
    for i in range(8):
        if out_key_count > max_key_num - 1:
            break
        if inmod & (1 << i):
            inmod_key = MODIFIER_BASE + i
            if inmod_key in table:
                conv_key = table[inmod_key]
                if conv_key == 0x00:
                    continue
                if is_modifier(conv_key):
                    outmod |= modifier_bit(conv_key)
                else:
                    out_keys.append(conv_key)
                    out_key_count += 1
            else:
                outmod |= inmod & (1 << i)

    # The key slots follow connection-info/modifier/reserved (3 bytes).
    for idx in range(max_key_num):
        inkey = payload[3 + idx]
        if out_key_count > max_key_num - 1:
            break
        if inkey in table:
            conv_key = table[inkey]
            if conv_key == 0x00:
                continue
            if is_modifier(conv_key):
                outmod |= modifier_bit(conv_key)
            else:
                out_keys.append(conv_key)
                out_key_count += 1
        else:
            out_keys.append(inkey)
            out_key_count += 1

    out_keys = (out_keys + [0] * max_key_num)[:max_key_num]
    body = bytes([conn_info, outmod, 0x00] + out_keys + [seq])
    return body + bytes([checksum(body)])
