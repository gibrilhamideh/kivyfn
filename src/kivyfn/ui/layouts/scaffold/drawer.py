from __future__ import annotations
from typing import Literal

from kivy.metrics import dp
from kivy.animation import Animation
from kivy.properties import (
    OptionProperty,
    BooleanProperty,
    ObjectProperty,
    NumericProperty,
)


class FnScaffoldDrawer:
    """
    Sliding drawer panel.

    The drawer controls its own position relative to its parent.
    It can be used inside or outside a FnScaffold.
    """

    position: Literal["left", "right"] = OptionProperty(
        "left", options=("left", "right")
    )

    open: bool = BooleanProperty(False)
    """
    Whether the drawer is open.

    When False, the drawer is positioned outside the parent.
    When True, the drawer is visible.
    """

    mode: Literal["overlay", "push"] = OptionProperty(
        "overlay", options=("overlay", "push")
    )

    extent: float = NumericProperty(dp(280))

    show_animation: Animation = ObjectProperty(None, allownone=True)
    hide_animation: Animation = ObjectProperty(None, allownone=True)


    # ----------------------------
    # Lifecycle
    # ----------------------------
    def on_kv_post(self, base_widget):
        self.bind(width=self._update_position)  # pyright: ignore
        self.bind(extent=self.setter("width"))  # pyright: ignore

        if self.parent: # pyright: ignore
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
        parent = self.parent # pyright: ignore
        if not parent:
            return

        target = 0 if self.position == "left" else parent.width - self.width # pyright: ignore

        if self.show_animation:
            self._cancel_animations()
            self.show_animation.start(self)
        else:
            self.x = target

    def _hide(self):
        parent = self.parent # pyright: ignore
        if not parent:
            return

        target = -self.width if self.position == "left" else parent.width # pyright: ignore

        if self.hide_animation:
            self._cancel_animations()
            self.hide_animation.start(self)
        else:
            self.x = target

    def _cancel_animations(self):
        if self.show_animation:
            Animation.cancel_all(self.show_animation)

        if self.hide_animation:
            Animation.cancel_all(self.hide_animation)

    def _update_position(self, *_):
        parent = self.parent # pyright: ignore
        if not parent:
            return

        if self.position == "left":
            if self.open:
                self.x = 0
            else:
                self.x = -self.width # pyright: ignore

        elif self.position == "right":
            if self.open:
                self.x = parent.width - self.width # pyright: ignore
            else:
                self.x = parent.width
