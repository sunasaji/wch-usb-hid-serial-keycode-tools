import pytest

from wch_hid_serial.ch9328 import Ch9328


class FakePort:
    def __init__(self):
        self.writes = []

    def write(self, data):
        self.writes.append(bytes(data))


def hx(s):
    return bytes.fromhex(s)


def test_send_report_and_release():
    port = FakePort()
    dev = Ch9328(port)
    dev.send_report(0x02, [0x05])
    dev.release_keys()
    assert port.writes == [
        hx("02 00 05 00 00 00 00 00"),
        hx("00 00 00 00 00 00 00 00"),
    ]


def test_type_text_press_release():
    port = FakePort()
    Ch9328(port).type_text("A")
    assert port.writes == [
        hx("02 00 04 00 00 00 00 00"),  # Shift + 'a'
        hx("00 00 00 00 00 00 00 00"),  # release
    ]


def test_send_ascii_passes_bytes_through():
    port = FakePort()
    Ch9328(port).send_ascii("Hi\n")
    assert port.writes == [b"Hi\n"]


def test_send_ascii_rejects_non_ascii():
    with pytest.raises(UnicodeEncodeError):
        Ch9328(FakePort()).send_ascii("café")
