
from __future__ import annotations

from time import monotonic
from typing import Any, Literal

from kivy.clock import Clock, ClockEvent
from kivy.properties import (
    BooleanProperty,
    NumericProperty,
    OptionProperty,
)
from kivy.vector import Vector


TouchMode = Literal["push", "toggle"]


class FnTouch:
    """
    Provide exclusive tap, long-press, and double-press gestures.

    A completed long press suppresses ``on_release``. Double-press
    detection is opt-in because confirming a single release must wait for
    ``double_press_time``. When a double press is confirmed, both normal
    release events are suppressed.

    Physical release always clears the visual push state, even when the
    normal release event is suppressed.
    """

    touch_mode: TouchMode = OptionProperty(
        "push",
        options=("push", "toggle"),
    )

    pressed: bool = BooleanProperty(False)
    disabled: bool = BooleanProperty(False)

    long_press_enabled: bool = BooleanProperty(True)
    double_press_enabled: bool = BooleanProperty(False)

    long_press_time: float = NumericProperty(0.5)
    double_press_time: float = NumericProperty(0.25)
    touch_slop: float = NumericProperty(10)

    __events__ = (
        "on_press",
        "on_release",
        "on_cancel",
        "on_long_press",
        "on_double_press",
    )

    def __init__(self, **kwargs: Any) -> None:
        super().__init__(**kwargs)

        self._active_touches: set[Any] = set()
        self._cancelled_touches: set[Any] = set()

        self._long_press_event: ClockEvent | None = None
        self._long_press_triggered = False

        self._pending_release_event: ClockEvent | None = None
        self._pending_release_touch: Any | None = None
        self._last_release_time: float | None = None

    # =================================== #
    # Touch handling
    # =================================== #

    def on_touch_down(self, touch: Any) -> bool:
        if self.disabled or not getattr(self, "display", True):
            return super().on_touch_down(touch)  # pyright: ignore

        if getattr(touch, "is_mouse_scrolling", False):
            return super().on_touch_down(touch)  # pyright: ignore

        if not self.collide_point(*touch.pos):  # pyright: ignore
            return super().on_touch_down(touch)  # pyright: ignore

        if super().on_touch_down(touch):  # pyright: ignore
            return True

        if self in touch.ud:
            return super().on_touch_down(touch)  # pyright: ignore

        touch.grab(self)
        touch.ud[self] = {
            "start_pos": touch.pos,
        }

        is_first_touch = not self._active_touches
        self._active_touches.add(touch)

        if is_first_touch:
            self._long_press_triggered = False
            self._expire_pending_release()
            self._do_press(touch)
            self.dispatch("on_press", touch)  # pyright: ignore
            self._start_long_press_timer(touch)

        return True

    def on_touch_move(self, touch: Any) -> bool:
        if touch.grab_current is not self:
            return super().on_touch_move(touch)  # pyright: ignore

        data = touch.ud.get(self)

        if data is not None:
            start_pos = data["start_pos"]
            distance = Vector(touch.pos).distance(start_pos)

            if distance > self.touch_slop:
                self._cancel_long_press_timer()

        if not self.collide_point(*touch.pos):  # pyright: ignore
            self._cancel_touch(touch)

        return True

    def on_touch_up(self, touch: Any) -> bool:
        if touch.grab_current is not self:
            return super().on_touch_up(touch)  # pyright: ignore

        touch.ungrab(self)
        self._cancel_long_press_timer()

        self._active_touches.discard(touch)

        cancelled = touch in self._cancelled_touches
        self._cancelled_touches.discard(touch)

        if cancelled or self._active_touches:
            return True

        self._reset_push_state()

        if self._long_press_triggered:
            self._long_press_triggered = False
            return True

        self._handle_release(touch)
        return True

    def _cancel_touch(self, touch: Any) -> None:
        if touch in self._cancelled_touches:
            return

        self._cancel_long_press_timer()
        self._cancelled_touches.add(touch)
        self._active_touches.discard(touch)

        if self._active_touches:
            return

        self._long_press_triggered = False
        self._do_cancel(touch)
        self.dispatch("on_cancel", touch)  # pyright: ignore

    # =================================== #
    # Long press
    # =================================== #

    def _start_long_press_timer(self, touch: Any) -> None:
        self._cancel_long_press_timer()

        if not self.long_press_enabled:
            return

        self._long_press_event = Clock.schedule_once(
            lambda dt: self._trigger_long_press(dt, touch),
            self.long_press_time,
        )

    def _trigger_long_press(self, _dt: float, touch: Any) -> None:
        self._long_press_event = None

        if (
            touch not in self._active_touches
            or touch in self._cancelled_touches
        ):
            return

        self._flush_pending_release()
        self._long_press_triggered = True
        self.dispatch("on_long_press", touch)  # pyright: ignore

    def _cancel_long_press_timer(self) -> None:
        if self._long_press_event is None:
            return

        self._long_press_event.cancel()
        self._long_press_event = None

    # =================================== #
    # Release and double press
    # =================================== #

    def _handle_release(self, touch: Any) -> None:
        if (
            not self.double_press_enabled
            or self.double_press_time <= 0
        ):
            self._dispatch_release(touch)
            return

        now = monotonic()
        elapsed = (
            None
            if self._last_release_time is None
            else now - self._last_release_time
        )

        if (
            self._pending_release_event is not None
            and elapsed is not None
            and elapsed <= self.double_press_time
        ):
            self._cancel_pending_release()
            self.dispatch("on_double_press", touch)  # pyright: ignore
            return

        self._flush_pending_release()
        self._last_release_time = now
        self._pending_release_touch = touch
        self._pending_release_event = Clock.schedule_once(
            self._dispatch_pending_release,
            self.double_press_time,
        )

    def _dispatch_pending_release(self, _dt: float) -> None:
        touch = self._pending_release_touch

        self._pending_release_event = None
        self._pending_release_touch = None
        self._last_release_time = None

        if touch is not None:
            self._dispatch_release(touch)

    def _dispatch_release(self, touch: Any) -> None:
        self._do_release(touch)
        self.dispatch("on_release", touch)  # pyright: ignore

    def _expire_pending_release(self) -> None:
        if (
            self._pending_release_event is None
            or self._last_release_time is None
        ):
            return

        if monotonic() - self._last_release_time > self.double_press_time:
            self._flush_pending_release()

    def _flush_pending_release(self) -> None:
        touch = self._pending_release_touch

        if self._pending_release_event is not None:
            self._pending_release_event.cancel()

        self._pending_release_event = None
        self._pending_release_touch = None
        self._last_release_time = None

        if touch is not None:
            self._dispatch_release(touch)

    def _cancel_pending_release(self) -> None:
        if self._pending_release_event is not None:
            self._pending_release_event.cancel()

        self._pending_release_event = None
        self._pending_release_touch = None
        self._last_release_time = None

    # =================================== #
    # Internal hooks
    # =================================== #

    def _do_press(self, _touch: Any) -> None:
        if self.touch_mode == "push":
            self.pressed = True

    def _reset_push_state(self) -> None:
        if self.touch_mode == "push":
            self.pressed = False

    def _do_release(self, _touch: Any) -> None:
        if self.touch_mode == "push":
            self.pressed = False
        elif self.touch_mode == "toggle":
            self.pressed = not self.pressed

    def _do_cancel(self, _touch: Any) -> None:
        if self.touch_mode == "push":
            self.pressed = False

    # =================================== #
    # Events
    # =================================== #

    def on_press(self, _touch: Any) -> None:
        pass

    def on_release(self, _touch: Any) -> None:
        pass

    def on_cancel(self, _touch: Any) -> None:
        pass

    def on_long_press(self, _touch: Any) -> None:
        pass

    def on_double_press(self, _touch: Any) -> None:
        pass

