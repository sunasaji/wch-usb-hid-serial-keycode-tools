"""Chip-agnostic USB HID helpers shared across WCH chips."""

from .keycodes import (
    ASCII_TO_KEYCODE,
    SHIFT_FLAG,
    MODIFIER_BASE,
    is_modifier,
    modifier_bit,
    ascii_to_keycode,
)

__all__ = [
    "ASCII_TO_KEYCODE",
    "SHIFT_FLAG",
    "MODIFIER_BASE",
    "is_modifier",
    "modifier_bit",
    "ascii_to_keycode",
]
