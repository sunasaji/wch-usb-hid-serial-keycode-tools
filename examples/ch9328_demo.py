#!/usr/bin/env python3
"""Sample: build CH9328 keyboard data (no hardware needed).

Run:  python examples/ch9328_demo.py

The CH9328 is keyboard-only and its mode is set by hardware pins:
  - Mode 3 sends raw 8-byte HID reports (built below).
  - Modes 0-2 send plain ASCII text (the chip converts it to keystrokes).

Datasheet: https://wch-ic.com/downloads/CH9328DS1_PDF.html
"""

from wch_hid_serial.hid import keyboard_report, iter_text_reports, modifier_name_to_bit


def show(label, data):
    print(f"{label:26} {data.hex(' ')}")


# --- mode 3: raw 8-byte HID reports ---
show("press 'a'", keyboard_report(0, [0x04]))
show("Ctrl+C", keyboard_report(modifier_name_to_bit("ctrl"), [0x06]))
for i, report in enumerate(iter_text_reports("Hi")):
    show(f"type 'Hi' [{i}]", report)

# --- modes 0-2: ASCII passthrough ---
print("ascii 'Hi\\n' ->", "Hi\n".encode("ascii"))

# --- driving a real device (needs a serial port) ---
# from wch_hid_serial.ch9328 import Ch9328, open_port
# dev = Ch9328(open_port("COM1,9600"))
# dev.type_text("Hello!\n")   # mode 3: raw HID reports (press + release)
# dev.send_ascii("Hello!\n")  # modes 0-2: the chip converts ASCII to keystrokes
