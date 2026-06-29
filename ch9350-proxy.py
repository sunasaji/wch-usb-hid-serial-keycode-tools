#!/usr/bin/env python3
# USB HID Serial Keycode Proxy for CH9350L
# (C) 2022 Suna.S
# SPDX-License-Identifier: MIT
import serial
import argparse

# Argparse settings
ap = argparse.ArgumentParser(description='USB HID Serial Keycode Proxy for CH9350L')
ap.add_argument('upper_serial', help='Serial port for Upper CH9350L. For example: COM1,115200')
ap.add_argument('lower_serial', help='Serial port for Lower CH9350L. For example: COM2,115200')
args = ap.parse_args()
upper_serial_args=args.upper_serial.split(",")
lower_serial_args=args.lower_serial.split(",")

# Open serial ports
upport = serial.Serial(*upper_serial_args)
lowport = serial.Serial(*lower_serial_args)

def hx(data):
    # Format bytes as space-separated hex for debug output, e.g. "57 ab 82 00"
    return data.hex(" ")

def readport(p):
    # Read bytes until (but not including) the next frame-start byte 0x57.
    # Returns a frame starting with 0x57. Returns b"" if nothing is waiting.
    if(p.in_waiting<=0):
        return b""
    data=bytearray([0x57])
    b=p.read(1)
    while(b!=b"\x57"):
        data+=b
        b=p.read(1)
    return bytes(data)

r = lowport.read(1)
while True:
    while (lowport.in_waiting > 0):
        if(r==b"\x57"):
            r=lowport.read(1)
            if(r==b"\xab"):
                r=lowport.read(1)
                if(r==b"\x82"):
                    r=lowport.read(1)
                    frame=bytes([0x57, 0xab, 0x82])+r
                    #Suppress status request/response frames. If needed, uncomment below prints.
                    #print("L> "+hx(frame))
                    upport.write(frame)
                    #print("U< "+hx(frame))
                    upreturn=readport(upport)
                    #print("U> "+hx(upreturn))
                    lowport.write(upreturn)
                    #print("L< "+hx(upreturn))
                    r=lowport.read(1)
                elif(r==b"\x83" or r==b"\x88"):
                    cmd=r[0]
                    keycode_len=lowport.read(1)[0]
                    report_type=lowport.read(1)[0]
                    payload=lowport.read(keycode_len-2)
                    checksum=lowport.read(1)
                    frame=bytes([0x57, 0xab, cmd, keycode_len, report_type])+payload+checksum
                    print("L> "+hx(frame))
                    upport.write(frame)
                    print("U< "+hx(frame))
                    r=lowport.read(1)
                else:
                    frame=bytearray([0x57, 0xab])+r
                    while(r != b"\x57"):
                        r=lowport.read(1)
                        frame+=r
                    frame=bytes(frame[:-1]) #drop the trailing 0x57 (start of the next frame)
                    print("L> "+hx(frame))
                    upport.write(frame)
                    print("U< "+hx(frame))
                    #If issued commands to upper ch9350l are not "No response" commands, then read a response from upper
                    if(frame[:3]!=bytes([0x57,0xab,0x81]) and
                       frame[:3]!=bytes([0x57,0xab,0x84]) and
                       frame[:3]!=bytes([0x57,0xab,0x85]) and
                       frame[:3]!=bytes([0x57,0xab,0x86]) and
                       frame[:3]!=bytes([0x57,0xab,0x87]) and
                       frame[:3]!=bytes([0x57,0xab,0x40])):
                        upreturn=readport(upport)
                        print("U> "+hx(upreturn))
                        lowport.write(upreturn)
                        print("L< "+hx(upreturn))
