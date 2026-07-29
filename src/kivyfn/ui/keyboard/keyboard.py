from __future__ import annotations

from collections.abc import Sequence
from typing import Any, cast

from kivy.uix.behaviors import FocusBehavior
from kivy.uix.widget import Widget
from kivy.properties import (
    BooleanProperty,
    ObjectProperty,
    StringProperty,
)

from kivyfn.ui.widget import FnWidget

from .key import FnKey
from .types import (
    FnKeycode,
    FnKeyboardModifier,
)


class FnKeyboard(FnWidget, Widget):
    """
    Base widget for application-defined virtual keyboards.

    Kivy creates this widget when a focusable input requests a virtual
    keyboard. Applications own its keys, layout, styling, sizing, and
    positioning. This class only implements the interface required by Kivy's
    window keyboard adapter.
    """

    target = cast(
        Widget | None,
        ObjectProperty(
            None,
            allownone=True,
        ),
    )
    """
    Widget currently receiving keyboard events.
    """

    callback = cast(
        Any,
        ObjectProperty(
            None,
            allownone=True,
        ),
    )
    """
    Callback supplied by Kivy when the target requests the keyboard.
    """

    docked: bool = BooleanProperty(False)
    """
    Whether Kivy requested a single docked keyboard.
    """

    keyboard_type: str = StringProperty("text")
    """
    Requested application keyboard type.

    Resolution first uses ``target.keyboard_type`` and then falls back to
    Kivy's standard ``target.input_type``.
    """

    __events__ = (
        "on_key_down",
        "on_key_up",
        "on_textinput",
    )

    # =================================== #
    # Target
    # =================================== #
    def on_target(
        self,
        _instance: FnKeyboard,
        target: Widget | None,
    ) -> None:
        """
        Resolve the keyboard presentation requested by the current target.
        """
        if target is None:
            self.keyboard_type = "text"
            return

        keyboard_type = getattr(
            target,
            "keyboard_type",
            "",
        )

        if not keyboard_type:
            keyboard_type = getattr(
                target,
                "input_type",
                "text",
            )

        self.keyboard_type = keyboard_type or "text"

    def on_touch_down(
        self,
        touch: Any,
    ) -> bool:
        """
        Preserve target focus when the virtual keyboard is touched.
        """
        if self.collide_point(
            *touch.pos,
        ):
            ignored_touch = FocusBehavior.ignored_touch

            if touch not in ignored_touch:
                ignored_touch.append(
                    touch,
                )

        return bool(
            super().on_touch_down(
                touch,
            ),
        )

    # =================================== #
    # Presentation
    # =================================== #

    def setup_mode(self, *_args: Any) -> None:
        """
        Configure presentation after Kivy attaches the keyboard to its window.

        Applications can override :meth:`setup_docked` and
        :meth:`setup_free` to implement their own geometry and animations.
        """
        if self.docked:
            self.setup_docked()
        else:
            self.setup_free()

    def setup_docked(self) -> None:
        """
        Configure a shared docked keyboard.
        """

    def setup_free(self) -> None:
        """
        Configure a target-owned keyboard used by multi-keyboard modes.
        """

    def dismiss(self) -> None:
        """
        Release this keyboard through its parent window.
        """
        target = self.target
        window = self.get_parent_window()

        if target is None or window is None:
            return

        window.release_keyboard(
            target,
        )

    # =================================== #
    # Input
    # =================================== #

    def do_key_down(
        self,
        key: FnKey | FnKeycode,
        text: str = "",
        modifiers: Sequence[FnKeyboardModifier] = (),
    ) -> None:
        """
        Emit a key-down event to the focused target.
        """
        resolved = self._resolve_key(
            key,
            text,
            modifiers,
        )

        self.dispatch(
            "on_key_down",
            resolved.keycode,
            resolved.text,
            list(resolved.modifiers),
        )

    def do_key_up(
        self,
        key: FnKey | FnKeycode,
        text: str = "",
        modifiers: Sequence[FnKeyboardModifier] = (),
    ) -> None:
        """
        Emit a key-up event to the focused target.
        """
        resolved = self._resolve_key(
            key,
            text,
            modifiers,
        )

        self.dispatch(
            "on_key_up",
            resolved.keycode,
            resolved.text,
            list(resolved.modifiers),
        )

    def do_key_press(
        self,
        key: FnKey | FnKeycode,
        text: str = "",
        modifiers: Sequence[FnKeyboardModifier] = (),
    ) -> None:
        """
        Emit a complete key press without a held state.
        """
        resolved = self._resolve_key(
            key,
            text,
            modifiers,
        )

        self.do_key_down(
            resolved,
        )

        self.do_key_up(
            resolved,
        )

    def do_textinput(
        self,
        text: str,
    ) -> None:
        """
        Emit composed text directly to the focused target.
        """
        self.dispatch(
            "on_textinput",
            text,
        )

    @staticmethod
    def _resolve_key(
        key: FnKey | FnKeycode,
        text: str,
        modifiers: Sequence[FnKeyboardModifier],
    ) -> FnKey:
        if isinstance(
            key,
            FnKey,
        ):
            return key

        return FnKey.create(
            keycode=key,
            text=text,
            modifiers=modifiers,
        )

    # =================================== #
    # Events
    # =================================== #

    def on_key_down(
        self,
        _keycode: FnKeycode,
        _text: str,
        _modifiers: list[FnKeyboardModifier],
    ) -> None:
        """
        Handle a dispatched key-down event.
        """

    def on_key_up(
        self,
        _keycode: FnKeycode,
        _text: str,
        _modifiers: list[FnKeyboardModifier],
    ) -> None:
        """
        Handle a dispatched key-up event.
        """

    def on_textinput(
        self,
        _text: str,
    ) -> None:
        """
        Handle a dispatched composed-text event.
        """
