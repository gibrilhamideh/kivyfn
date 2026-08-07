from __future__ import annotations

from typing import Any

from ..errors import ChartSeriesError
from ..types import LineInterpolation
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

        super().__init__(**kwargs)
        self.width = float(width)
        self.interpolation = interpolation
        self.marker_size = float(marker_size)
        self.dash_length = float(dash_length)
        self.dash_offset = float(dash_offset)
