from __future__ import annotations

from dataclasses import dataclass

from ..data import ChartPoint
from ..types import ChartValue, SelectionMode


@dataclass(slots=True, frozen=True)
class SelectedPoint:
    series_id: str
    point: ChartPoint
    pixel: tuple[float, float]
    distance: float


@dataclass(slots=True, frozen=True)
class ChartSelection:
    mode: SelectionMode
    x: ChartValue
    pixel: tuple[float, float]
    points: tuple[SelectedPoint, ...]

    def get(self, series_id: str) -> SelectedPoint | None:
        for point in self.points:
            if point.series_id == series_id:
                return point

        return None
