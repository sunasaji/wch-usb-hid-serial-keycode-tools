"""Keyboard layouts loaded from YAML files.

Built-in layouts live as YAML files in the ``layouts/`` directory next to this
module. A layout file lists only the characters that differ from the base US
map (:data:`wch_hid_serial.hid.keys.US_CHAR_MAP`); :func:`build_char_map`
merges the base with a layout's overrides.

To add your own layout without touching any Python, drop ``<name>.yaml`` into
a directory and point the ``WCH_HID_LAYOUTS_DIR`` environment variable at it
(or pass ``layouts_dir=`` to the layout functions). User directories are
searched before the built-in layouts.

YAML format::

    overrides:
      '"': [shift, 0x1f]
      '@': [none, 0x2f]

Modifiers may be ``none``, a name (``shift``), or a ``+``-joined combo
(``shift+ralt``). Keycodes may be hex (``0x1f``) or decimal.
"""

import os
from importlib.resources import files
from pathlib import Path

import yaml

from .modifiers import parse_modifiers

#: Environment variable naming an extra directory of ``<name>.yaml`` layouts.
ENV_LAYOUTS_DIR = "WCH_HID_LAYOUTS_DIR"


def _keycode(value):
    if isinstance(value, int):
        return value
    value = str(value)
    return int(value, 16) if value.lower().startswith("0x") else int(value)


def _parse_overrides(data):
    overrides = (data or {}).get("overrides") or {}
    result = {}
    for char, mapping in overrides.items():
        result[str(char)] = (parse_modifiers(str(mapping[0])), _keycode(mapping[1]))
    return result


def load_layout_yaml(path):
    """Load a layout's ``{char: (modifier, keycode)}`` overrides from a file."""
    with open(path, encoding="utf-8") as f:
        return _parse_overrides(yaml.safe_load(f))


def _builtin_dir():
    return files("wch_hid_serial.hid").joinpath("layouts")


def _user_dirs(layouts_dir=None):
    dirs = []
    if layouts_dir:
        dirs.append(Path(layouts_dir))
    env = os.environ.get(ENV_LAYOUTS_DIR)
    if env:
        dirs.append(Path(env))
    return dirs


def get_overrides(name, layouts_dir=None):
    """Return the override map for layout ``name``.

    User directories (``layouts_dir`` then ``$WCH_HID_LAYOUTS_DIR``) are
    searched before the built-in layouts. Raises ``ValueError`` if not found.
    """
    for directory in _user_dirs(layouts_dir):
        path = directory / (name + ".yaml")
        if path.is_file():
            return load_layout_yaml(path)
    resource = _builtin_dir().joinpath(name + ".yaml")
    if resource.is_file():
        return _parse_overrides(yaml.safe_load(resource.read_text(encoding="utf-8")))
    raise ValueError("unknown layout: %r" % (name,))


def available_layouts(layouts_dir=None):
    """Return the sorted layout names available (built-in plus user dirs)."""
    names = set()
    for entry in _builtin_dir().iterdir():
        if entry.name.endswith(".yaml"):
            names.add(entry.name[:-5])
    for directory in _user_dirs(layouts_dir):
        if directory.is_dir():
            for path in directory.glob("*.yaml"):
                names.add(path.stem)
    return sorted(names)
