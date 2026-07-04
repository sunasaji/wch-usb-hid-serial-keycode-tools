"""CH9329 support: serial-to-USB-HID keyboard and mouse.

The CH9329 receives UART command packets and emulates a USB HID keyboard and
mouse. This does the same job as the *upper* end of a CH9350L (both emulate a
USB HID device from serial and can be used on their own); the difference is the
interface -- the CH9329 uses a high-level command protocol, while the CH9350L
carries near-raw HID report frames.
"""

from .protocol import (
    HEAD,
    DEFAULT_ADDR,
    CMD_GET_INFO,
    CMD_SEND_KB_GENERAL,
    CMD_SEND_KB_MEDIA,
    CMD_SEND_MS_ABS,
    CMD_SEND_MS_REL,
    checksum,
    build_packet,
    to_hex,
)
from .keyboard import general_report, general_packet, iter_text_packets, RELEASE_PACKET
from .mouse import (
    relative_packet,
    absolute_packet,
    button_mask,
    scale_abs,
    BUTTON_LEFT,
    BUTTON_RIGHT,
    BUTTON_MIDDLE,
)
from .device import open_port, Ch9329

__all__ = [
    "HEAD",
    "DEFAULT_ADDR",
    "CMD_GET_INFO",
    "CMD_SEND_KB_GENERAL",
    "CMD_SEND_KB_MEDIA",
    "CMD_SEND_MS_ABS",
    "CMD_SEND_MS_REL",
    "checksum",
    "build_packet",
    "to_hex",
    "general_report",
    "general_packet",
    "iter_text_packets",
    "RELEASE_PACKET",
    "relative_packet",
    "absolute_packet",
    "button_mask",
    "scale_abs",
    "BUTTON_LEFT",
    "BUTTON_RIGHT",
    "BUTTON_MIDDLE",
    "open_port",
    "Ch9329",
]
