from __future__ import annotations

from typing import TYPE_CHECKING, Any

from kivy.core.text import Label as CoreLabel
from kivy.graphics import Color, Ellipse, Rectangle
from kivy.uix.widget import Widget

from kivyfn.ui.widget import FnWidget


if TYPE_CHECKING:
    from ..chart import FnChart


class ChartLegend(FnWidget, Widget):
    """Compact canvas legend with series visibility controls."""

    def __init__(
        self,
        chart: FnChart,
        **kwargs: Any,
    ) -> None:
        super().__init__(**kwargs)
        self.chart = chart
        self.size_hint = None, None
        self.height = 30
        self._hit_regions: list[
            tuple[float, float, float, float, str]
        ] = []

    def rebuild(self) -> None:
        self.canvas.clear()
        self._hit_regions.clear()
        cursor_x = 0.0

        for series in self.chart.series:
            color = self.chart.color_for_series(series)
            alpha = 1.0 if series.visible else 0.35
            label = CoreLabel(
                text=series.label,
                font_size=11,
                color=(*self.chart.text_color[:3], alpha),
            )
            label.refresh()
            width = 18 + label.texture.size[0] + 16

            with self.canvas:
                Color(*color[:3], color[3] * alpha)
                Ellipse(
                    pos=(self.x + cursor_x, self.y + 10),
                    size=(8, 8),
                )
                Color(1, 1, 1, alpha)
                Rectangle(
                    texture=label.texture,
                    pos=(self.x + cursor_x + 14, self.y + 5),
                    size=label.texture.size,
                )

            self._hit_regions.append(
                (cursor_x, 0, width, self.height, series.id)
            )
            cursor_x += width

        self.width = max(cursor_x, 1)

    def on_touch_down(self, touch: Any) -> bool:
        if not self.collide_point(*touch.pos):
            return super().on_touch_down(touch)

        local_x, local_y = self.to_local(*touch.pos)

        for x, y, width, height, series_id in self._hit_regions:
            if x <= local_x <= x + width and y <= local_y <= y + height:
                self.chart.toggle_series(series_id)
                return True

        return super().on_touch_down(touch)
