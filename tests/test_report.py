from wch_hid_serial.hid import RELEASE_REPORT, iter_text_reports, keyboard_report


def hx(s):
    return bytes.fromhex(s)


def test_keyboard_report():
    assert keyboard_report(0x02, [0x04]) == hx("02 00 04 00 00 00 00 00")
    assert keyboard_report() == hx("00 00 00 00 00 00 00 00")
    assert RELEASE_REPORT == hx("00 00 00 00 00 00 00 00")
    # More than 6 keycodes are truncated to 6.
    assert keyboard_report(0, [1, 2, 3, 4, 5, 6, 7]) == hx("00 00 01 02 03 04 05 06")


def test_iter_text_reports_press_release():
    assert list(iter_text_reports("A")) == [
        hx("02 00 04 00 00 00 00 00"),  # Shift + 'a'
        RELEASE_REPORT,
    ]


def test_iter_text_reports_multiple_and_skip():
    assert list(iter_text_reports("a\x00b")) == [
        hx("00 00 04 00 00 00 00 00"),  # a
        RELEASE_REPORT,
        hx("00 00 05 00 00 00 00 00"),  # b (unmapped 0x00 skipped)
        RELEASE_REPORT,
    ]
