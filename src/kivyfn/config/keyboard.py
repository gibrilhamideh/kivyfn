from __future__ import annotations
from typing import Literal
from dataclasses import dataclass

from kivy.config import Config

KeyboardMode = Literal[
    "",
    "system",
    "dock",
    "multi",
    "systemanddock",
    "systemandmulti",
]
"""
Keyboard input mode.
"""

@dataclass(slots=True)
class FnKeyboardConfig:
    mode: KeyboardMode = "system"
    """
    Keyboard mode.

    Supported values:
    - ""
    - "system"
    - "dock"
    - "multi"
    - "systemanddock"
    - "systemandmulti"
    """

    layout: str = "qwerty"
    """
    Keyboard layout identifier.
    """

    def apply(self) -> None:
        Config.set("kivy", "keyboard_mode", self.mode)
        Config.set("kivy", "keyboard_layout", self.layout)
