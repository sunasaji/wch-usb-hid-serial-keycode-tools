from itertools import islice

from wch_hid_serial.ch9350 import iter_lower_frames, read_response


class FakeSerial:
    """Minimal serial stand-in backed by a fixed byte stream."""

    def __init__(self, data):
        self.data = bytes(data)
        self.pos = 0

    @property
    def in_waiting(self):
        return len(self.data) - self.pos

    def read(self, n=1):
        assert self.pos + n <= len(self.data), "read past end of fake stream"
        chunk = self.data[self.pos:self.pos + n]
        self.pos += n
        return chunk


def hx(s):
    return bytes.fromhex(s)


def test_iter_length_delimited_frames():
    status = hx("57 ab 82 00")
    keyboard = hx("57 ab 83 0c 12 01 00 00 04 00 00 00 00 00 5f aa")
    mouse = hx("57 ab 83 08 22 01 00 00 00 00 00 7f")
    port = FakeSerial(status + keyboard + mouse)
    frames = list(islice(iter_lower_frames(port), 3))
    assert frames == [status, keyboard, mouse]


def test_iter_command_frame_terminated_by_next_head():
    # An "else" command frame is delimited by the next 0x57; that byte is
    # consumed but not included in the yielded frame.
    port = FakeSerial(hx("57 ab 81 02 57"))
    frames = list(islice(iter_lower_frames(port), 1))
    assert frames == [hx("57 ab 81 02")]


def test_iter_resyncs_on_garbage():
    port = FakeSerial(hx("ff 00 57 ab 82 09"))
    frames = list(islice(iter_lower_frames(port), 1))
    assert frames == [hx("57 ab 82 09")]


def test_read_response():
    port = FakeSerial(hx("ab 82 01 57"))
    assert read_response(port) == hx("57 ab 82 01")


def test_read_response_empty():
    port = FakeSerial(b"")
    assert read_response(port) == b""
