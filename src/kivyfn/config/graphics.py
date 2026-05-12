from __future__ import annotations
from typing import Literal
from dataclasses import dataclass

from kivy.config import Config

FullScreenMode = Literal[
    False,
    True,
    "auto",
    "fake",
]

WindowPosition = Literal[
    "auto",
    "custom",
]

VSyncMode = Literal[
    -1,
    0,
    1,
]


WindowState = Literal[
    "visible",
    "hidden",
    "maximized",
    "minimized",
]


@dataclass(slots=True)
class FnGraphicsConfig:
    width: int = 1280
    """
    Window width in pixels.
    """

    height: int = 720
    """
    Window height in pixels.
    """

    resizable: bool = True
    """
    Allow the user to resize the window.
    """

    fullscreen: FullScreenMode = False
    """
    Start the window in fullscreen mode.

    Supported values:
    - False
    - True
    - "auto"
    - "fake"
    """

    borderless: bool = False
    """
    Remove the OS window borders and titlebar.
    """

    position: WindowPosition = "auto"
    """
    Window position mode.

    Supported values:
    - "auto"
    - "custom"
    """

    top: int = 0
    """
    Window top position when using custom positioning.
    """

    left: int = 0
    """
    Window left position when using custom positioning.
    """

    show_cursor: bool = True
    """
    Show the mouse cursor.
    """

    maxfps: int = 60
    """
    Maximum frames per second.
    """

    vsync: VSyncMode = 1
    """
    Vertical sync mode.

    Supported values:
    - 0: disabled
    - 1: enabled
    - -1: adaptive
    """

    window_state: WindowState = "visible"
    """
    Initial window state.

    Supported values:
    - "visible"
    - "hidden"
    - "maximized"
    - "minimized"
    """

    always_on_top: bool = False
    """
    Keep the window above other windows.
    """

    minimum_width: int = 0
    """
    Minimum allowed window width.
    """

    minimum_height: int = 0
    """
    Minimum allowed window height.
    """

    allow_screensaver: bool = True
    """
    Allow the system screensaver or sleep mode.
    """

    def apply(self) -> None:
        Config.set("graphics", "width", str(self.width))
        Config.set("graphics", "height", str(self.height))
        Config.set("graphics", "resizable", str(int(self.resizable)))
        Config.set("graphics", "fullscreen", str(self.fullscreen))
        Config.set("graphics", "borderless", str(int(self.borderless)))
        Config.set("graphics", "position", self.position)
        Config.set("graphics", "top", str(self.top))
        Config.set("graphics", "left", str(self.left))
        Config.set("graphics", "show_cursor", str(int(self.show_cursor)))
        Config.set("graphics", "maxfps", str(self.maxfps))
        Config.set("graphics", "vsync", str(self.vsync))
        Config.set("graphics", "window_state", self.window_state)
        Config.set("graphics", "always_on_top", str(int(self.always_on_top)))
        Config.set("graphics", "minimum_width", str(self.minimum_width))
        Config.set("graphics", "minimum_height", str(self.minimum_height))
        Config.set("graphics", "allow_screensaver", str(int(self.allow_screensaver)))
