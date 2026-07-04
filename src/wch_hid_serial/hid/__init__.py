"""Chip-agnostic USB HID helpers shared across WCH chips."""

from .keycodes import (
    ASCII_TO_KEYCODE,
    SHIFT_FLAG,
    MODIFIER_BASE,
    is_modifier,
    modifier_bit,
    ascii_to_keycode,
)
from .modifiers import (
    MOD_LCTRL,
    MOD_LSHIFT,
    MOD_LALT,
    MOD_LGUI,
    MOD_RCTRL,
    MOD_RSHIFT,
    MOD_RALT,
    MOD_RGUI,
    modifier_name_to_bit,
    modifiers_to_byte,
)

__all__ = [
    "ASCII_TO_KEYCODE",
    "SHIFT_FLAG",
    "MODIFIER_BASE",
    "is_modifier",
    "modifier_bit",
    "ascii_to_keycode",
    "MOD_LCTRL",
    "MOD_LSHIFT",
    "MOD_LALT",
    "MOD_LGUI",
    "MOD_RCTRL",
    "MOD_RSHIFT",
    "MOD_RALT",
    "MOD_RGUI",
    "modifier_name_to_bit",
    "modifiers_to_byte",
]
