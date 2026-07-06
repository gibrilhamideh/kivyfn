# kivyfn/ui/fields/base.py
from __future__ import annotations

from typing import Any

from kivy.clock import Clock
from kivy.metrics import dp
from kivy.properties import (
    AliasProperty,
    BooleanProperty,
    NumericProperty,
    ObjectProperty,
    OptionProperty,
)
from kivy.uix.textinput import TextInput

from kivyfn.ui.fields.event import InputEvent
from kivyfn.ui.widget import FnWidget


class FnBaseField(FnWidget, TextInput):
    invalid = BooleanProperty(False)
    revert_on_invalid_text = BooleanProperty(True)
    revert_on_invalid_value = BooleanProperty(True)

    default: Any = ObjectProperty(None, allownone=True)
    formatter = ObjectProperty(None, allownone=True)
    clear_on_focus = BooleanProperty(False)

    # ---------------------------------------------------------
    # Text layout
    # ---------------------------------------------------------
    valign_offset = NumericProperty(dp(0))

    valign = OptionProperty(
        None,
        options=(None, "top", "center", "bottom"),
        allownone=True,
    )


    _value = ObjectProperty(None, allownone=True)
    _cached_text = ObjectProperty("", allownone=True)

    __events__ = ("on_commit",)

    def __init__(self, **kwargs: Any) -> None:
        super().__init__(**kwargs)

        self.bind(
            height=self._trigger_valign_update,
            text=self._trigger_valign_update,
            font_size=self._trigger_valign_update,
            line_height=self._trigger_valign_update,
            multiline=self._trigger_valign_update,
            valign=self._trigger_valign_update,
            valign_offset=self._trigger_valign_update,
        )

        self._trigger_valign_update()

    def on_kv_post(self, base_widget) -> None:
        super().on_kv_post(base_widget)
        self._set_initial_value()

    # ---------------------------------------------------------
    # Default
    # ---------------------------------------------------------
    def _set_initial_value(self) -> None:
        if self.value is None:
            self.value = self.default

    # ---------------------------------------------------------
    # Padding aliases
    # ---------------------------------------------------------
    def _get_padding_left(self) -> float:
        return float(self.padding[0])

    def _set_padding_left(self, value: float) -> None:
        self.padding[0] = value

    padding_left = AliasProperty(
        _get_padding_left,
        _set_padding_left,
        bind=("padding",),
    )

    def _get_padding_top(self) -> float:
        return float(self.padding[1])

    def _set_padding_top(self, value: float) -> None:
        self.padding[1] = value

    padding_top = AliasProperty(
        _get_padding_top,
        _set_padding_top,
        bind=("padding",),
    )

    def _get_padding_right(self) -> float:
        return float(self.padding[2])

    def _set_padding_right(self, value: float) -> None:
        self.padding[2] = value

    padding_right = AliasProperty(
        _get_padding_right,
        _set_padding_right,
        bind=("padding",),
    )

    def _get_padding_bottom(self) -> float:
        return float(self.padding[3])

    def _set_padding_bottom(self, value: float) -> None:
        self.padding[3] = value

    padding_bottom = AliasProperty(
        _get_padding_bottom,
        _set_padding_bottom,
        bind=("padding",),
    )

    # ---------------------------------------------------------
    # Value API
    # ---------------------------------------------------------
    def _get_value(self) -> Any:
        return self._value

    def _set_value(self, value: Any) -> bool:
        if not self.validate_value(value):
            return False

        text = self.value_to_text(value)

        self._value = value
        self.text = text
        return True

    def _alias_get(self) -> Any:
        return self._get_value()

    def _alias_set(self, value: Any) -> bool:
        return self._set_value(value)

    value = AliasProperty(
        _alias_get,
        _alias_set,
    )

    # ---------------------------------------------------------
    # Validation and normalization
    # ---------------------------------------------------------
    def validate_value(self, value: Any) -> bool:
        return True

    def validate_beforeinput(self, event: InputEvent) -> bool:
        return True

    def value_to_text(self, value: Any) -> str:
        return "" if value is None else str(value)

    def text_to_value(self) -> Any:
        return self.text

    # ---------------------------------------------------------
    # Input Events
    # ---------------------------------------------------------
    def on_commit(self, value: Any) -> None:
        pass

    # ---------------------------------------------------------
    # Vertical alignment
    # ---------------------------------------------------------
    def _trigger_valign_update(self, *args: Any) -> None:
        Clock.schedule_once(self._update_valign, 0)

    def _get_text_content_height(self) -> float:
        if not self.multiline:
            return float(self.line_height)

        lines = getattr(self, "_lines", None)

        if lines:
            line_count = len(lines)
        else:
            line_count = max(1, len(self.text.splitlines()) or 1)

        return float(line_count * self.line_height)

    def _update_valign(self, *args: Any) -> None:
        if self.valign is None:
            return

        content_height = self._get_text_content_height()

        extra_space = max(
            0,
            self.height - content_height - (self.valign_offset * 2),
        )

        if self.valign == "top":
            top_offset = 0
        elif self.valign == "bottom":
            top_offset = extra_space
        else:
            top_offset = extra_space / 2

        self.padding_top = self.valign_offset + top_offset
        self.padding_bottom = (
            self.valign_offset
            + extra_space
            - top_offset
        )

    # ---------------------------------------------------------
    # Helpers for subclasses
    # ---------------------------------------------------------
    def _dispatch_commit(self) -> None:
        self.dispatch("on_commit", self.value)

    def _cache_current_state(self) -> None:
        self._cached_text = self.text

    def _restore_cached_state(self) -> None:
        self.text = self._cached_text

    def _clear_on_focus(self):
        if not self.clear_on_focus:
            return

        self.text = ""

    # ---------------------------------------------------------
    # Focus Handling
    # ---------------------------------------------------------
    def _on_textinput_focused(self, instance: Any, value: bool, *largs: Any) -> None:
        super()._on_textinput_focused(instance, value, *largs)

        focused = value
        if focused:
            self._cache_current_state()
            self._clear_on_focus()
            return

        if self.invalid:
            if self.revert_on_invalid_text:
                self._restore_cached_state()
            return

        field_value = self.text_to_value()

        if field_value is None:
            field_value = self.default

        if not self.validate_value(field_value):
            if self.revert_on_invalid_value:
                self._restore_cached_state()
            return

        self.value = field_value
        self._dispatch_commit()
