from __future__ import annotations
from typing import Literal

from time import time

from kivy.clock import Clock
from kivy.properties import (
    BooleanProperty,
    NumericProperty,
    OptionProperty,
)
from kivy.vector import Vector


Touch_Mode = Literal["push", "toggle"]

class FnTouch:
    """
    Robust interaction behavior for Kivy widgets.

    Features
    --------
    • Push and Toggle modes
    • Multi-touch tracking
    • Long press detection
    • Double press detection
    • Touch slop handling
    • Cancel detection when leaving widget bounds

    This behavior is intended as a general interaction layer for widgets.
    It does NOT implement visuals.
    """

    touch_mode: Touch_Mode = OptionProperty("push", options=("push", "toggle"))

    pressed = BooleanProperty(False)

    disabled = BooleanProperty(False)

    long_press_time = NumericProperty(0.5)
    double_press_time = NumericProperty(0.25)

    touch_slop = NumericProperty(10)

    # ---------------------------------------------------------------------
    # Initialization
    # ---------------------------------------------------------------------
    __events__ = (
        "on_press",
        "on_release",
        "on_cancel",
        "on_long_press",
        "on_double_press",
    )

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._active_touches = set()
        self._cancelled_touches = set()

        self._long_press_event = None

        self._last_press_time = 0

    # ---------------------------------------------------------------------
    # Touch Handling
    # ---------------------------------------------------------------------

    def on_touch_down(self, touch):
        if self.disabled or not self.display: # pyright: ignore
            return super().on_touch_down(touch) # pyright: ignore

        if getattr(touch, "is_mouse_scrolling", False):
            return super().on_touch_down(touch) # pyright: ignore

        if not self.collide_point(*touch.pos): # pyright: ignore
            return super().on_touch_down(touch) # pyright: ignore

        # NOTE: Need More Testing
        if super().on_touch_down(touch): # pyright: ignore
            return True

        # prevent double handling
        if self in touch.ud:
            return super().on_touch_down(touch) # pyright: ignore

        # grab touch
        touch.grab(self)

        touch.ud[self] = {
            "start_pos": touch.pos,
        }

        is_first_touch = len(self._active_touches) == 0

        self._active_touches.add(touch)

        if is_first_touch:
            self._do_press(touch)

            self.dispatch("on_press", touch) # pyright: ignore

            self._start_long_press_timer(touch)

        return True

    def on_touch_move(self, touch):
        if touch.grab_current is self:
            data = touch.ud.get(self)

            if data:
                start_pos = data["start_pos"]

                if self._long_press_event:
                    if Vector(touch.pos).distance(start_pos) > self.touch_slop:
                        self._cancel_long_press_timer()

            if not self.collide_point(*touch.pos): # pyright: ignore
                if touch not in self._cancelled_touches:
                    self._cancel_long_press_timer()

                    self._cancelled_touches.add(touch)

                    if touch in self._active_touches:
                        self._active_touches.remove(touch)

                    if not self._active_touches:
                        self._do_cancel(touch)

                        self.dispatch("on_cancel", touch) # pyright: ignore

            return True

        return super().on_touch_move(touch) # pyright: ignore

    def on_touch_up(self, touch):
        if touch.grab_current is not self:
            return super().on_touch_up(touch) # pyright: ignore

        touch.ungrab(self)

        self._cancel_long_press_timer()

        if touch in self._active_touches:
            self._active_touches.remove(touch)

        cancelled = touch in self._cancelled_touches

        self._cancelled_touches.discard(touch)

        if not cancelled and not self._active_touches:
            self._do_release(touch)

            self.dispatch("on_release", touch) # pyright: ignore

            self._check_double_press(touch)

        return True

    # ---------------------------------------------------------------------
    # Gesture Detection
    # ---------------------------------------------------------------------

    def _start_long_press_timer(self, touch):
        self._cancel_long_press_timer()

        self._long_press_event = Clock.schedule_once(
            lambda dt: self.dispatch("on_long_press", touch), # pyright: ignore
            self.long_press_time,
        )

    def _cancel_long_press_timer(self):
        if self._long_press_event:
            self._long_press_event.cancel()

            self._long_press_event = None

    def _check_double_press(self, touch):
        now = time()

        if self._last_press_time is not None and (
            now - self._last_press_time <= self.double_press_time
        ):
            self.dispatch("on_double_press", touch) # pyright: ignore
            self._last_press_time = None
        else:
            self._last_press_time = now

    # ---------------------------------------------------------------------
    # Internal Hooks
    # ---------------------------------------------------------------------

    def _do_press(self, touch):
        if self.touch_mode == "push":
            self.pressed = True

    def _do_release(self, touch):
        if self.touch_mode == "push":
            self.pressed = False

        elif self.touch_mode == "toggle":
            self.pressed = not self.pressed

    def _do_cancel(self, touch):
        if self.touch_mode == "push":
            self.pressed = False

    # ---------------------------------------------------------------------
    # Events (override in subclasses)
    # ---------------------------------------------------------------------

    def on_press(self, touch):
        pass

    def on_release(self, touch):
        pass

    def on_cancel(self, touch):
        pass

    def on_long_press(self, touch):
        pass

    def on_double_press(self, touch):
        pass
