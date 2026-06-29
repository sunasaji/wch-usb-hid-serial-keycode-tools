#!/usr/bin/env python3
# USB HID Serial Keycode Reader for CH9350L
# (C) 2022 Suna.S
# SPDX-License-Identifier: MIT
import serial
import argparse

# Argparse settings
ap = argparse.ArgumentParser(description='USB HID Serial Keycode Reader for CH9350L')
ap.add_argument('lower_serial', help='Serial port for Lower CH9350L. For example: COM1,115200')
args = ap.parse_args()
serial_args=args.lower_serial.split(",")

# Open serial port
port = serial.Serial(*serial_args)

def hx(data):
    # Format bytes as space-separated hex for output, e.g. "57 ab 83 0c"
    return data.hex(" ")

r = port.read(1)
while True:
    while (port.in_waiting > 0):
        if(r==b"\x57"):
            r=port.read(1)
            if(r==b"\xab"):
                r=port.read(1)
                if(r==b"\x82"):
                    r=port.read(1)
                    #print(hx(bytes([0x57, 0xab, 0x82])+r))
                elif(r==b"\x83" or r==b"\x88"):
                    cmd=r[0]
                    length=port.read(1)[0]
                    report_type=port.read(1)[0]
                    payload=port.read(length-2)
                    checksum=port.read(1)
                    frame=bytes([0x57, 0xab, cmd, length, report_type])+payload+checksum
                    print(hx(frame))
                else:
                    frame=bytearray([0x57, 0xab])+r
                    while(r != b"\x57"):
                        r=port.read(1)
                        frame+=r
                    print(hx(bytes(frame[:-1]))) #drop the trailing 0x57 (start of the next frame)
                    continue
        r=port.read(1)
