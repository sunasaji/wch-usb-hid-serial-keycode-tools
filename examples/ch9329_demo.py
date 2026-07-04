#!/usr/bin/env python3
"""Sample: build CH9329 packets for common operations (no hardware needed).

Run:  python examples/ch9329_demo.py

This prints the packet bytes for typical keyboard and mouse operations. To
actually drive a device, see the commented Ch9329 section at the bottom.
"""

from wch_hid_serial.ch9329 import (
    RELEASE_PACKET,
    absolute_packet,
    button_mask,
    general_packet,
    iter_text_packets,
    relative_packet,
    scale_abs,
)
from wch_hid_serial.hid import modifier_name_to_bit


def show(label, packet):
    print(f"{label:24} {packet.hex(' ')}")


# --- keyboard ---
show("press 'a'", general_packet(0, [0x04]))
show("release all keys", RELEASE_PACKET)
show("Ctrl+C", general_packet(modifier_name_to_bit("ctrl"), [0x06]))
for i, packet in enumerate(iter_text_packets("Hi")):
    show(f"type 'Hi' [{i}]", packet)

# --- mouse ---
show("move rel (+5,-3)", relative_packet(5, -3))
show("left button down", relative_packet(0, 0, button_mask("left")))
show("scroll up 1", relative_packet(0, 0, 0, 1))
x, y = scale_abs(960, 540, 1920, 1080)  # centre of a 1920x1080 screen
show("move abs centre", absolute_packet(x, y))

# --- driving a real device (needs a serial port) ---
# from wch_hid_serial.ch9329 import Ch9329, open_port
# dev = Ch9329(open_port("COM1,9600"))
# dev.type_text("Hello!\n")            # type text as keystrokes
# dev.tap_key(0x04, modifier_name_to_bit("ctrl"))  # Ctrl+A
# dev.click("left")                    # click
# dev.drag(100, 100, 300, 300, screen=(1920, 1080))  # drag on screen
