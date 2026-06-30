from wch_hid_serial.ch9350 import (
    NO_RESPONSE_COMMANDS,
    checksum,
    is_keyboard_report,
)


def test_checksum():
    assert checksum(bytes.fromhex("01 01 00 00 00 00 00 00 00 5f")) == 0x61
    assert checksum(b"") == 0
    assert checksum(bytes([0xff, 0x02])) == 0x01  # wraps at 0x100


def test_is_keyboard_report():
    assert is_keyboard_report(0x12)
    assert not is_keyboard_report(0x22)  # mouse


def test_no_response_commands():
    assert 0x81 in NO_RESPONSE_COMMANDS
    assert 0x40 in NO_RESPONSE_COMMANDS
    assert 0x83 not in NO_RESPONSE_COMMANDS
