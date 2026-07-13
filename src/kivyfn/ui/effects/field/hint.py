# kivyfn/ui/effects/field/hint.py
from __future__ import annotations

from typing import Any, Literal

from kivy.clock import Clock
from kivy.animation import Animation
from kivy.metrics import dp
from kivy.properties import (
    BoundedNumericProperty,
    ColorProperty,
    NumericProperty,
    OptionProperty,
    BooleanProperty,
    AliasProperty,
)

from kivyfn.ui.behaviors.field import (
        FnFieldBorderBehavior,
        FnFieldLayoutBehavior,
)

FieldHintMode = Literal["normal", "filled", "outlined"]


class FnFieldHintEffect(
    FnFieldLayoutBehavior,
    FnFieldBorderBehavior
):
    hint_mode: FieldHintMode = OptionProperty(
        "normal",
        options=["normal", "filled", "outlined"],
    )

    hint_rest_color = ColorProperty([0.5, 0.5, 0.5, 1])
    hint_focus_color = ColorProperty([0.5, 0.5, 0.5, 1])

    hint_rest_scale = NumericProperty(1.0)
    hint_float_scale = NumericProperty(0.86)

    hint_top_offset = NumericProperty(dp(4))
    hint_outline_padding = NumericProperty(dp(8))

    hint_duration = NumericProperty(0.2)
    hint_progress = BoundedNumericProperty(0, min=0, max=1)

    filled_valign_offset = NumericProperty(dp(6))
    normal_valign_offset = NumericProperty(dp(0))
    outlined_valign_offset = NumericProperty(dp(0))

    hint_active = BooleanProperty(False)

    def _get_hint_max_width(self) -> float:
        return max(
            0.0,
            self.width  # pyright: ignore
            - self.padding_left  # pyright: ignore
            - self.padding_right,  # pyright: ignore
        )

    hint_max_width = AliasProperty(
        _get_hint_max_width,
        None,
        bind=(
            "width",
            "padding_left",
            "padding_right",
        ),
    )

    def __init__(self, **kwargs: Any) -> None:
        super().__init__(**kwargs)

        self.effect_trigger = Clock.create_trigger(self._animate_hint, 0)
        self.reset_trigger = Clock.create_trigger(self._reset_hint, 0)

        self.bind(  # pyright: ignore
            text=self._text_active,
            focus=self._text_active,
            hint_size=self.reset_trigger,
            height=self.reset_trigger,
            padding_left=self.reset_trigger,
            hint_mode=self.reset_trigger,
            hint_rest_scale=self.reset_trigger,
            hint_float_scale=self.reset_trigger,
            hint_top_offset=self.reset_trigger,
            hint_outline_padding=self.reset_trigger,
            filled_valign_offset=self.reset_trigger,
            normal_valign_offset=self.reset_trigger,
            outlined_valign_offset=self.reset_trigger,
            hint_rest_color=self._sync_hint_color,
            hint_focus_color=self._sync_hint_color,
        )

    def _text_active(self, *_args: Any) -> None:
        active = bool(self.focus) or bool(self.text)  # pyright: ignore

        if self.hint_active == active:
            self._sync_hint_color()
            return

        self.hint_active = active

    def on_hint_active(self, *_args: Any) -> None:
        self.effect_trigger()

    def on_hint_mode(self, *_args: Any) -> None:
        if self.hint_mode == "filled":
            self.valign = "bottom"  # pyright: ignore
            self.valign_offset = self.filled_valign_offset  # pyright: ignore
        elif self.hint_mode == "outlined":
            self.valign = "center"  # pyright: ignore
            self.valign_offset = self.outlined_valign_offset  # pyright: ignore
        else:
            self.valign = "center"  # pyright: ignore
            self.valign_offset = self.normal_valign_offset  # pyright: ignore

    def _target_hint_scale(self) -> float:
        if self.hint_mode == "normal":
            return self.hint_rest_scale

        return self.hint_float_scale if self.hint_active else self.hint_rest_scale

    def _target_hint_y(self) -> float:
        hint_height = self.hint_scaled_size[1]  # pyright: ignore

        if self.hint_mode == "normal":
            return (self.height - hint_height) / 2  # pyright: ignore

        if self.hint_mode == "filled":
            if self.hint_active:
                return self.height - hint_height - self.hint_top_offset  # pyright: ignore
            return self.filled_valign_offset

        if self.hint_active:
            return self.height - (hint_height / 2)  # pyright: ignore

        return (self.height - hint_height) / 2  # pyright: ignore

    def _target_hint_color(self) -> list[float]:
        if self.hint_mode == "normal" and self.hint_active:
            return [0, 0, 0, 0]

        if self.focus:  # pyright: ignore
            return self.hint_focus_color

        return self.hint_rest_color

    def _target_gap_width(self) -> float:
        if self.hint_mode != "outlined" or not self.hint_active:
            return 0

        return self.hint_scaled_size[0] + (self.hint_outline_padding * 2)  # pyright: ignore

    def _sync_hint_color(self, *_args: Any) -> None:
        self.hint_color = self._target_hint_color()  # pyright: ignore

    def _apply_hint_x_and_gap_x(self) -> None:
        self.hint_x = self.padding_left  # pyright: ignore
        self.border_gap_x = max(0, self.hint_x - self.hint_outline_padding)

    def _set_hint_state(self, *_args: Any) -> None:
        Animation.cancel_all(
            self,
            "hint_y",
            "hint_color",
            "hint_scale",
            "border_gap_width",
        )

        self.hint_scale = self._target_hint_scale()  # pyright: ignore
        self._apply_hint_x_and_gap_x()

        self.hint_y = self._target_hint_y()  # pyright: ignore
        self.hint_color = self._target_hint_color()  # pyright: ignore
        self.border_gap_width = self._target_gap_width()
        self.hint_progress = 1 if self.hint_active else 0

    def _reset_hint(self, *_args: Any) -> None:
        self._set_hint_state()

    def _animate_hint(self, *_args: Any) -> None:
        self._apply_hint_x_and_gap_x()

        target_scale = self._target_hint_scale()

        current_scale = self.hint_scale  # pyright: ignore
        self.hint_scale = target_scale  # pyright: ignore

        target_y = self._target_hint_y()
        target_gap_width = self._target_gap_width()

        self.hint_scale = current_scale  # pyright: ignore

        Animation.cancel_all(
            self,
            "hint_y",
            "hint_color",
            "hint_scale",
            "border_gap_width",
        )

        animation = Animation(
            hint_y=target_y,
            hint_color=self._target_hint_color(),
            hint_scale=target_scale,
            border_gap_width=target_gap_width,
            d=self.hint_duration,
            t="out_quad",
        )

        animation.bind(on_progress=self._on_hint_progress)
        animation.bind(on_complete=self._on_hint_done)
        animation.start(self)

    def _on_hint_progress(
        self,
        _animation: Animation,
        _instance: Any,
        progress: float,
    ) -> None:
        self.hint_progress = progress if self.hint_active else 1 - progress

    def _on_hint_done(self, *_args: Any) -> None:
        self.hint_progress = 1 if self.hint_active else 0
