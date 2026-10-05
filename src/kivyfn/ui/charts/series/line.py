from __future__ import annotations

from math import isfinite
from typing import Any

from ..errors import ChartSeriesError
from ..types import FillBaseline, LineFill, LineInterpolation
from .base import ChartSeries


class LineSeries(ChartSeries):
    """A connected numeric series rendered as linear or step segments."""

    kind = "line"

    def __init__(
        self,
        *,
        width: float = 2.0,
        interpolation: LineInterpolation = "linear",
        marker_size: float = 0.0,
        dash_length: float = 0.0,
        dash_offset: float = 0.0,
        fill: LineFill = "none",
        fill_opacity: float = 0.18,
        fill_baseline: FillBaseline = 0.0,
        glow: bool = False,
        glow_radius: float = 8.0,
        glow_opacity: float = 0.25,
        **kwargs: Any,
    ) -> None:
        if width <= 0:
            raise ChartSeriesError("Line width must be positive")

        if interpolation not in {"linear", "step"}:
            raise ChartSeriesError(
                f"Unsupported line interpolation {interpolation!r}"
            )

        if marker_size < 0:
            raise ChartSeriesError("Marker size cannot be negative")

        if dash_length < 0 or dash_offset < 0:
            raise ChartSeriesError(
                "Line dash length and offset cannot be negative"
            )

        self.fill = fill
        self.fill_opacity = fill_opacity
        self.fill_baseline = fill_baseline
        self.glow = glow
        self.glow_radius = glow_radius
        self.glow_opacity = glow_opacity
        self._validate_effects()

        super().__init__(**kwargs)
        self.width = float(width)
        self.interpolation = interpolation
        self.marker_size = float(marker_size)
        self.dash_length = float(dash_length)
        self.dash_offset = float(dash_offset)

    def notify_changed(self) -> None:
        """Validate edited effect settings and request the usual redraw."""
        self._validate_effects()
        super().notify_changed()

    def _validate_effects(self) -> None:
        if self.fill not in {"none", "solid", "gradient"}:
            raise ChartSeriesError(f"Unsupported line fill {self.fill!r}")
        if not isinstance(self.glow, bool):
            raise ChartSeriesError("glow must be a boolean")
        for name in ("fill_opacity", "glow_opacity", "glow_radius"):
            value = getattr(self, name)
            if not _finite_number(value) or value < 0:
                raise ChartSeriesError(
                    f"{name} must be finite and nonnegative"
                )
            if name != "glow_radius" and value > 1:
                raise ChartSeriesError(f"{name} must be between zero and one")
        if self.fill_baseline != "bottom" and not _finite_number(
            self.fill_baseline
        ):
            raise ChartSeriesError(
                "fill_baseline must be a finite number or 'bottom'"
            )


def _finite_number(value: Any) -> bool:
    return (
        isinstance(value, (int, float))
        and not isinstance(value, bool)
        and isfinite(value)
    )
