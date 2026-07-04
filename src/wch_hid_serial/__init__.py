"""wch_hid_serial: tools for USB HID over UART using WCH chips.

Implemented:

- CH9350L (:mod:`wch_hid_serial.ch9350`): a bidirectional HID-over-UART
  bridge carrying near-raw HID report frames. Its lower end captures a real
  USB keyboard/mouse to serial; its upper end emulates a USB HID
  keyboard/mouse from serial. Each end can be used on its own.
- CH9329 (:mod:`wch_hid_serial.ch9329`): emulates a USB HID keyboard/mouse
  from serial. This does the same job as a CH9350L upper end (both can be
  used on their own); the difference is the interface -- the CH9329 uses a
  high-level command protocol, while the CH9350L carries near-raw HID
  report frames.

Support for CH9328 is planned as another sibling subpackage. The
chip-agnostic USB HID helpers live in :mod:`wch_hid_serial.hid`.
"""

__version__ = "0.1.0"
