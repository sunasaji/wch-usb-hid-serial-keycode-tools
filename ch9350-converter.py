#!/usr/bin/env python3
# USB HID Serial Keycode Converter for CH9350L
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

# See https://gist.github.com/MightyPork/6da26e382a7ad91b5496ee55fdc73db2
# Key Conversion Table
# input_keycode : converted_keycode
# A keycode is a 1-byte scan code used in a USB HID Report.
keytbl={          #InputKey    ConvertedKey
    0x39:0xe0,    #Caps     -> LeftCtrl
    0x8a:0xe0,    #Henkan   -> LeftCtrl
    0x8b:0xe2,    #MuHenkan -> LeftAlt
}
# Modifier keycodes:
# e0: Left Control
# e1: Left Shift
# e2: Left Alt
# e3: Left GUI
# e4: Right Control
# e5: Right Shift
# e6: Right Alt
# e7: Right GUI

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

# Convert keycodes and recalculate the check sum.
# payload: bytes = [connection-info][modifier][reserved][keys...][seq-num]
# Returns bytes = converted payload followed by the recalculated checksum byte.
def convkeys(payload):
    max_key_num=len(payload)-4 # Exclude 4 slots ([connection-info] [modifier] [reserved] [seq-num])
    conn_info=payload[0] # connection info
    inmod=payload[1]     # input modifier
    seq=payload[-1]      # sequence number
    out_key_count=0
    out_keys=[]
    outmod=0x00
    for i in range(8):
        if(out_key_count>max_key_num-1):
            break
        # read each bit of input modifier and interpret it as "e0" to "e7" keycode (inmod_key)
        elif(inmod & (1 << i)):
            inmod_key=0xe0+i
            if inmod_key in keytbl:
                conv_key=keytbl[inmod_key]
                #if converted keycode is 0x00, ignore this input key
                if(conv_key==0x00):
                    continue
                #if converted keycode is a modifier key (0xe0-0xe7), set corresponding bit of output modifier keycode (outmod)
                if(0xe0<=conv_key<=0xe7):
                    outmod=outmod | (1 << (conv_key-0xe0))
                #if converted keycode is NOT a modifier key, add the converted keycode to out_keys list and increment out_key_count
                else:
                    out_keys.append(conv_key)
                    out_key_count+=1
            else:
                outmod=outmod | (inmod & (1 << i))
    for idx in range(max_key_num):
        inkey=payload[3+idx] # "3+idx" skips connection info, modifier and reserved slots
        if(out_key_count>max_key_num-1):
            break
        if inkey in keytbl:
            conv_key=keytbl[inkey]
            #if converted keycode is 0x00, ignore this input key
            if(conv_key==0x00):
                continue
            #if converted keycode is a modifier key (0xe0-0xe7), set corresponding bit of output modifier keycode (outmod)
            if(0xe0<=conv_key<=0xe7):
                outmod=outmod | (1 << (conv_key-0xe0))
            #if converted keycode is NOT a modifier key, add the converted keycode to out_keys list and increment out_key_count
            else:
                out_keys.append(conv_key)
                out_key_count+=1
        else:
            out_keys.append(inkey)
            out_key_count+=1
    # Pad / trim the key slots to max_key_num
    out_keys=(out_keys+[0]*max_key_num)[:max_key_num]
    body=bytes([conn_info, outmod, 0x00]+out_keys+[seq])
    check_sum=sum(body)&0xff # connection info + output modifier + keys + sequence number (reserved 0x00 adds nothing)
    return body+bytes([check_sum])

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
                    if((report_type>>4)==0x1): #keyboard
                        frame=bytes([0x57, 0xab, cmd, keycode_len, report_type])+convkeys(payload) #Call keycode converter
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
