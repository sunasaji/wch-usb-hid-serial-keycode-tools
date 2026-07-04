"""CH9329 serial device: send keyboard/mouse commands over a serial port."""

import time

from ..serialio import open_port
from . import keyboard, mouse

__all__ = ["open_port", "Ch9329"]


class Ch9329:
    """Send USB HID commands to a CH9329 over a serial port.

    ``port`` is an open ``serial.Serial`` (see :func:`open_port`). Commands
    are written fire-and-forget; response frames are not read. Mouse button
    state is tracked so that a held button persists across relative moves
    (needed for dragging).
    """

    def __init__(self, port):
        self.port = port
        self._buttons = 0

    # --- keyboard ---------------------------------------------------------
    def send_keyboard(self, modifier=0, keycodes=()):
        """Send one keyboard general-data report (does not auto-release)."""
        self.port.write(keyboard.general_packet(modifier, keycodes))

    def release_keys(self):
        """Send an all-zero keyboard report to release every key."""
        self.port.write(keyboard.RELEASE_PACKET)

    def tap_key(self, keycode, modifier=0, release_delay=0.01):
        """Press ``keycode`` (with optional ``modifier``) then release."""
        self.port.write(keyboard.general_packet(modifier, [keycode]))
        if release_delay:
            time.sleep(release_delay)
        self.release_keys()

    def type_text(self, text, wait=0.0):
        """Type ``text`` as keystrokes (press+release per character).

        ``wait`` is an optional delay in seconds after each packet.
        """
        for packet in keyboard.iter_text_packets(text):
            self.port.write(packet)
            if wait:
                time.sleep(wait)

    # --- mouse ------------------------------------------------------------
    def move_mouse(self, x=0, y=0, wheel=0):
        """Relative mouse move (keeps any currently held buttons)."""
        self.port.write(mouse.relative_packet(x, y, self._buttons, wheel))

    def move_absolute(self, x, y, screen=None, wheel=0):
        """Absolute mouse move.

        ``x``/``y`` are CH9329 coordinates (0..4095), or screen pixels if
        ``screen=(width, height)`` is given (they are then scaled).
        """
        if screen is not None:
            x, y = mouse.scale_abs(x, y, screen[0], screen[1])
        self.port.write(mouse.absolute_packet(x, y, self._buttons, wheel))

    def mouse_down(self, button="left"):
        """Press and hold a mouse button (persists until released)."""
        self._buttons |= mouse.button_mask(button)
        self.port.write(mouse.relative_packet(0, 0, self._buttons))

    def mouse_up(self, button="left"):
        """Release a held mouse button."""
        self._buttons &= ~mouse.button_mask(button) & 0xff
        self.port.write(mouse.relative_packet(0, 0, self._buttons))

    def click(self, button="left", press_delay=0.01):
        """Press and release a mouse button."""
        self.mouse_down(button)
        if press_delay:
            time.sleep(press_delay)
        self.mouse_up(button)

    def scroll(self, amount):
        """Scroll the wheel (positive up, negative down)."""
        self.port.write(mouse.relative_packet(0, 0, self._buttons, amount))

    def drag(self, x1, y1, x2, y2, button="left", screen=None, delay=0.05):
        """Drag from (x1,y1) to (x2,y2) with ``button`` held (absolute move)."""
        self.move_absolute(x1, y1, screen)
        if delay:
            time.sleep(delay)
        self.mouse_down(button)
        if delay:
            time.sleep(delay)
        self.move_absolute(x2, y2, screen)
        if delay:
            time.sleep(delay)
        self.mouse_up(button)
