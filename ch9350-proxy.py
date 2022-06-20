#!/usr/bin/env python3
# USB HID Serial Keycode Proxy for CH9350L
# (C) 2022 Suna.S
# SPDX-License-Identifier: MIT
import serial
import argparse

# Argparse settings
ap = argparse.ArgumentParser(description='USB HID Serial Keycode Converter for CH9350L')
ap.add_argument('upper_serial', help='Serial port for Upper CH9350L. For example: COM1,115200')
ap.add_argument('lower_serial', help='Serial port for Lower CH9350L. For example: COM2,115200')
args = ap.parse_args()
upper_serial_args=args.upper_serial.split(",")
lower_serial_args=args.lower_serial.split(",")

# Open serial ports
upport = serial.Serial(*upper_serial_args)
lowport = serial.Serial(*lower_serial_args)

def readport(p):
    result=""
    if(p.in_waiting>0):
        result="57 "
        r=p.read(1).hex()
        while (r!='57'):
            result+=r+" "
            r=p.read(1).hex()
    return(result)

r = lowport.read(1).hex()
while True:
    while (lowport.in_waiting > 0):
        if(r=='57'):
            r=lowport.read(1).hex()
            if(r=='ab'):
                r=lowport.read(1).hex()
                if(r=='82'):
                    r=lowport.read(1).hex()
                    string="57 ab 82 "+r
                    #Suppress status request/response frames. If needed, uncomment below prints.
                    #print("L> "+string)
                    upport.write(list(bytearray.fromhex(string)))
                    #print("U< "+string)
                    upreturn=readport(upport)[:-1]
                    #print("U> "+upreturn)
                    lowport.write(list(bytearray.fromhex(upreturn)))
                    #print("L< "+upreturn)
                    r=lowport.read(1).hex()
                elif(r=='83' or r=='88'):
                    r2=lowport.read(1)
                    keycode_len=int.from_bytes(r2,'big')
                    r3=lowport.read(1).hex()
                    r4=""
                    #checksum=0
                    for i in range(keycode_len-2):
                        r5=lowport.read(1)
                        r4+=" "+r5.hex()
                        #checksum=(checksum+int.from_bytes(r5,'big'))&0xff
                    r6=lowport.read(1).hex()
                    string="57 ab "+r+" "+r2.hex()+" "+r3+r4+" "+r6
                    #print(string +" check:"+'%01x'%(checksum & 0xff))
                    print("L> "+string)
                    upport.write(list(bytearray.fromhex(string)))
                    print("U< "+string)
                    r=lowport.read(1).hex()
                else:
                    string="57 ab "+r
                    while(r != '57'):
                        r=lowport.read(1).hex()
                        string+=" "+r
                    print("L> "+string[:-3])
                    upport.write(list(bytearray.fromhex(string[:-3])))
                    print("U< "+string[:-3])
                    #If issued commands to upper ch9350l are not "No response" commands, then read a response from upper
                    if(string[:9]!='57 ab 81 ' and
                       string[:9]!='57 ab 84 ' and
                       string[:9]!='57 ab 85 ' and
                       string[:9]!='57 ab 86 ' and
                       string[:9]!='57 ab 87 ' and
                       string[:9]!='57 ab 40 '):
                        upreturn=readport(upport)[:-1]
                        print("U> "+upreturn)
                        lowport.write(list(bytearray.fromhex(upreturn)))
                        print("L< "+upreturn)
