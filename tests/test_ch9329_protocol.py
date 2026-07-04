from wch_hid_serial.ch9329 import build_packet, checksum


def hx(s):
    return bytes.fromhex(s)


def test_checksum():
    assert checksum(hx("57 ab 00 02 08 00 00 04 00 00 00 00 00")) == 0x10
    assert checksum(b"") == 0
    assert checksum(bytes([0xff, 0x02])) == 0x01  # wraps at 0x100


def test_build_packet_wraps_head_len_and_checksum():
    # Keyboard general data for key 'a' (0x04).
    data = hx("00 00 04 00 00 00 00 00")
    assert build_packet(0x02, data) == hx("57 ab 00 02 08 00 00 04 00 00 00 00 00 10")


def test_build_packet_empty_data():
    # HEAD + addr + cmd + len(0) + checksum; sum(57 ab 00 01 00) & 0xff = 0x03
    assert build_packet(0x01) == hx("57 ab 00 01 00 03")
