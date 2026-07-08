import pytest

from wch_hid_serial.hid import (
    char_to_hid,
    resolve_key,
    special_key_to_hid,
    validate_chars,
)


def test_special_key_to_hid():
    assert special_key_to_hid("enter") == 0x28
    assert special_key_to_hid("ESC") == 0x29  # case-insensitive alias
    assert special_key_to_hid("f12") == 0x45
    assert special_key_to_hid("0x2c") == 0x2C  # hex keycode string
    assert special_key_to_hid("nope") is None
    assert special_key_to_hid("0x1ff") is None  # out of 1-byte range


def test_char_to_hid_us():
    assert char_to_hid("a") == (0x00, 0x04)
    assert char_to_hid("A") == (0x02, 0x04)
    assert char_to_hid("@") == (0x02, 0x1F)  # Shift+2 on US
    assert char_to_hid("\n") == (0x00, 0x28)
    assert char_to_hid("€") is None  # euro sign: unmapped


def test_resolve_key():
    assert resolve_key("c", ["ctrl"]) == (0x01, 0x06)  # Ctrl+C
    assert resolve_key("a", ["ctrl", "shift"]) == (0x03, 0x04)
    assert resolve_key("a", "ctrl+shift") == (0x03, 0x04)  # combo string
    assert resolve_key("enter") == (0x00, 0x28)
    assert resolve_key("0x2c") == (0x00, 0x2C)
    assert resolve_key("A") == (0x02, 0x04)  # the char's own Shift modifier
    assert resolve_key("€") is None


def test_validate_chars():
    validate_chars("Hello, World!\n\t")  # printable + tab/newline: no raise
    with pytest.raises(ValueError):
        validate_chars("café")  # non-ASCII
    with pytest.raises(ValueError):
        validate_chars("\x00")  # control char
