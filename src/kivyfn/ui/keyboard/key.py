from __future__ import annotations

from dataclasses import dataclass

from .types import (
    FnKeycode,
    FnKeyboardModifier,
    FnKeyboardModifiers,
)


@dataclass(
    frozen=True,
    slots=True,
)
class FnKey:
    """
    Value emitted by a custom virtual keyboard key.

    ``keycode`` identifies control keys such as ``"backspace"`` or
    ``"enter"``. For printable keys, ``text`` contains the text delivered to
    the focused input. Set ``keycode`` to ``None`` to let Kivy derive it from
    ``text``.
    """

    keycode: FnKeycode = None
    text: str = ""
    modifiers: tuple[FnKeyboardModifier, ...] = ()

    @classmethod
    def create(
        cls,
        keycode: FnKeycode = None,
        text: str = "",
        modifiers: FnKeyboardModifiers = (),
    ) -> FnKey:
        """
        Create a key while normalizing modifiers to an immutable tuple.
        """
        return cls(
            keycode=keycode,
            text=text,
            modifiers=tuple(modifiers),
        )

