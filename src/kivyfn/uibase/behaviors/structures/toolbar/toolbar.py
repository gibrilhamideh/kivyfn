from __future__ import annotations
from typing import Literal

from kivy.metrics import dp
from kivy.animation import Animation
from kivy.uix.relativelayout import RelativeLayout
from kivy.properties import (
    OptionProperty,
    BooleanProperty,
    ObjectProperty,
    NumericProperty,
)


class FnToolbarBehavior:
    """
    toolbar.

    The toolbar controls its own position relative to its parent.
    It can be used inside or outside a FnScaffold.
    """

    position: Literal["top", "bottom"] = OptionProperty(
        "top", options=("top", "bottom")
    )

    open: bool = BooleanProperty(False)
    """
    Whether the toolbar is open.

    When False, the toolbar is positioned outside the parent.
    When True, the toolbar is visible.
    """

    mode: Literal["overlay", "push"] = OptionProperty(
        "overlay", options=("overlay", "push")
    )

    extent: float = NumericProperty(dp(48))

    show_animation: Animation = ObjectProperty(None, allownone=True)
    hide_animation: Animation = ObjectProperty(None, allownone=True)

    parent: RelativeLayout
    height: float
    y: float

    # ----------------------------
    # Lifecycle
    # ----------------------------

    def on_kv_post(self, base_widget):
        self.bind(height=self._update_position)  # pyright: ignore
        self.bind(extent=self.setter("height"))

        if self.parent:
            self.parent.bind(size=self._update_position)  # pyright: ignore

        self._update_position()

        return super().on_kv_post(base_widget)  # pyright: ignore

    # ----------------------------
    # Public API
    # ----------------------------

    def show(self):
        self.open = True

    def hide(self):
        self.open = False

    def toggle(self):
        self.open = not self.open

    # ----------------------------
    # Events
    # ----------------------------
    def on_open(self, *_):
        if self.open:
            self._show()
        else:
            self._hide()

    # ----------------------------
    # Internal
    # ----------------------------
    def _show(self):
        parent = self.parent
        if not parent:
            return

        if self.position == "top":
            target = parent.height - self.height
        else:  # bottom
            target = 0

        if self.show_animation:
            self._cancel_animations()
            self.show_animation.start(self)
        else:
            self.y = target

    def _hide(self):
        parent = self.parent
        if not parent:
            return

        if self.position == "top":
            target = parent.height
        else:  # bottom
            target = -self.height

        if self.hide_animation:
            self._cancel_animations()
            self.hide_animation.start(self)
        else:
            self.y = target

    def _cancel_animations(self):
        if self.show_animation:
            Animation.cancel_all(self.show_animation)

        if self.hide_animation:
            Animation.cancel_all(self.hide_animation)

    def _update_position(self, *_):
        parent = self.parent
        if not parent:
            return

        if self.position == "top":
            self.y = parent.height - self.height if self.open else parent.height

        elif self.position == "bottom":
            self.y = 0 if self.open else -self.height
