from __future__ import annotations

from kivy.properties import ColorProperty
from kivy.uix.label import Label

from kivyfn.factory import load_kv
from kivyfn.ui.widget import FnWidget

from ..geometry import ChartBounds


class ChartTooltip(FnWidget, Label): # pyright: ignore
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

    def show(
        self,
        text: str,
        *,
        anchor: tuple[float, float],
        bounds: ChartBounds,
    ) -> None:
        self.text = text
        self.texture_update()
        padding_x, padding_y = self.padding
        self.size = (
            self.texture_size[0] + padding_x * 2,
            self.texture_size[1] + padding_y * 2,
        )

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
