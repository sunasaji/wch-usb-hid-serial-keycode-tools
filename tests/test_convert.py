"""Golden tests for CH9350L keycode conversion, taken from the README."""

from wch_hid_serial.ch9350 import convert_report


def hx(s):
    return bytes.fromhex(s)


def test_caps_to_left_ctrl():
    # 00 00 39 (Caps Lock) -> 01 00 00 (Left Ctrl)
    assert convert_report(hx("01 00 00 39 00 00 00 00 00 5f")) == hx(
        "01 01 00 00 00 00 00 00 00 5f 61"
    )


def test_muhenkan_to_left_alt():
    # 00 00 8b (MuHenkan) -> 04 00 00 (Left Alt)
    assert convert_report(hx("01 00 00 8b 00 00 00 00 00 65")) == hx(
        "01 04 00 00 00 00 00 00 00 65 6a"
    )


def test_henkan_to_left_ctrl():
    # 00 00 8a (Henkan) -> 01 00 00 (Left Ctrl)
    assert convert_report(hx("01 00 00 8a 00 00 00 00 00 6b")) == hx(
        "01 01 00 00 00 00 00 00 00 6b 6d"
    )


def test_unmapped_key_passes_through():
    # 0x04 ('a') is not in the table, so it is forwarded unchanged.
    out = convert_report(hx("01 00 00 04 00 00 00 00 00 10"))
    assert out == hx("01 00 00 04 00 00 00 00 00 10 15")


def test_custom_table_drop_and_remap():
    table = {0x04: 0x00, 0x05: 0xe1}  # drop 'a'; 'b' -> Left Shift
    # 'a' dropped, 'b' becomes a modifier bit, no key slots used.
    out = convert_report(hx("01 00 00 04 05 00 00 00 00 20"), table)
    assert out == hx("01 02 00 00 00 00 00 00 00 20 23")
