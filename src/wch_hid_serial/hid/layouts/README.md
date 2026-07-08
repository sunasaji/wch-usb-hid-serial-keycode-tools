# Keyboard layouts

This directory holds the built-in keyboard layouts as YAML files. Each layout
maps **characters** to **physical key presses** (`char_to_hid`, `resolve_key`).
You can add your own layout **without changing any Python** — just drop a
`<name>.yaml` file into a directory (see [How to use](#how-to-use)).

## Overview

The base layout is US ANSI 104-key (`us104`). A layout file only lists the
characters that **differ from US104**. For example, `jp106.yaml` overrides `"`
from Shift+`'` (US) to Shift+`2` (JIS). `build_char_map(name)` merges the base
US map with the layout's overrides.

## File format

A layout file is YAML with a single top-level `overrides` key:

```yaml
# mylayout.yaml - Description of your layout
# Only characters that differ from US104 need to be listed.

overrides:
  'character': [modifier, hid_keycode]
```

Each entry maps a character to a `[modifier, keycode]` pair:

- **character** — the character you want to type (e.g. `'"'`, `'@'`, `'\'`)
- **modifier** — which modifier(s) to hold: `none`, `shift`, `ralt`, `ctrl`,
  or a `+`-joined combo like `shift+ralt`
- **hid_keycode** — the physical key's USB HID keycode, hex (`0x1F`) or decimal

### Modifier names

| Name | Bit | Notes |
|------|-----|-------|
| `none` | 0x00 | No modifier |
| `shift` / `lshift` | 0x02 | Left Shift |
| `rshift` | 0x20 | Right Shift |
| `ctrl` / `lctrl` | 0x01 | Left Control |
| `rctrl` | 0x10 | Right Control |
| `alt` / `lalt` | 0x04 | Left Alt |
| `ralt` / `altgr` | 0x40 | Right Alt (AltGr on ISO keyboards) |
| `win` / `gui` / `super` / `meta` | 0x08 | Left Windows/Command |

Combine with `+`: `shift+ralt`, `ctrl+shift`, etc.

### HID keycodes (physical key positions)

HID keycodes identify **physical key positions**, not the characters printed on
them. Common keycodes:

```
Number row:  `/~=0x35  1=0x1E 2=0x1F 3=0x20 4=0x21 5=0x22 6=0x23 7=0x24
             8=0x25 9=0x26 0=0x27  -/_=0x2D  =/+=0x2E  Backspace=0x2A
QWERTY row:  Tab=0x2B  Q=0x14 W=0x1A E=0x08 R=0x15 T=0x17 Y=0x1C U=0x18
             I=0x0C O=0x12 P=0x13  [/{=0x2F  ]/}=0x30  \/|=0x31
Home row:    CapsLock=0x39  A=0x04 S=0x16 D=0x07 F=0x09 G=0x0A H=0x0B
             J=0x0D K=0x0E L=0x0F  ;/:=0x33  '/"=0x34  Enter=0x28
Bottom row:  Z=0x1D X=0x1B C=0x06 V=0x19 B=0x05 N=0x11 M=0x10
             ,/<=0x36  ./>=0x37  //?=0x38  Space=0x2C
ISO/JIS:     Non-US #~=0x32   Non-US \|=0x64
             International1=0x87 (JIS ろ)   International3=0x89 (JIS ¥|)
```

> The labels show the US characters on each physical key. On your layout the
> same physical key may produce different characters — that is exactly what
> your override file defines.

## US104 base mapping

Characters already correct in US104 need no override. The base map covers:

- `a`-`z` → 0x04-0x1D (no modifier); `A`-`Z` → 0x04-0x1D (shift)
- `0`-`9` → 0x27, 0x1E-0x26 (no modifier); `!@#$%^&*()` → 0x1E-0x27 (shift)
- Punctuation `` ` `` `-` `=` `[` `]` `\` `;` `'` `,` `.` `/` (no modifier)
- Shifted `~` `_` `+` `{` `}` `|` `:` `"` `<` `>` `?` (shift)
- `\n` → Enter, `\t` → Tab, ` ` → Space

## Example

A layout where `@` is typed with `AltGr+2` instead of `Shift+2`:

```yaml
# myiso.yaml
overrides:
  '@': [ralt, 0x1F]    # AltGr+2 produces @
```

## How to use

Save your file as `<name>.yaml`, then load it in one of these ways:

```python
from wch_hid_serial.hid import set_layout, char_to_hid, load_layout_yaml, register_layout

# 1) Point WCH_HID_LAYOUTS_DIR at your directory, or pass layouts_dir=:
set_layout("myiso", layouts_dir="/path/to/layouts")
char_to_hid("@")   # resolved via your layout

# 2) Or load a single file and register it in memory:
register_layout("myiso", load_layout_yaml("/path/to/myiso.yaml"))
set_layout("myiso")
```

User directories (the `layouts_dir` argument, then `$WCH_HID_LAYOUTS_DIR`) are
searched **before** the built-in layouts, so you can also override a built-in.

## Reference: existing layouts

| File | Description | Key differences from US104 |
|------|-------------|----------------------------|
| `us104.yaml` | US ANSI (base) | No overrides (empty) |
| `jp106.yaml` | Japanese JIS | Number-row symbols, `@`/`[`/`]` positions, JIS ろ/¥ keys |
| `uk105.yaml` | UK ISO | `"` and `@` swapped, `#` on Non-US key |
| `de105.yaml` | German QWERTZ | Y/Z swapped, AltGr symbols |
| `fr105.yaml` | French AZERTY | Extensively remapped letters and symbols |

## Asking an AI to create a layout

> Create a `wch_hid_serial` keyboard layout YAML for [name] (e.g. "Spanish ISO",
> "Brazilian ABNT2", "Korean 106").
>
> Format:
> ```yaml
> overrides:
>   'character': [modifier, hid_keycode]
> ```
> - Only list characters that differ from US ANSI 104.
> - `modifier` is one of `none`, `shift`, `ralt`, `ctrl`, `shift+ralt`, etc.
> - `hid_keycode` is the USB HID Usage ID of the physical key position in hex
>   (e.g. `0x1F` for the `2` key).
> - Reference: a=0x04, 1=0x1E, 2=0x1F … 0=0x27, -=0x2D, ==0x2E, [=0x2F, ]=0x30,
>   \=0x31, Non-US#=0x32, ;=0x33, '=0x34, `` ` ``=0x35, ,=0x36, .=0x37, /=0x38,
>   International1=0x87, International3=0x89, Non-US\\|=0x64.
> - See `jp106.yaml` and `uk105.yaml` for examples.
