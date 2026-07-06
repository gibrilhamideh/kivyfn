from __future__ import annotations
from typing import Literal
from kivy.clock import Clock
from kivy.uix.relativelayout import RelativeLayout
from kivy.properties import ObjectProperty, DictProperty

from kivyfn.ui.widget import FnWidget

from kivyfn.ui.behaviors.canvas import FnClipBehavior
from kivyfn.ui.behaviors.style import FnBackgroundBehavior
from kivyfn.ui.layouts.scaffold.body import FnScaffoldBody
from kivyfn.ui.layouts.scaffold.drawer import FnScaffoldDrawer
from kivyfn.ui.layouts.scaffold.toolbar import FnScaffoldToolbar


class FnScaffold(FnBackgroundBehavior, FnClipBehavior, FnWidget, RelativeLayout):
    body: FnScaffoldBody = ObjectProperty()
    toolbars: dict[Literal["top", "bottom"], FnScaffoldToolbar] = DictProperty()
    drawers: dict[Literal["left", "right"], FnScaffoldDrawer] = DictProperty()

    # --------------------------------------------------
    # Widget insertion
    # --------------------------------------------------

    def add_widget(self, widget, *args, **kwargs):
        Clock.schedule_once(lambda x: self._register(widget))

        return super().add_widget(widget, *args, **kwargs)

    def _register(self, widget, *_):
        if isinstance(widget, FnScaffoldDrawer):
            position = widget.position
            if position in self.drawers:
                raise ValueError("drawer in this position already added")

            widget.bind(  # pyright: ignore
                x=self._update_layout,
                width=self._update_layout,
                mode=self._update_layout,
            )

            widget.size_hint = None, None  # pyright: ignore
            widget.width = widget.extent  # pyright: ignore
            self.drawers[position] = widget  # pyright: ignore

        elif isinstance(widget, FnScaffoldToolbar):
            position = widget.position
            if position in self.toolbars:
                raise ValueError("toolbar in this position already added")

            widget.bind(  # pyright: ignore
                y=self._update_layout,
                height=self._update_layout,
                mode=self._update_layout,
            )

            widget.size_hint = None, None  # pyright: ignore
            widget.height = widget.extent  # pyright: ignore
            self.toolbars[position] = widget

        elif isinstance(widget, FnScaffoldBody):
            if self.body is not None:
                raise ValueError("FnScaffold already has a body")

            self.body = widget
            self.body.size_hint = (None, None) # pyright: ignore

    # --------------------------------------------------
    # Lifecycle
    # --------------------------------------------------

    def on_kv_post(self, base_widget):
        self.bind(size=self._update_layout)  # pyright: ignore
        self._update_layout()

        return super().on_kv_post(base_widget)

    # --------------------------------------------------
    # Layout engine
    # --------------------------------------------------
    def _update_layout(self, *_):
        top_push = 0
        bottom_push = 0
        left_push = 0
        right_push = 0

        # --------------------------------------------------
        # Toolbars
        # --------------------------------------------------

        top = self.toolbars.get("top")
        if top and top.mode == "push":
            top_push = self.height - top.y

        bottom = self.toolbars.get("bottom")
        if bottom and bottom.mode == "push":
            bottom_push = bottom.height + bottom.y  # pyright: ignore

        # --------------------------------------------------
        # Drawers
        # --------------------------------------------------

        left = self.drawers.get("left")
        if left and left.mode == "push":
            left_push = left.width + left.x  # pyright: ignore

        right = self.drawers.get("right")
        if right and right.mode == "push":
            right_push = self.width - right.x

        # --------------------------------------------------
        # Compute shared content geometry
        # body + toolbars are pushed by drawers
        # --------------------------------------------------

        content_x = left_push
        content_width = self.width - left_push - right_push

        body_y = bottom_push
        body_height = self.height - top_push - bottom_push

        # --------------------------------------------------
        # Body layout
        # --------------------------------------------------

        if self.body:
            self.body.x = content_x # pyright: ignore
            self.body.y = body_y # pyright: ignore
            self.body.width = content_width # pyright: ignore
            self.body.height = body_height # pyright: ignore

        # --------------------------------------------------
        # Toolbar layout
        # Toolbars keep their own y from FnToolbarBehavior,
        # but scaffold controls x/width so drawers can push them
        # --------------------------------------------------

        if top:
            top.x = content_x # pyright: ignore
            top.width = content_width # pyright: ignore

        if bottom:
            bottom.x = content_x # pyright: ignore
            bottom.width = content_width # pyright: ignore

        # --------------------------------------------------
        # Drawer layout
        # Drawers always span full scaffold height
        # They keep their own x from FnDrawerBehavior
        # --------------------------------------------------

        for drawer in self.drawers.values():
            drawer.y = 0 # pyright: ignore
            drawer.height = self.height # pyright: ignore
