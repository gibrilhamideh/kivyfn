from __future__ import annotations

from dataclasses import dataclass
from math import hypot
from typing import Any

from ..errors import ChartConfigurationError
from ..types import PanMode, SelectionMode, ZoomMode


@dataclass(slots=True, frozen=True)
class ChartInteraction:
    pan: PanMode = "x"
    zoom: ZoomMode = "x"
    selection: SelectionMode = "nearest_x"
    pinch_zoom: bool = True
    double_tap_reset: bool = True
    touch_slop: float = 8.0

    def __post_init__(self) -> None:
        modes = {"none", "x", "y", "both"}
        if self.pan not in modes:
            raise ChartConfigurationError(
                f"Unsupported chart pan mode {self.pan!r}"
            )

        if self.zoom not in modes:
            raise ChartConfigurationError(
                f"Unsupported chart zoom mode {self.zoom!r}"
            )

        selections = {"none", "nearest_x", "nearest_point"}
        if self.selection not in selections:
            raise ChartConfigurationError(
                "Unsupported chart selection mode "
                f"{self.selection!r}"
            )

        if self.touch_slop < 0:
            raise ChartConfigurationError(
                "Chart touch slop cannot be negative"
            )


class ChartInteractionController:
    """Translate Kivy touch streams into high-level chart operations."""

    def __init__(self, chart: Any) -> None:
        self.chart = chart
        self._touches: dict[Any, dict[str, Any]] = {}
        self._pinch_distance: float | None = None

    def on_touch_down(self, touch: Any) -> bool:
        if not self.chart.is_plot_point(*touch.pos):
            return False

        if getattr(touch, "is_mouse_scrolling", False):
            return self._handle_scroll(touch)

        interaction = self.chart.interaction
        if interaction.double_tap_reset and getattr(
            touch,
            "is_double_tap",
            False,
        ):
            self.chart.reset_viewport()
            return True

        touch.grab(self.chart)
        self._touches[touch] = {
            "start": touch.pos,
            "last": touch.pos,
            "moved": False,
        }

        if len(self._touches) == 2:
            self._pinch_distance = self._distance_between_touches()

        return True

    def on_touch_move(self, touch: Any) -> bool:
        state = self._touches.get(touch)
        if state is None or touch.grab_current is not self.chart:
            return False

        interaction = self.chart.interaction

        if (
            len(self._touches) == 2
            and interaction.pinch_zoom
            and interaction.zoom != "none"
        ):
            self._update_pinch()
            state["last"] = touch.pos
            state["moved"] = True
            return True

        last_x, last_y = state["last"]
        delta_x = touch.x - last_x
        delta_y = touch.y - last_y
        start_x, start_y = state["start"]
        distance = hypot(touch.x - start_x, touch.y - start_y)

        if distance >= interaction.touch_slop:
            state["moved"] = True

        if state["moved"] and interaction.pan != "none":
            self.chart.pan_pixels(delta_x, delta_y)
        elif interaction.selection != "none":
            self.chart.select_at(touch.x, touch.y)

        state["last"] = touch.pos
        return True

    def on_touch_up(self, touch: Any) -> bool:
        state = self._touches.pop(touch, None)
        if state is None or touch.grab_current is not self.chart:
            return False

        touch.ungrab(self.chart)

        if not state["moved"]:
            self.chart.activate_at(touch.x, touch.y)

        if len(self._touches) < 2:
            self._pinch_distance = None

        self.chart.finish_interaction()
        return True

    def cancel(self) -> None:
        for touch in tuple(self._touches):
            if touch.grab_current is self.chart:
                touch.ungrab(self.chart)

        self._touches.clear()
        self._pinch_distance = None

    def _handle_scroll(self, touch: Any) -> bool:
        if self.chart.interaction.zoom == "none":
            return False

        button = getattr(touch, "button", "")
        if button == "scrollup":
            factor = 0.8
        elif button == "scrolldown":
            factor = 1.25
        else:
            return False

        self.chart.zoom_at(touch.x, touch.y, factor)
        self.chart.finish_interaction()
        return True

    def _update_pinch(self) -> None:
        current = self._distance_between_touches()
        previous = self._pinch_distance

        if previous is None or previous <= 0 or current <= 0:
            self._pinch_distance = current
            return

        center_x = sum(touch.x for touch in self._touches) / 2
        center_y = sum(touch.y for touch in self._touches) / 2
        factor = previous / current
        self.chart.zoom_at(center_x, center_y, factor)
        self._pinch_distance = current

    def _distance_between_touches(self) -> float:
        first, second = tuple(self._touches)[:2]
        return hypot(first.x - second.x, first.y - second.y)
