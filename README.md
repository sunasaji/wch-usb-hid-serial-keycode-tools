# wch-usb-hid-serial-keycode-tools
Tools and a Python library for WCH USB-HID-over-UART chips:
- **CH9350L** — a bidirectional USB keyboard/mouse to UART bridge. Read, write and convert its HID report frames. ([datasheet](http://www.wch-ic.com/downloads/CH9350DS_PDF.html))
- **CH9329** — a serial-to-USB-HID chip that emulates a USB keyboard/mouse from UART command packets. ([datasheet](https://www.wch.cn/uploads/file/20190508/1557278355473027.pdf))

See the [CH9350L tools](#tools) and the [CH9329](#ch9329) section below.  
This software is not an official product of WCH company.

English | [Japanese](https://github.com/sunasaji/wch-usb-hid-serial-keycode-tools/blob/master/README-ja.md)

# Environment
- Windows11 10.0.25126
- Python 3.11 or later (on Windows)
- pyserial 3.5

On Windows, use Python 3.11 or later. `ch9350-keysender` inserts a short
delay (`time.sleep()`) between HID reports so that the CH9350L does not drop
characters. On Windows, the resolution of `time.sleep()` was limited to the
OS timer tick (about 15.6 ms) up to Python 3.10, which makes such a small
delay far too long and slows the transfer. Python 3.11 uses a high-resolution
waitable timer, so the delay works as intended. (On Linux/macOS, Python 3.10
is fine.)

# Install
```
pip install wch-hid-serial
```
This installs the `ch9350-reader`, `ch9350-proxy`, `ch9350-converter`,
`ch9350-keysender`, `ch9329-keysender` and `ch9329-mouse` commands. To install
from a checkout of this repository instead, run `pip install .` (or
`pip install -e .` for development).

# Library usage
The tools are thin wrappers around the `wch_hid_serial` package, which you can
use from your own code. Each example below shows the code and the output it
produces.

**Convert a keyboard report** — `convert_report()` rewrites the keys in a
CH9350L keyboard report payload with a lookup table and appends a recomputed
checksum.
```python
from wch_hid_serial.ch9350 import convert_report

# Default table: Caps Lock (0x39) -> Left Ctrl (0xe0)
payload = bytes.fromhex("01 00 00 39 00 00 00 00 00 5f")
print(convert_report(payload).hex(" "))
# 01 01 00 00 00 00 00 00 00 5f 61

# Custom table: remap the 'a' key (0x04) to Left Shift (0xe1)
payload = bytes.fromhex("01 00 00 04 00 00 00 00 00 20")
print(convert_report(payload, {0x04: 0xe1}).hex(" "))
# 01 02 00 00 00 00 00 00 00 20 23
```

**Build key reports from text** — `iter_key_reports()` yields `(frame, is_char)`
pairs. An empty report is inserted between two identical keys so they register
separately.
```python
from wch_hid_serial.ch9350 import iter_key_reports

for frame, is_char in iter_key_reports("Hi!"):
    print(frame.hex(" "))
# 57 ab 01 02 00 0b 00 00 00 00 00   (H, with Shift)
# 57 ab 01 00 00 0c 00 00 00 00 00   (i)
# 57 ab 01 02 00 1e 00 00 00 00 00   (!, with Shift)

for frame, is_char in iter_key_reports("aa"):
    print(frame.hex(" "))
# 57 ab 01 00 00 04 00 00 00 00 00   (a)
# 57 ab 01 00 00 00 00 00 00 00 00   (empty, inserted between repeats)
# 57 ab 01 00 00 04 00 00 00 00 00   (a)
```

**Look up HID keycodes** — `ascii_to_keycode()` returns `(shift, keycode)`.
```python
from wch_hid_serial.hid import ascii_to_keycode

print(ascii_to_keycode("A"))     # (True, 4)   Shift + keycode 0x04
print(ascii_to_keycode("a"))     # (False, 4)
print(ascii_to_keycode("\x00"))  # None        (no keycode)
```

**Read frames from a device** — `iter_lower_frames()` reads the lower CH9350L
and yields raw frames. It needs a serial port, so the output depends on your
hardware.
```python
from wch_hid_serial.ch9350 import iter_lower_frames, open_port

for frame in iter_lower_frames(open_port("COM1,115200")):
    print(frame.hex(" "))
# 57 ab 83 0c 12 01 00 00 39 00 00 00 00 00 5f 99   (Caps Lock pressed)
# 57 ab 83 0c 12 01 00 00 8b 00 00 00 00 00 65 f1   (MuHenkan pressed)
```

# Tools

## ch9350-reader.py
This script reads serial data from lower CH9350L and prints each command.  
**Structure chart:**
```mermaid
flowchart LR
usbkm(USB keyboard/mouse)
ch9350l(lower CH9350L)
usb-uart(USB-UART converter)
pc1(PC1_reader)
usbkm --> ch9350l
ch9350l --> usb-uart
usb-uart --> pc1
```

**Usage:** ```ch9350-reader <portname>,<baudrate>```  
**Example command:** ```ch9350-reader COM1,115200```  
**Example output**:  
![ch9350-reader](images/ch9350-reader.gif)

## ch9350-keysender.py
This script reads text input from standard input and sends keycode to upper CH9350L.  
In my environment, I set the CH9350L serial speed to 115200 bps and `--wait-ms 8`.  
I Base64-encoded a binary file to send, which became a 13.3KB string, and pasted
this text data to the standard input.  
The transfer took 120 seconds with no errors.  
The data transfer speed was 6.6KB/min = 111B/s = 889bps.  
A faster transfer may be possible by connecting PIN37 and 38 of the CH9350L to GND
to set the baud rate to 300,000 bps, and by setting `--wait-ms` a little smaller.  
Send data should end with a new line. Otherwise, the last character repeats endlessly.  
**Structure chart:**
```mermaid
flowchart LR
pc1(PC1_keysender)
usb-uart(USB-UART converter)
ch9350l(upper CH9350L)
pc2(PC2)
pc1 --> usb-uart
usb-uart --> ch9350l
ch9350l --> pc2
```

**Usage:** ```ch9350-keysender [--wait-ms <ms>] <portname>,<baudrate>```  
**Example command:** ```ch9350-keysender COM1,115200```  
`--wait-ms` sets the delay between HID reports in milliseconds (default 8).  
**Example input:**  
![ch9350-sender](https://user-images.githubusercontent.com/45969150/174817700-2d087bc6-2717-4e0e-b037-5ccb62bf8391.gif)

ASCII_TO_KEYCODE table in this script is derived from below code:  
https://github.com/adafruit/Adafruit_CircuitPython_HID/blob/main/adafruit_hid/keyboard_layout_us.py

## ch9350-proxy.py
This script reads serial data from lower CH9350L and sends the same data to upper CH9350L.  
**Structure chart:**
```mermaid
flowchart LR
usbkm(USB keyboard/mouse)
ch9350l_L(lower CH9350L)
usb-uart_L(USB-UART converter1)
pc1(PC1_proxy)
usb-uart_U(USB-UART converter2)
ch9350l_U(upper CH9350L)
pc2(PC2)
usbkm <--> ch9350l_L
ch9350l_L <--> usb-uart_L
usb-uart_L <--> pc1
pc1 <--> usb-uart_U
usb-uart_U <--> ch9350l_U
ch9350l_U <--> pc2
```

**Usage:** ```ch9350-proxy <upper_portname>,<upper_baudrate> <lower_portname>,<lower_baudrate>```  
**Example command:** ```ch9350-proxy COM1,115200 COM2,115200```  
**Example communication:** (between two CH9350L chips)  
![ch9350-proxy](images/ch9350-proxy.gif)  
Explanatory notes:  
`L>` indicates data sent from lower CH9350L to PC1  
`L<` indicates data sent to lower CH9350L from PC1  
`U>` indicates data sent from upper CH9350L to PC1  
`U<` indicates data sent to upper CH9350L from PC1  

## ch9350-converter.py
This script reads serial data from lower CH9350L, **converts some key codes by conversion table,** and sends the converted data to upper CH9350L.  
**Structure chart:**
```mermaid
flowchart LR
usbkm(USB keyboard/mouse)
ch9350l_L(lower CH9350L)
usb-uart_L(USB-UART converter1)
pc1(PC1_converter)
usb-uart_U(USB-UART converter2)
ch9350l_U(upper CH9350L)
pc2(PC2)
usbkm <--> ch9350l_L
ch9350l_L <--> usb-uart_L
usb-uart_L <--> pc1
pc1 <--> usb-uart_U
usb-uart_U <--> ch9350l_U
ch9350l_U <--> pc2
```

**Usage:** ```ch9350-converter <upper_portname>,<upper_baudrate> <lower_portname>,<lower_baudrate>```  
**Example command:** ```ch9350-converter COM1,115200 COM2,115200```  
**Default key conversion table** (`DEFAULT_TABLE` in `wch_hid_serial/ch9350/convert.py`):

| Input keycode | Output keycode |
| --- | --- |
| 0x39 (Caps Lock) | 0xe0 (Left Ctrl) |
| 0x8a (Henkan) | 0xe0 (Left Ctrl) |
| 0x8b (MuHenkan) | 0xe2 (Left Alt) |

```
Modifier keys are expressed by codes below in key conversion table:
e0: Left Control
e1: Left Shift
e2: Left Alt
e3: Left GUI
e4: Right Control
e5: Right Shift
e6: Right Alt
e7: Right GUI
```
Other keycodes are listed here: [MightyPork/usb_hid_keys.h](https://gist.github.com/MightyPork/6da26e382a7ad91b5496ee55fdc73db2)

**Example conversion:** (between two CH9350L chips)  
![ch9350-converter](images/ch9350-converter.gif)  
In this case,  
```
L> 57 ab 83 0c 12 01 00 00 39 00 00 00 00 00 5f 99 (00 00 39:Caps Lock) is converted to
U< 57 ab 83 0c 12 01 01 00 00 00 00 00 00 00 5f 61 (01 00 00:Control)
```
```
L> 57 ab 83 0c 12 01 00 00 8b 00 00 00 00 00 65 f1 (00 00 8b:Muhenkan) is converted to
U< 57 ab 83 0c 12 01 04 00 00 00 00 00 00 00 65 6a (04 00 00:Alt)
```
```
L> 57 ab 83 0c 12 01 00 00 8a 00 00 00 00 00 6b f6 (00 00 8a:Henkan) is converted to
U< 57 ab 83 0c 12 01 01 00 00 00 00 00 00 00 6b 6d (01 00 00:Control)
```

# CH9329
The package also supports the **CH9329**, a different WCH chip that receives
UART command packets and *emulates* a USB HID keyboard/mouse. This does the
same job as the **upper** end of a CH9350L: both emulate a USB HID device from
serial and can be used on their own (`ch9350-keysender` drives a CH9350L upper
end by itself). The difference is the interface — the CH9329 uses a high-level
command protocol, while the CH9350L carries near-raw HID report frames. A
CH9329 packet is `57 AB <addr> <cmd> <len> <data...> <sum>`.

**Type text as USB keystrokes** with the `ch9329-keysender` command:  
**Usage:** ```ch9329-keysender [--wait-ms <ms>] <portname>,<baudrate>```  
**Example command:** ```ch9329-keysender COM1,9600```  
It reads text from stdin and types it via the CH9329 (a press and release
report per character). The default baud rate of the CH9329 is 9600.

**Control the mouse** with the `ch9329-mouse` command (one operation per call):  
**Usage:** ```ch9329-mouse <portname>,<baudrate> <operation> ...```  
```
ch9329-mouse COM1,9600 move 100 200 --screen 1920x1080  # absolute (screen px)
ch9329-mouse COM1,9600 move 5 -3 --relative             # relative move
ch9329-mouse COM1,9600 click --button right             # click
ch9329-mouse COM1,9600 down --button left               # press and hold
ch9329-mouse COM1,9600 up --button left                 # release
ch9329-mouse COM1,9600 scroll -2                         # scroll down
ch9329-mouse COM1,9600 drag 100 100 300 300 --screen 1920x1080
```

**Library usage:**
```python
from wch_hid_serial.ch9329 import Ch9329, open_port
from wch_hid_serial.hid import modifier_name_to_bit

dev = Ch9329(open_port("COM1,9600"))
dev.type_text("Hello!\n")                        # type as a USB keyboard
dev.tap_key(0x04, modifier_name_to_bit("ctrl"))  # Ctrl+A (press + release)
dev.click("left")                                # click
dev.move_absolute(960, 540, screen=(1920, 1080)) # move to screen centre
dev.drag(100, 100, 300, 300, screen=(1920, 1080))# drag (button held while moving)
```

The packet builders are pure (no port needed), which makes them easy to test:
```python
from wch_hid_serial.ch9329 import general_packet, relative_packet

print(general_packet(0, [0x04]).hex(" "))  # key 'a'
# 57 ab 00 02 08 00 00 04 00 00 00 00 00 10
print(relative_packet(5, -3).hex(" "))
# 57 ab 00 05 05 01 00 05 fd 00 0f
```
See [examples/ch9329_demo.py](examples/ch9329_demo.py) for a runnable sample.

# Tips
On Cygwin or MSYS terminal, use [winpty](https://github.com/rprichard/winpty) like this: ```winpty ch9350-reader COM1,115200```

# License

## [wch-usb-hid-serial-keycode-tools](https://github.com/sunasaji/wch-usb-hid-serial-keycode-tools)
Copyright (c) 2022 Suna.S  
Released under the MIT License  
https://github.com/sunasaji/wch-usb-hid-serial-keycode-tools/blob/master/LICENSE.txt

## [Adafruit_CircuitPython_HID](https://github.com/adafruit/Adafruit_CircuitPython_HID)
Copyright (c) 2017 Scott Shawcroft for Adafruit Industries  
Released under the MIT License  
https://github.com/adafruit/Adafruit_CircuitPython_HID/blob/main/LICENSE
