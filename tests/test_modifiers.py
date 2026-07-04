import pytest

from wch_hid_serial.hid import (
    MOD_LALT,
    MOD_LCTRL,
    MOD_LGUI,
    MOD_LSHIFT,
    MOD_RALT,
    modifier_name_to_bit,
    modifiers_to_byte,
)


def test_bit_constants():
    assert (MOD_LCTRL, MOD_LSHIFT, MOD_LALT, MOD_LGUI) == (0x01, 0x02, 0x04, 0x08)


def test_name_to_bit_aliases():
    assert modifier_name_to_bit("ctrl") == MOD_LCTRL
    assert modifier_name_to_bit("CONTROL") == MOD_LCTRL
    assert modifier_name_to_bit("shift") == MOD_LSHIFT
    assert modifier_name_to_bit("win") == MOD_LGUI
    assert modifier_name_to_bit("super") == MOD_LGUI
    assert modifier_name_to_bit("meta") == MOD_LGUI
    assert modifier_name_to_bit("altgr") == MOD_RALT


def test_name_to_bit_unknown():
    with pytest.raises(ValueError):
        modifier_name_to_bit("hyper")


def test_modifiers_to_byte_combines():
    assert modifiers_to_byte(["ctrl", "shift"]) == 0x03
    assert modifiers_to_byte([]) == 0
