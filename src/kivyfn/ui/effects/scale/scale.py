from __future__ import annotations

from typing import Literal

from kivy.animation import Animation
from kivy.properties import NumericProperty, OptionProperty

from kivyfn.ui.behaviors.transform.scale import FnScaleBehavior
from kivyfn.ui.effects.types import Effect_Types


ScaleAxis = Literal["x", "y", "xy"]

ScaleTransition = Literal[
    "linear",
    "in_quad",
    "out_quad",
    "in_out_quad",
    "out_back",
    "out_elastic",
]


class FnScaleEffect(FnScaleBehavior):
    """
    Generic current-value-to-target scale effect.

    Useful for dialogs, cards, menus, popups, and overlay enter/exit
    transitions.

    This is different from spring:
    - spring = press feedback
    - scale = direct scale transition
    """

    scale_axis: ScaleAxis = OptionProperty(
        "xy",
        options=["x", "y", "xy"],
    )

    scale_target = NumericProperty(1.0)
    scale_duration = NumericProperty(0.12)

    scale_transition: ScaleTransition = OptionProperty(
        "out_quad",
        options=[
            "linear",
            "in_quad",
            "out_quad",
            "in_out_quad",
            "out_back",
            "out_elastic",
        ],
    )

    __events__ = (
        "on_effect_start",
        "on_effect_transition",
        "on_effect_done",
    )

    def scale_to(self, target: float | None = None) -> None:
        Animation.cancel_all(self, "scale_x", "scale_y")

        if target is None:
            target = self.scale_target

        self.dispatch("on_effect_start", "scale")  # pyright: ignore

        kwargs = {
            "d": self.scale_duration,
            "t": self.scale_transition,
        }

        if self.scale_axis in ("x", "xy"):
            kwargs["scale_x"] = target

        if self.scale_axis in ("y", "xy"):
            kwargs["scale_y"] = target

        animation = Animation(**kwargs)
        animation.bind(on_complete=self._on_scale_complete)
        animation.start(self)

    def scale_in(self) -> None:
        self.scale_to(1.0)

    def scale_out(self) -> None:
        self.scale_to(0.0)

    def _on_scale_complete(self, *_args) -> None:
        self.dispatch("on_effect_done", "scale")  # pyright: ignore

    def on_effect_start(self, effect_name: Effect_Types) -> None:
        pass

    def on_effect_transition(self, effect_name: Effect_Types) -> None:
        pass

    def on_effect_done(self, effect_name: Effect_Types) -> None:
        pass
