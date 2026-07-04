"""CH9350L serial I/O: opening ports and reading frames from a port."""

from ..serialio import open_port  # re-exported for backwards compatibility

__all__ = ["open_port", "read_response", "iter_lower_frames"]


def read_response(port):
    """Read one response frame from ``port`` (e.g. the upper CH9350L).

    Reads bytes until (but not including) the next frame-start byte 0x57 and
    returns a frame beginning with 0x57. Returns ``b""`` if nothing is
    waiting.
    """
    if port.in_waiting <= 0:
        return b""
    data = bytearray([0x57])
    b = port.read(1)
    while b != b"\x57":
        data += b
        b = port.read(1)
    return bytes(data)


def iter_lower_frames(port):
    """Yield complete frames read from the lower CH9350L ``port``.

    Each yielded value is the raw frame bytes starting with ``57 ab``. This
    is an infinite generator that blocks on the serial port; iterate it with
    a ``for`` loop. Bytes that do not form a valid ``57 ab`` head are skipped
    (resynchronisation).
    """
    r = port.read(1)
    while True:
        if r != b"\x57":
            r = port.read(1)
            continue
        r = port.read(1)  # second head byte
        if r != b"\xab":
            continue  # resync; r is re-examined at the loop top
        r = port.read(1)  # command byte
        cmd = r[0]
        if cmd == 0x82:
            status = port.read(1)
            yield bytes([0x57, 0xab, 0x82]) + status
            r = port.read(1)
        elif cmd in (0x83, 0x88):
            length = port.read(1)[0]
            report_type = port.read(1)[0]
            payload = port.read(length - 2)
            chk = port.read(1)
            yield bytes([0x57, 0xab, cmd, length, report_type]) + payload + chk
            r = port.read(1)
        else:
            frame = bytearray([0x57, 0xab]) + r
            while r != b"\x57":
                r = port.read(1)
                frame += r
            yield bytes(frame[:-1])  # drop the trailing 0x57 (start of next frame)
            # r == b"\x57" is carried to the next iteration
