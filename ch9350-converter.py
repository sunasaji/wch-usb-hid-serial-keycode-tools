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
# "input_keycode" : "converted_keycode"
# A keycode is a 1-byte scan code used in a USB HID Report.
keytbl={       #InputKey    ConvertedKey
    "39":"e0", #Caps     -> LeftCtrl
    "8a":"e0", #Henkan   -> LeftCtrl
    "8b":"e2"  #MuHenkan -> LeftAlt
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

def readport(p):
    result=""
    if(p.in_waiting>0):
        result="57 "
        r=p.read(1).hex()
        while (r!='57'):
            result+=r+" "
            r=p.read(1).hex()
    return(result)

# Convert keycodes and calculate check sum
def convkeys(input):
    input_len=len(input)//3
    max_key_num=input_len-4 # Exclude 4 slots ([connection-info] [modifier] [reserved] [seq-num])
    out_key_count=0
    out_keys=[]
    r1 = input[1:3] # connection info
    outmod = 0x00
    inmod = int(input[4:6],16) # input modifier
    for i in range(8):
        if(out_key_count>max_key_num-1):
            break
        # read each bit of input modifier and interpret it as "e0" to "e7" keycode (inmod_key)
        elif(inmod & 1 << i):
            inmod_key_bin = 0xe0 + i
            inmod_key = inmod_key_bin.to_bytes(1, byteorder="big").hex()
            if inmod_key in keytbl.keys():
                conv_key = keytbl[inmod_key]
                #if converted keycode is "00", ignore this input key
                if(conv_key=="00"):
                    continue
                #if converted keycode is a modifier key(starts with "e"), set corresponding bit of output modifier keycode (outmod)
                if(conv_key[0]=="e"):
                    mod_shift_num=int(conv_key[1])
                    outmod = outmod | (1 << mod_shift_num)
                #if converted keycode is NOT a modifier key, add the conveted keycode to out_keys list and increment out_key_count
                else:
                    out_keys.append(int(conv_key,16))
                    out_key_count+=1
            else:
                outmod = outmod | inmod & 1 << i
    in_key_count=3 # "in_key_count=0" is connection info, "in_key_count=1" is modifier key, "in_key_count=2" is reserved, so set 3
    for i in range(max_key_num):
        inkey = input[in_key_count*3+1:in_key_count*3+3]
        in_key_count+=1
        if(out_key_count>max_key_num-1):
            break
        if inkey in keytbl.keys():
            conv_key = keytbl[inkey]
            #if converted keycode is "00", ignore this input key
            if(conv_key=="00"):
                continue
            #if converted keycode is a modifier key(starts with "e"), set corresponding bit of output modifier keycode (outmod)
            if(conv_key[0]=="e"):
                mod_shift_num=int(conv_key[1])
                outmod = outmod + 1 << mod_shift_num
            #if converted keycode is NOT a modifier key, add the conveted keycode to out_keys list and increment out_key_count
            else:
                out_keys.append(int(conv_key,16))
                out_key_count+=1
        else:
            out_keys.append(int(inkey,16))
            out_key_count+=1
    check_sum = int(r1,16) + outmod + int(input[-2:],16) # add "connection info" and "output modifier key" and "sequence number"
    key_str=""
    out_keys_len=len(out_keys)
    for i in range(max_key_num):
        if(i>=out_keys_len):
            out_keys.append(0)
            out_key_count+=1
        check_sum = check_sum + out_keys[i]
        key_str = key_str +" "+ out_keys[i].to_bytes(1,byteorder="big").hex()
    result= " "+ r1 +" "+ outmod.to_bytes(1,byteorder="big").hex() +" 00"+ key_str +" "+input[-2:] +" "+ (check_sum & 0xff).to_bytes(1,byteorder="big").hex()
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
                    if(r3[0]=="1"): #keyboard
                        string="57 ab "+r+" "+r2.hex()+" "+r3+ convkeys(r4) #Call Keycode converter function
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
