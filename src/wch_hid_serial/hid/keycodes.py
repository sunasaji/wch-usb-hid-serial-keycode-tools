"""USB HID keyboard keycodes and the US-layout ASCII conversion table.

These are standard USB HID definitions, not specific to any chip, so they
are shared by every chip backend in this package.
"""

# High bit of an ASCII_TO_KEYCODE entry means "press with Shift".
SHIFT_FLAG = 0x80

# Modifier keycodes occupy 0xe0..0xe7 (Left Ctrl .. Right GUI).
MODIFIER_BASE = 0xe0
MOD_LEFT_CTRL = 0xe0
MOD_LEFT_SHIFT = 0xe1
MOD_LEFT_ALT = 0xe2
MOD_LEFT_GUI = 0xe3
MOD_RIGHT_CTRL = 0xe4
MOD_RIGHT_SHIFT = 0xe5
MOD_RIGHT_ALT = 0xe6
MOD_RIGHT_GUI = 0xe7


def is_modifier(keycode):
    """Return True if ``keycode`` is a modifier key (0xe0..0xe7)."""
    return MODIFIER_BASE <= keycode <= MODIFIER_BASE + 7


def modifier_bit(keycode):
    """Return the modifier-byte bit for a modifier ``keycode`` (0xe0..0xe7)."""
    return 1 << (keycode - MODIFIER_BASE)


