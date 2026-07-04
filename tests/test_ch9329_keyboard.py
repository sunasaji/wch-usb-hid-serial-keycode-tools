from wch_hid_serial.ch9329 import (
    RELEASE_PACKET,
    general_packet,
    general_report,
    iter_text_packets,
)


def hx(s):
    return bytes.fromhex(s)


def test_general_report_padding_and_modifier():
    assert general_report(0x02, [0x04]) == hx("02 00 04 00 00 00 00 00")
    assert general_report() == hx("00 00 00 00 00 00 00 00")
    # More than 6 keycodes are truncated to 6.
    assert general_report(0, [1, 2, 3, 4, 5, 6, 7]) == hx("00 00 01 02 03 04 05 06")


def test_general_packet_and_release():
    assert general_packet(0, [0x04]) == hx("57 ab 00 02 08 00 00 04 00 00 00 00 00 10")
    assert RELEASE_PACKET == hx("57 ab 00 02 08 00 00 00 00 00 00 00 00 0c")


def test_iter_text_packets_press_release():
    # 'A' = Shift + keycode 0x04, then release.
    assert list(iter_text_packets("A")) == [
        hx("57 ab 00 02 08 02 00 04 00 00 00 00 00 12"),
        RELEASE_PACKET,
    ]


def test_iter_text_packets_multiple_and_skip():
    # 'a','b' each press+release; unmapped chars are skipped.
    packets = list(iter_text_packets("a\x00b"))
    assert packets == [
        hx("57 ab 00 02 08 00 00 04 00 00 00 00 00 10"),  # a
        RELEASE_PACKET,
        hx("57 ab 00 02 08 00 00 05 00 00 00 00 00 11"),  # b
        RELEASE_PACKET,
    ]
