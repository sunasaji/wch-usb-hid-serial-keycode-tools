#!/usr/bin/env python3
# USB HID Serial Keycode Reader for CH9350L
# (C) 2022 Suna.S
# SPDX-License-Identifier: MIT
import serial
import argparse

# Argparse settings
ap = argparse.ArgumentParser(description='USB HID Serial Keycode Sender for CH9350L')
ap.add_argument('lower_serial', help='Serial port for Lower CH9350L. For example: COM1,115200')
args = ap.parse_args()
serial_args=args.lower_serial.split(",")

# Open serial port
port = serial.Serial(*serial_args)

r=""
r = port.read(1).hex()
while True:
    while (port.in_waiting > 0):
        if(r=='57'):
            r=port.read(1).hex()
            if(r=='ab'):
                r=port.read(1).hex()
                if(r=='82'):
                    r=port.read(1).hex()
                    #print("57 ab 82 "+r)
                elif(r=='83' or r=='88'):
                    r2=port.read(1)
                    len=int.from_bytes(r2,'big')
                    r3=port.read(1).hex()
                    r4=""
                    #checksum=0
                    for i in range(len-2):
                        r5=port.read(1)
                        r4+=" "+r5.hex()
                        #checksum=(checksum+int.from_bytes(r5,'big'))&0xff
                    r6=port.read(1).hex()
                    #print("57 ab "+r+" "+r2.hex()+" "+r3+r4+" "+r6+" check:"+'%01x'%(checksum & 0xff))
                    print("57 ab "+r+" "+r2.hex()+" "+r3+r4+" "+r6)
                else:
                    string="57 ab "+r
                    while(r != '57'):
                        r=port.read(1).hex()
                        string+=" "+r
                    print(string[:-3])
                    continue
        r=port.read(1).hex()
