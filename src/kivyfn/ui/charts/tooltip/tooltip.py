from __future__ import annotations

from kivy.properties import ColorProperty
from kivy.uix.label import Label

from kivyfn.factory import load_kv
from kivyfn.ui.widget import FnWidget

from ..geometry import ChartBounds


class ChartTooltip(FnWidget, Label):  # pyright: ignore
    """Default boundary-aware tooltip used by FnChart."""

    background_color = ColorProperty((0.09, 0.11, 0.18, 0.96))
    border_color = ColorProperty((0.55, 0.60, 0.65, 0.4))

    def __init__(self, **kwargs: object) -> None:
        super().__init__(**kwargs)
        self.size_hint = None, None
        self.opacity = 0
        self.halign = "left"
        self.valign = "middle"
        self.padding = 10, 6
        self.markup = True

    def show(
        self, text: str, *, anchor: tuple[float, float], bounds: ChartBounds
    ) -> None:
        if bounds.width <= 0 or bounds.height <= 0:
            self.dismiss()
            return
        self.text_size = None, None
        self.text = text
        self.texture_update()
        if self.texture_size[0] > bounds.width:
            self.text_size = bounds.width, None
            self.texture_update()
        # Label's texture includes padding; Kivy 2.3 exposes four values.
        self.size = self.texture_size

        x = anchor[0] + 12
        y = anchor[1] + 12

        if x + self.width > bounds.right:
            x = anchor[0] - self.width - 12

        if y + self.height > bounds.top:
            y = anchor[1] - self.height - 12

        self.x = max(bounds.left, min(x, bounds.right - self.width))
        self.y = max(bounds.bottom, min(y, bounds.top - self.height))
        self.opacity = 1

    def dismiss(self) -> None:
        self.opacity = 0


load_kv(__file__)
