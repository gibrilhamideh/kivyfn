from __future__ import annotations

from dataclasses import dataclass
from math import hypot
from typing import Any

from ..errors import ChartConfigurationError
from ..types import DragMode, PanMode, SelectionMode, ZoomMode


@dataclass(slots=True, frozen=True)
class ChartInteraction:
    pan: PanMode = "x"
    zoom: ZoomMode = "x"
    selection: SelectionMode = "nearest_x"
    pinch_zoom: bool = True
    double_tap_reset: bool = True
    touch_slop: float = 8.0
    snap: bool = True
    drag: DragMode = "pan"

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
                f"Unsupported chart selection mode {self.selection!r}"
            )

        if self.touch_slop < 0:
            raise ChartConfigurationError(
                "Chart touch slop cannot be negative"
            )
        if self.drag not in {"pan", "inspect"}:
            raise ChartConfigurationError(
                f"Unsupported chart drag mode {self.drag!r}"
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
            touch, "is_double_tap", False
        ):
            self.chart.reset_viewport()
            return True

        if len(self._touches) >= 2:
            return False

        touch.grab(self.chart)
        local = self.chart.to_local(*touch.pos)
        self._touches[touch] = {
            "start": local,
            "last": local,
            "moved": False,
            "multi": False,
        }

        if len(self._touches) == 2:
            for state in self._touches.values():
                state["multi"] = True
            self._pinch_distance = self._distance_between_touches()
        else:
            self.chart.activate_at(*touch.pos)

        return True

    def on_touch_move(self, touch: Any) -> bool:
        state = self._touches.get(touch)
        if state is None or touch.grab_current is not self.chart:
            return False

        interaction = self.chart.interaction

        local = self.chart.to_local(*touch.pos)
        previous_center = self._center()
        last_x, last_y = state["last"]
        state["last"] = local

        if len(self._touches) == 2:
            self._update_pinch(previous_center)
            state["moved"] = True
            return True

        # Lifting one finger must not turn a pinch into an inspection jump.
        if state["multi"]:
            return True

        delta_x = local[0] - last_x
        delta_y = local[1] - last_y
        start_x, start_y = state["start"]
        distance = hypot(local[0] - start_x, local[1] - start_y)

        if distance >= interaction.touch_slop:
            state["moved"] = True

        if interaction.drag == "inspect" and interaction.selection != "none":
            bounds = self.chart.plot_bounds
            x = max(bounds.left, min(local[0], bounds.right))
            y = max(bounds.bottom, min(local[1], bounds.top))
            self.chart.select_at(*self.chart.to_parent(x, y))
        elif state["moved"] and interaction.pan != "none":
            self.chart.pan_pixels(delta_x, delta_y)
        elif interaction.selection != "none":
            self.chart.select_at(touch.x, touch.y)

        return True

    def on_touch_up(self, touch: Any) -> bool:
        state = self._touches.pop(touch, None)
        if state is None or touch.grab_current is not self.chart:
            return False

        touch.ungrab(self.chart)

        if len(self._touches) < 2:
            self._pinch_distance = None

        self.chart.finish_interaction()
        return True

    def cancel(self) -> None:
        for touch in tuple(self._touches):
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

    def _update_pinch(self, previous_center: tuple[float, float]) -> None:
        current = self._distance_between_touches()
        previous = self._pinch_distance
        center = self._center()
        interaction = self.chart.interaction
        with self.chart.update():
            if interaction.pan != "none":
                self.chart.pan_pixels(
                    center[0] - previous_center[0],
                    center[1] - previous_center[1],
                )
            if (
                interaction.pinch_zoom and interaction.zoom != "none"
                and previous and current > 0
            ):
                self.chart.zoom_at(
                    *self.chart.to_parent(*center), previous / current
                )
        self._pinch_distance = current

    def _distance_between_touches(self) -> float:
        first, second = tuple(self._touches.values())[:2]
        a, b = first["last"], second["last"]
        return hypot(a[0] - b[0], a[1] - b[1])

    def _center(self) -> tuple[float, float]:
        positions = [state["last"] for state in self._touches.values()]
        return (
            sum(point[0] for point in positions) / len(positions),
            sum(point[1] for point in positions) / len(positions),
        )
