from wch_hid_serial.ch9350 import (
    EMPTY_REPORT,
    NEWLINE_REPORT,
    iter_key_reports,
)


def report(modifier, keycode):
    return bytes([0x57, 0xab, 0x01, modifier, 0, keycode, 0, 0, 0, 0, 0])


A = report(0, 0x04)          # 'a'
A_SHIFT = report(0x02, 0x04)  # 'A' (Left Shift)
B = report(0, 0x05)          # 'b'


def test_single_char():
    assert list(iter_key_reports("a")) == [(A, True)]


def test_shifted_char():
    assert list(iter_key_reports("A")) == [(A_SHIFT, True)]


def test_repeated_char_inserts_empty():
    assert list(iter_key_reports("aa")) == [(A, True), (EMPTY_REPORT, False), (A, True)]


def test_newline():
    assert list(iter_key_reports("a\nb")) == [
        (A, True),
        (NEWLINE_REPORT, False),
        (EMPTY_REPORT, False),
        (B, True),
    ]


def test_unmapped_char_skipped():
    assert list(iter_key_reports("\x00")) == []


def test_etx_stops():
    assert list(iter_key_reports("a\x03b")) == [(A, True)]
