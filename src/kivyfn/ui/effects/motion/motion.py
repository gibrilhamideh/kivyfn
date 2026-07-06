from __future__ import annotations

from kivy.animation import Animation
from kivy.properties import BooleanProperty, NumericProperty, StringProperty


class FnMotionEffect:
    move_x = NumericProperty(0.0)
    move_y = NumericProperty(0.0)

    motion_duration = NumericProperty(0.25)
    motion_transition = StringProperty("out_cubic")
    motion_enabled = BooleanProperty(True)

    _motion_x_anim = None
    _motion_y_anim = None

    def on_move_x(self, instance, value: float) -> None:
        if not self.motion_enabled:
            self.x = value
            return

        if self._motion_x_anim is not None:
            self._motion_x_anim.cancel(self)

        self._motion_x_anim = Animation(
            x=value,
            duration=self.motion_duration,
            transition=self.motion_transition,
        )
        self._motion_x_anim.start(self)

    def on_move_y(self, instance, value: float) -> None:
        if not self.motion_enabled:
            self.y = value
            return

        if self._motion_y_anim is not None:
            self._motion_y_anim.cancel(self)

        self._motion_y_anim = Animation(
            y=value,
            duration=self.motion_duration,
            transition=self.motion_transition,
        )
        self._motion_y_anim.start(self)

    def move_to(self, x: float, y: float) -> None:
        self.move_x = x
        self.move_y = y

    def jump_to(self, x: float, y: float) -> None:
        old = self.motion_enabled
        self.motion_enabled = False
        self.move_x = x
        self.move_y = y
        self.motion_enabled = old
