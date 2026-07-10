from __future__ import annotations

from typing import Any

from kivy.uix.boxlayout import BoxLayout

from kivyfn.ui.widget import FnWidget
from kivyfn.ui.behaviors.layouts.adaptive_size import (
    FnLayoutAdaptiveSizeBehavior,
)


class FnBoxLayout(
    FnLayoutAdaptiveSizeBehavior,
    FnWidget,
    BoxLayout,
):
    def do_layout(self, *args: Any) -> None:
        children = [
            child
            for child in self.children  # pyright: ignore
            if child.display # pyright: ignore
        ]

        if not children:
            left, top, right, bottom = self.padding
            self.minimum_size = (
                left + right,
                top + bottom,
            )
            return

        sizes = [
            (
                child.size,
                child.size_hint,
                child.pos_hint,
                child.size_hint_min,
                child.size_hint_max,
            )
            for child in children
        ]

        for index, x, y, width, height in self._iterate_layout(sizes):
            child = children[index]
            child.pos = x, y

            size_hint_x, size_hint_y = child.size_hint

            if size_hint_x is None:
                if size_hint_y is not None:
                    child.height = height
            elif size_hint_y is None:
                child.width = width
            else:
                child.size = width, height

    def add_widget(
        self,
        widget: Any,
        *args: Any,
        **kwargs: Any,
    ) -> None:
        widget.fbind(
            "display",
            self._trigger_layout,
        )

        super().add_widget(
            widget,
            *args,
            **kwargs,
        )

    def remove_widget(
        self,
        widget: Any,
        *args: Any,
        **kwargs: Any,
    ) -> None:
        widget.funbind(
            "display",
            self._trigger_layout,
        )

        super().remove_widget(
            widget,
            *args,
            **kwargs,
        )
