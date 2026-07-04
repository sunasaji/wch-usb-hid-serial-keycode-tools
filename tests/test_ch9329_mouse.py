import pytest

from wch_hid_serial.ch9329 import (
    BUTTON_LEFT,
    BUTTON_MIDDLE,
    BUTTON_RIGHT,
    absolute_packet,
    button_mask,
    relative_packet,
    scale_abs,
)


def hx(s):
    return bytes.fromhex(s)


def test_button_mask():
    assert (button_mask("left"), button_mask("right"), button_mask("middle")) == (
        BUTTON_LEFT, BUTTON_RIGHT, BUTTON_MIDDLE)
    assert button_mask(0x03) == 0x03  # int passthrough
    with pytest.raises(ValueError):
        button_mask("side")


def test_scale_abs():
    assert scale_abs(960, 540, 1920, 1080) == (2048, 2048)  # centre
    assert scale_abs(0, 0, 1920, 1080) == (0, 0)
    assert scale_abs(1920, 1080, 1920, 1080) == (0x0fff, 0x0fff)  # clamped bottom-right


def test_relative_signed_movement():
    assert relative_packet(5, -3) == hx("57 ab 00 05 05 01 00 05 fd 00 0f")


def test_relative_button():
    assert relative_packet(0, 0, buttons=1) == hx("57 ab 00 05 05 01 01 00 00 00 0e")


def test_relative_clamps_to_int8():
    # 200 clamps to 127 (0x7f), -200 clamps to -128 (0x80).
    assert relative_packet(200, -200)[6:9] == hx("00 7f 80")


def test_absolute_little_endian_coords():
    # x=100 (0x0064), y=200 (0x00c8) as little-endian 16-bit fields.
    assert absolute_packet(100, 200) == hx("57 ab 00 04 07 02 00 64 00 c8 00 00 3b")
