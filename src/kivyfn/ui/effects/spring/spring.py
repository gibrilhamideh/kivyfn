from __future__ import annotations
from typing import Literal

from kivy.animation import Animation
from kivy.properties import NumericProperty, OptionProperty

from kivyfn.ui.behaviors.transform.scale import FnScaleBehavior

from kivyfn.ui.effects.types import Effect_Types

SpringDirection = Literal[
    "inward",
    "outward",
]

SpringMode = Literal[
    "press_release",
    "auto_release",
]

EffectTrigger = Literal[
    "touch",
    "state",
]

SpringInTransition = Literal[
    "linear",
    "in_quad",
    "out_quad",
    "in_out_quad",
    "out_back",
    "out_elastic",
]

SpringOutTransition = Literal[
    "linear",
    "in_quad",
    "out_quad",
    "in_out_quad",
    "out_back",
    "out_elastic",
]

class FnSpringEffect(FnScaleBehavior):
    """
    Spring press animation effect.

    Requires the widget to also inherit from
    `FnTouchBehavior` or another behavior that dispatches:

    - on_press
    - on_release
    - on_cancel
    """

    spring_direction: SpringDirection = OptionProperty(
        "inward",
        options=["inward", "outward"],
    )
    """
    Spring animation direction.

    - ``inward`` compresses the widget when pressed.
    - ``outward`` expands the widget when pressed.

    :attr:`spring_direction` is a
    :class:`~kivy.properties.OptionProperty`
    and defaults to ``"inward"``.
    """

    spring_scale = NumericProperty(0.86)
    """
    Target scale used during the spring animation.

    :attr:`spring_scale` is a
    :class:`~kivy.properties.NumericProperty`
    and defaults to ``0.96``.
    """

    spring_in_duration = NumericProperty(0.08)
    """
    Press animation duration.

    :attr:`spring_in_duration` is a
    :class:`~kivy.properties.NumericProperty`
    and defaults to ``0.08``.
    """

    spring_out_duration = NumericProperty(0.12)
    """
    Release animation duration.

    :attr:`spring_out_duration` is a
    :class:`~kivy.properties.NumericProperty`
    and defaults to ``0.12``.
    """

    spring_in_transition: SpringInTransition = OptionProperty(
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
    """
    Transition used during press animation.
    """

    spring_out_transition: SpringOutTransition = OptionProperty(
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
    """
    Transition used during release animation.
    """


    spring_mode: SpringMode = OptionProperty(
        "press_release",
        options=["press_release", "auto_release"],
    )
    """
    Spring animation mode.

    - ``press_release`` runs the spring in animation
    on press and the spring out animation on
    release or cancel.

    - ``auto_release`` runs the full spring animation
    sequence automatically from a single trigger.

    :attr:`spring_mode` is a
    :class:`~kivy.properties.OptionProperty`
    and defaults to ``"press_release"``.
    """

    effect_trigger: EffectTrigger = OptionProperty(
        "touch",
        options=["touch", "state"],
    )
    """
    Effect trigger source.

    - ``touch`` runs the effect from touch events such as
    press, release, and cancel.

    - ``state`` runs the effect when the widget interaction
    state changes, usually from the ``pressed`` property.

    :attr:`effect_trigger` is a
    :class:`~kivy.properties.OptionProperty`
    and defaults to ``"touch"``.
    """

    # ---------------------------------------------------------------------
    # Internal
    # ---------------------------------------------------------------------
    __events__ = (
        "on_effect_start",
        "on_effect_transition",
        "on_effect_done",
    )


    def spring_in(self) -> None:
        Animation.cancel_all(self, "scale_x", "scale_y")

        self.dispatch("on_effect_start", "spring") #pyright: ignore

        scale = self._get_spring_target_scale()

        animation = Animation(
            scale_x=scale,
            scale_y=scale,
            d=self.spring_in_duration,
            t=self.spring_in_transition,
        )

        animation.bind(on_complete=self._on_spring_in_complete)
        animation.start(self)

    def spring_out(self) -> None:
        Animation.cancel_all(self, "scale_x", "scale_y")

        animation = Animation(
            scale_x=1,
            scale_y=1,
            d=self.spring_out_duration,
            t=self.spring_out_transition,
        )

        animation.bind(on_complete=self._on_spring_out_complete)
        animation.start(self)


    def _on_spring_in_complete(self, *_args) -> None:
        self.dispatch("on_effect_transition", "spring") # pyright: ignore

        if self.spring_mode == "auto_release":
            self.spring_out()

    def _on_spring_out_complete(self, *_args) -> None:
        self.dispatch("on_effect_done", "spring") # pyright: ignore

    def _get_spring_target_scale(self) -> float:
        if self.spring_direction == "inward":
            return self.spring_scale

        return 1 + (1 - self.spring_scale)

    # ---------------------------------------------------------------------
    # Touch Events
    # ---------------------------------------------------------------------
    def on_press(self, touch):
        if self.effect_trigger == "touch":
            self.spring_in()

        return super().on_press(touch)  # pyright: ignore


    def on_release(self, touch):
        if (
            self.effect_trigger == "touch"
            and self.spring_mode == "press_release"
        ):
            self.spring_out()

        return super().on_release(touch)  # pyright: ignore


    def on_cancel(self, touch):
        if self.effect_trigger == "touch":
            self.spring_out()

        return super().on_cancel(touch)  # pyright: ignore


    def on_pressed(self, instance, value: bool) -> None:
        if self.effect_trigger != "state":
            return

        self.spring_in()

    # ---------------------------------------------------------------------
    # Effect Events
    # ---------------------------------------------------------------------
    def on_effect_start(self, effect_name: Effect_Types) -> None:
        pass

    def on_effect_transition(self, effect_name: Effect_Types) -> None:
        pass

    def on_effect_done(self, effect_name: Effect_Types) -> None:
        pass
