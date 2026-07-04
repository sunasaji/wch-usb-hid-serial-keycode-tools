from wch_hid_serial.ch9329 import Ch9329


class FakePort:
    """Serial stand-in that records written packets."""

    def __init__(self):
        self.writes = []

    def write(self, data):
        self.writes.append(bytes(data))


def hx(s):
    return bytes.fromhex(s)


def test_tap_key_press_then_release():
    port = FakePort()
    Ch9329(port).tap_key(0x04, 0x01, release_delay=0)  # Ctrl+a
    assert port.writes == [
        hx("57 ab 00 02 08 01 00 04 00 00 00 00 00 11"),
        hx("57 ab 00 02 08 00 00 00 00 00 00 00 00 0c"),
    ]


def test_mouse_button_state_persists_across_move():
    port = FakePort()
    dev = Ch9329(port)
    dev.mouse_down("left")
    dev.move_mouse(3, 4)   # button still held
    dev.mouse_up("left")
    assert port.writes == [
        hx("57 ab 00 05 05 01 01 00 00 00 0e"),  # down (buttons=1)
        hx("57 ab 00 05 05 01 01 03 04 00 15"),  # move with button held
        hx("57 ab 00 05 05 01 00 00 00 00 0d"),  # up
    ]


def test_click_and_scroll():
    port = FakePort()
    dev = Ch9329(port)
    dev.click("right", press_delay=0)
    dev.scroll(-2)
    assert port.writes == [
        hx("57 ab 00 05 05 01 02 00 00 00 0f"),  # right down
        hx("57 ab 00 05 05 01 00 00 00 00 0d"),  # right up
        hx("57 ab 00 05 05 01 00 00 00 fe 0b"),  # scroll -2 (wheel 0xfe)
    ]


def test_drag_with_screen_scaling():
    port = FakePort()
    Ch9329(port).drag(10, 20, 30, 40, screen=(1920, 1080), delay=0)
    assert port.writes == [
        hx("57 ab 00 04 07 02 00 15 00 4b 00 00 6f"),  # abs move to start (buttons=0)
        hx("57 ab 00 05 05 01 01 00 00 00 0e"),        # left down
        hx("57 ab 00 04 07 02 01 40 00 97 00 00 e7"),  # abs move to end (button held)
        hx("57 ab 00 05 05 01 00 00 00 00 0d"),        # left up
    ]
