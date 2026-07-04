"""CH9329 serial protocol: frame constants and packet building.

The CH9329 turns UART commands from the host into USB HID keyboard/mouse
output. A command packet is::

    HEAD(0x57 0xAB)  ADDR  CMD  LEN  DATA...  SUM

``SUM`` is the low byte of the sum of every preceding byte (head, address,
command, length and data). Protocol confirmed against the CH9329 datasheet
and the CH9329_COMM reference implementation.
"""

HEAD = bytes([0x57, 0xab])
DEFAULT_ADDR = 0x00

# Command codes (CMD byte).
CMD_GET_INFO = 0x01
CMD_SEND_KB_GENERAL = 0x02  # standard keyboard report
CMD_SEND_KB_MEDIA = 0x03    # multimedia / system keys
CMD_SEND_MS_ABS = 0x04      # absolute mouse
CMD_SEND_MS_REL = 0x05      # relative mouse


def checksum(data):
    """Low byte of the sum of ``data`` (the CH9329 packet checksum)."""
    return sum(data) & 0xff


def build_packet(cmd, data=b"", addr=DEFAULT_ADDR):
    """Build a full CH9329 command packet (with head, length and checksum)."""
    data = bytes(data)
    body = HEAD + bytes([addr & 0xff, cmd & 0xff, len(data)]) + data
    return body + bytes([checksum(body)])


def to_hex(data):
    """Format bytes as space-separated hex, e.g. ``"57 ab 00 02"``."""
    return data.hex(" ")
