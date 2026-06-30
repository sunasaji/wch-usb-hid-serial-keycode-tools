"""CH9350L support: protocol framing, key conversion, device I/O and keysend."""

from .protocol import (
    HEAD,
    CMD_STATUS,
    NO_RESPONSE_COMMANDS,
    checksum,
    is_keyboard_report,
    to_hex,
)
from .convert import DEFAULT_TABLE, convert_report
from .device import open_port, iter_lower_frames, read_response
from .keysend import (
    EMPTY_REPORT,
    NEWLINE_REPORT,
    RESET_STATUS,
    SET_STATUS_2,
    iter_key_reports,
)

__all__ = [
    "HEAD",
    "CMD_STATUS",
    "NO_RESPONSE_COMMANDS",
    "checksum",
    "is_keyboard_report",
    "to_hex",
    "DEFAULT_TABLE",
    "convert_report",
    "open_port",
    "iter_lower_frames",
    "read_response",
    "EMPTY_REPORT",
    "NEWLINE_REPORT",
    "RESET_STATUS",
    "SET_STATUS_2",
    "iter_key_reports",
]
