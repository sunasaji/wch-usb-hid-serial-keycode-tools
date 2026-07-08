"""Key names, the US character map, keyboard layouts and key resolution.

This adds named special keys (``enter``, ``f1``, ``up``…), a character ->
``(modifier, keycode)`` map with pluggable layouts, a high-level
:func:`resolve_key`, and :func:`validate_chars`. Keycodes follow the USB HID
Usage Tables. Layout data matches the serial-hid-kvm definitions.
"""

from . import layouts as _layouts
from .modifiers import MOD_LSHIFT, MOD_NONE, parse_modifiers

# Special (non-character) key name -> HID keycode.
SPECIAL_KEYS = {
    "enter": 0x28, "return": 0x28,
    "escape": 0x29, "esc": 0x29,
    "backspace": 0x2A,
    "tab": 0x2B,
    "space": 0x2C,
    "capslock": 0x39,
    "f1": 0x3A, "f2": 0x3B, "f3": 0x3C, "f4": 0x3D, "f5": 0x3E, "f6": 0x3F,
    "f7": 0x40, "f8": 0x41, "f9": 0x42, "f10": 0x43, "f11": 0x44, "f12": 0x45,
    "printscreen": 0x46, "scrolllock": 0x47, "pause": 0x48, "insert": 0x49,
    "home": 0x4A, "pageup": 0x4B, "delete": 0x4C, "end": 0x4D, "pagedown": 0x4E,
    "right": 0x4F, "left": 0x50, "down": 0x51, "up": 0x52, "numlock": 0x53,
}


def _build_us_char_map():
    m = {}
    for i, c in enumerate("abcdefghijklmnopqrstuvwxyz"):
        m[c] = (MOD_NONE, 0x04 + i)
    for i, c in enumerate("ABCDEFGHIJKLMNOPQRSTUVWXYZ"):
        m[c] = (MOD_LSHIFT, 0x04 + i)
    for i, c in enumerate("123456789"):
        m[c] = (MOD_NONE, 0x1E + i)
    m["0"] = (MOD_NONE, 0x27)
    for c, kc in {"!": 0x1E, "@": 0x1F, "#": 0x20, "$": 0x21, "%": 0x22,
                  "^": 0x23, "&": 0x24, "*": 0x25, "(": 0x26, ")": 0x27}.items():
        m[c] = (MOD_LSHIFT, kc)
    for c, kc in {" ": 0x2C, "-": 0x2D, "=": 0x2E, "[": 0x2F, "]": 0x30,
                  "\\": 0x31, ";": 0x33, "'": 0x34, "`": 0x35, ",": 0x36,
                  ".": 0x37, "/": 0x38}.items():
        m[c] = (MOD_NONE, kc)
    for c, kc in {"_": 0x2D, "+": 0x2E, "{": 0x2F, "}": 0x30, "|": 0x31,
                  ":": 0x33, '"': 0x34, "~": 0x35, "<": 0x36, ">": 0x37,
                  "?": 0x38}.items():
        m[c] = (MOD_LSHIFT, kc)
    m["\t"] = (MOD_NONE, 0x2B)
    m["\n"] = (MOD_NONE, 0x28)
    return m


#: Base US (us104) character map: ``char -> (modifier, keycode)``.
US_CHAR_MAP = _build_us_char_map()

# In-memory layouts registered at runtime (name -> override map). These take
# precedence over the YAML files discovered by the layouts module.
_registered = {}
_active_layout = "us104"
_active_char_map = dict(US_CHAR_MAP)


def register_layout(name, overrides):
    """Register (or replace) a layout in memory by its
    ``char -> (modifier, keycode)`` override map (takes precedence over YAML
    files). Use with :func:`load_layout_yaml` for custom YAML layouts."""
    _registered[name] = dict(overrides)


def _overrides_for(name, layouts_dir=None):
    if name in _registered:
        return _registered[name]
    return _layouts.get_overrides(name, layouts_dir=layouts_dir)


def available_layouts(layouts_dir=None):
    """Return the sorted names of the available layouts (registered, YAML
    files in ``layouts_dir`` / ``$WCH_HID_LAYOUTS_DIR``, and the built-ins)."""
    return sorted(set(_registered) | set(_layouts.available_layouts(layouts_dir)))


def build_char_map(name, layouts_dir=None):
    """Build a character map for ``name`` (US base + the layout's overrides)."""
    merged = dict(US_CHAR_MAP)
    merged.update(_overrides_for(name, layouts_dir))
    return merged


def set_layout(name, layouts_dir=None):
    """Activate a layout for :func:`char_to_hid`. Returns the layout name."""
    global _active_char_map, _active_layout
    _active_char_map = build_char_map(name, layouts_dir)
    _active_layout = name
    return name


def get_layout():
    """Return the name of the active layout."""
    return _active_layout


def char_to_hid(char, char_map=None):
    """Return ``(modifier, keycode)`` for a character, or ``None``.

    Uses ``char_map`` if given, otherwise the active layout (default us104).
    """
    return (char_map if char_map is not None else _active_char_map).get(char)


def special_key_to_hid(key_name):
    """Return the HID keycode for a special key name or ``"0x.."`` string.

    Accepts named keys (``"enter"``, ``"f1"``…) and hex keycode strings
    (``"0x2c"``). Returns ``None`` if unknown.
    """
    keycode = SPECIAL_KEYS.get(key_name.lower())
    if keycode is not None:
        return keycode
    lower = key_name.lower()
    if lower.startswith("0x"):
        try:
            value = int(lower, 16)
        except ValueError:
            return None
        if 0x00 <= value <= 0xFF:
            return value
    return None


def resolve_key(key, modifiers=()):
    """Resolve a key + modifiers to ``(modifier_byte, keycode)`` or ``None``.

    ``key`` may be a named special key (``"enter"``), a hex keycode
    (``"0x2c"``), or a single character (mapped via the active layout).
    ``modifiers`` is an iterable of modifier names/ints (or a ``"+"`` combo
    string) that are OR-ed onto any modifier the character itself needs.
    """
    modifier = parse_modifiers(modifiers)
    keycode = special_key_to_hid(key)
    if keycode is not None:
        return (modifier, keycode)
    if len(key) == 1:
        mapping = char_to_hid(key)
        if mapping is not None:
            return (modifier | mapping[0], mapping[1])
    return None


# Characters any layout can produce: ASCII printable + tab + line endings.
_TYPABLE_CHARS = set(chr(c) for c in range(0x20, 0x7F)) | {"\t", "\n", "\r"}


def validate_chars(text):
    """Raise ``ValueError`` if ``text`` has characters that cannot be typed.

    Allows ASCII printable characters plus tab and line endings; rejects
    Unicode and other control characters. A layout may map fewer or more, but
    this catches obviously unsupported input early.
    """
    for ch in text:
        if ch not in _TYPABLE_CHARS:
            raise ValueError(
                "unsupported character: %r (U+%04X); only ASCII printable "
                "characters are supported" % (ch, ord(ch))
            )