# ASCII -> HID keycode (high bit = Shift), US layout. 128 entries (NUL..DEL).
# Derived from Adafruit_CircuitPython_HID keyboard_layout_us.py (MIT).
ASCII_TO_KEYCODE = (
    b"\x00"  # NUL
    b"\x00"  # SOH
    b"\x00"  # STX
    b"\x00"  # ETX
    b"\x00"  # EOT
    b"\x00"  # ENQ
    b"\x00"  # ACK
    b"\x00"  # BEL \a
    b"\x2a"  # BS BACKSPACE \b (called DELETE in the usb.org document)
    b"\x2b"  # TAB \t
    b"\x28"  # LF \n (called Return or ENTER in the usb.org document)
    b"\x00"  # VT \v
    b"\x00"  # FF \f
    b"\x00"  # CR \r
    b"\x00"  # SO
    b"\x00"  # SI
    b"\x00"  # DLE
    b"\x00"  # DC1
    b"\x00"  # DC2
    b"\x00"  # DC3
    b"\x00"  # DC4
    b"\x00"  # NAK
    b"\x00"  # SYN
    b"\x00"  # ETB
    b"\x00"  # CAN
    b"\x00"  # EM
    b"\x00"  # SUB
    b"\x29"  # ESC
    b"\x00"  # FS
    b"\x00"  # GS
    b"\x00"  # RS
    b"\x00"  # US
    b"\x2c"  # SPACE
    b"\x9e"  # ! x1e|SHIFT_FLAG (shift 1)
    b"\xb4"  # " x34|SHIFT_FLAG (shift ')
    b"\xa0"  # # x20|SHIFT_FLAG (shift 3)
    b"\xa1"  # $ x21|SHIFT_FLAG (shift 4)
    b"\xa2"  # % x22|SHIFT_FLAG (shift 5)
    b"\xa4"  # & x24|SHIFT_FLAG (shift 7)
    b"\x34"  # '
    b"\xa6"  # ( x26|SHIFT_FLAG (shift 9)
    b"\xa7"  # ) x27|SHIFT_FLAG (shift 0)
    b"\xa5"  # * x25|SHIFT_FLAG (shift 8)
    b"\xae"  # + x2e|SHIFT_FLAG (shift =)
    b"\x36"  # ,
    b"\x2d"  # -
    b"\x37"  # .
    b"\x38"  # /
    b"\x27"  # 0
    b"\x1e"  # 1
    b"\x1f"  # 2
    b"\x20"  # 3
    b"\x21"  # 4
    b"\x22"  # 5
    b"\x23"  # 6
    b"\x24"  # 7
    b"\x25"  # 8
    b"\x26"  # 9
    b"\xb3"  # : x33|SHIFT_FLAG (shift ;)
    b"\x33"  # ;
    b"\xb6"  # < x36|SHIFT_FLAG (shift ,)
    b"\x2e"  # =
    b"\xb7"  # > x37|SHIFT_FLAG (shift .)
    b"\xb8"  # ? x38|SHIFT_FLAG (shift /)
    b"\x9f"  # @ x1f|SHIFT_FLAG (shift 2)
    b"\x84"  # A x04|SHIFT_FLAG (shift a)
    b"\x85"  # B x05|SHIFT_FLAG (etc.)
    b"\x86"  # C x06|SHIFT_FLAG
    b"\x87"  # D x07|SHIFT_FLAG
    b"\x88"  # E x08|SHIFT_FLAG
    b"\x89"  # F x09|SHIFT_FLAG
    b"\x8a"  # G x0a|SHIFT_FLAG
    b"\x8b"  # H x0b|SHIFT_FLAG
    b"\x8c"  # I x0c|SHIFT_FLAG
    b"\x8d"  # J x0d|SHIFT_FLAG
    b"\x8e"  # K x0e|SHIFT_FLAG
    b"\x8f"  # L x0f|SHIFT_FLAG
    b"\x90"  # M x10|SHIFT_FLAG
    b"\x91"  # N x11|SHIFT_FLAG
    b"\x92"  # O x12|SHIFT_FLAG
    b"\x93"  # P x13|SHIFT_FLAG
    b"\x94"  # Q x14|SHIFT_FLAG
    b"\x95"  # R x15|SHIFT_FLAG
    b"\x96"  # S x16|SHIFT_FLAG
    b"\x97"  # T x17|SHIFT_FLAG
    b"\x98"  # U x18|SHIFT_FLAG
    b"\x99"  # V x19|SHIFT_FLAG
    b"\x9a"  # W x1a|SHIFT_FLAG
    b"\x9b"  # X x1b|SHIFT_FLAG
    b"\x9c"  # Y x1c|SHIFT_FLAG
    b"\x9d"  # Z x1d|SHIFT_FLAG
    b"\x2f"  # [
    b"\x31"  # \ backslash
    b"\x30"  # ]
    b"\xa3"  # ^ x23|SHIFT_FLAG (shift 6)
    b"\xad"  # _ x2d|SHIFT_FLAG (shift -)
    b"\x35"  # `
    b"\x04"  # a
    b"\x05"  # b
    b"\x06"  # c
    b"\x07"  # d
    b"\x08"  # e
    b"\x09"  # f
    b"\x0a"  # g
    b"\x0b"  # h
    b"\x0c"  # i
    b"\x0d"  # j
    b"\x0e"  # k
    b"\x0f"  # l
    b"\x10"  # m
    b"\x11"  # n
    b"\x12"  # o
    b"\x13"  # p
    b"\x14"  # q
    b"\x15"  # r
    b"\x16"  # s
    b"\x17"  # t
    b"\x18"  # u
    b"\x19"  # v
    b"\x1a"  # w
    b"\x1b"  # x
    b"\x1c"  # y
    b"\x1d"  # z
    b"\xaf"  # { x2f|SHIFT_FLAG (shift [)
    b"\xb1"  # | x31|SHIFT_FLAG (shift \)
    b"\xb0"  # } x30|SHIFT_FLAG (shift ])
    b"\xb5"  # ~ x35|SHIFT_FLAG (shift `)
    b"\x4c"  # DEL DELETE (called Forward Delete in usb.org document)
)


def ascii_to_keycode(ch):
    """Map a single ASCII character to ``(shift, keycode)``.

    ``shift`` is a bool (whether the character requires the Shift key) and
    ``keycode`` is the 7-bit HID keycode. Returns ``None`` for characters
    that have no mapping (keycode 0) or that are outside ASCII (ord >= 128).
    """
    c = ord(ch)
    if c >= 128:
        return None
    shifted = ASCII_TO_KEYCODE[c]
    if shifted == 0:
        return None
    return bool(shifted & SHIFT_FLAG), shifted & 0x7f
