from wch_hid_serial.hid import (
    ASCII_TO_KEYCODE,
    ascii_to_keycode,
    is_modifier,
    modifier_bit,
)


def test_table_length():
    assert len(ASCII_TO_KEYCODE) == 128


def test_ascii_to_keycode_basic():
    assert ascii_to_keycode("a") == (False, 0x04)
    assert ascii_to_keycode("A") == (True, 0x04)
    assert ascii_to_keycode("1") == (False, 0x1e)
    assert ascii_to_keycode("!") == (True, 0x1e)
    assert ascii_to_keycode("\n") == (False, 0x28)


def test_ascii_to_keycode_unmapped():
    assert ascii_to_keycode("\x00") is None  # NUL has no keycode
    assert ascii_to_keycode("\x01") is None  # SOH has no keycode


def test_modifier_helpers():
    assert is_modifier(0xe0) and is_modifier(0xe7)
    assert not is_modifier(0x04)
    assert not is_modifier(0xe8)
    assert modifier_bit(0xe0) == 0b0001
    assert modifier_bit(0xe1) == 0b0010  # Left Shift
    assert modifier_bit(0xe2) == 0b0100  # Left Alt
