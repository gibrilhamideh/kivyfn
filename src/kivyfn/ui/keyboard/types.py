from __future__ import annotations

from collections.abc import Sequence
from typing import Literal, TypeAlias


FnKeycode: TypeAlias = str | None
"""
Key identifier understood by Kivy's keyboard event adapter.

Use ``None`` when text should determine the keycode.
"""


FnKeyboardModifier = Literal[
    "alt",
    "capslock",
    "ctrl",
    "meta",
    "numlock",
    "scrolllock",
    "shift",
]
"""
Modifier names emitted by Kivy keyboard events.
"""


FnKeyboardModifiers: TypeAlias = Sequence[FnKeyboardModifier]
"""
Sequence of active keyboard modifiers.
"""
