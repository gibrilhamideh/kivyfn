from __future__ import annotations

from dataclasses import dataclass

from ..axis import ChartAxis
from ..geometry import ChartBounds
from ..types import RenderQuality


@dataclass(slots=True, frozen=True)
class RenderContext:
    bounds: ChartBounds
    x_axis: ChartAxis
    y_axis: ChartAxis
    quality: RenderQuality = "final"
    max_points: int = 2000
