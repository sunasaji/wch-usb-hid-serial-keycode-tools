import pytest

from wch_hid_serial.hid import (
    available_layouts,
    build_char_map,
    char_to_hid,
    get_layout,
    load_layout_yaml,
    register_layout,
    set_layout,
)


@pytest.fixture(autouse=True)
def _reset_layout():
    yield
    set_layout("us104")  # keep global layout state isolated between tests


def test_available_layouts():
    assert {"us104", "jp106", "uk105", "de105", "fr105"} <= set(available_layouts())


def test_set_and_get_layout():
    assert set_layout("jp106") == "jp106"
    assert get_layout() == "jp106"
    assert char_to_hid("@") == (0x00, 0x2F)  # '@' is unshifted on JIS
    assert char_to_hid('"') == (0x02, 0x1F)


def test_build_char_map_does_not_change_active():
    set_layout("us104")
    jp = build_char_map("jp106")
    assert jp["@"] == (0x00, 0x2F)
    assert jp["a"] == (0x00, 0x04)  # base letters unchanged
    assert char_to_hid("@") == (0x02, 0x1F)  # active layout still US


def test_unknown_layout_raises():
    with pytest.raises(ValueError):
        build_char_map("zz999")


def test_register_layout():
    register_layout("custom", {"@": (0x00, 0x99)})
    assert build_char_map("custom")["@"] == (0x00, 0x99)


def test_load_layout_yaml(tmp_path):
    path = tmp_path / "layout.yaml"
    path.write_text("overrides:\n  '@': [none, 0x2f]\n  '\"': [shift, 0x1f]\n")
    assert load_layout_yaml(str(path)) == {"@": (0x00, 0x2F), '"': (0x02, 0x1F)}


def test_layouts_dir_discovery(tmp_path):
    # A YAML file in a user directory is discovered without any code change.
    (tmp_path / "myiso.yaml").write_text("overrides:\n  '@': [ralt, 0x1f]\n")
    assert "myiso" in available_layouts(layouts_dir=str(tmp_path))
    set_layout("myiso", layouts_dir=str(tmp_path))
    assert char_to_hid("@") == (0x40, 0x1F)  # AltGr+2
