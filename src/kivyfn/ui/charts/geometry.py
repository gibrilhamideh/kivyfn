from __future__ import annotations

from dataclasses import dataclass
from math import hypot


@dataclass(slots=True, frozen=True)
class ChartBounds:
    """Rectangular chart region expressed in local widget coordinates."""

    left: float
    bottom: float
    right: float
    top: float

    def __post_init__(self) -> None:
        if self.right < self.left:
            raise ValueError("Chart bounds right must be at least left")

        if self.top < self.bottom:
            raise ValueError("Chart bounds top must be at least bottom")

    @property
    def width(self) -> float:
        return self.right - self.left

    @property
    def height(self) -> float:
        return self.top - self.bottom

    @property
    def pos(self) -> tuple[float, float]:
        return self.left, self.bottom

    @property
    def size(self) -> tuple[float, float]:
        return self.width, self.height

    def contains(self, x: float, y: float) -> bool:
        return (
            self.left <= x <= self.right
            and self.bottom <= y <= self.top
        )


def distance(
    point_a: tuple[float, float],
    point_b: tuple[float, float],
) -> float:
    """Return Euclidean distance between two points."""
    return hypot(
        point_b[0] - point_a[0],
        point_b[1] - point_a[1],
    )


def clip_segment(
    start: tuple[float, float],
    end: tuple[float, float],
    bounds: ChartBounds,
) -> tuple[tuple[float, float], tuple[float, float]] | None:
    """Clip one segment to bounds with the Liang-Barsky algorithm."""
    x0, y0 = start
    x1, y1 = end
    dx = x1 - x0
    dy = y1 - y0

    p = (-dx, dx, -dy, dy)
    q = (
        x0 - bounds.left,
        bounds.right - x0,
        y0 - bounds.bottom,
        bounds.top - y0,
    )

    lower = 0.0
    upper = 1.0

    for direction, distance_to_edge in zip(p, q, strict=True):
        if direction == 0:
            if distance_to_edge < 0:
                return None

            continue

        ratio = distance_to_edge / direction

        if direction < 0:
            lower = max(lower, ratio)
        else:
            upper = min(upper, ratio)

        if lower > upper:
            return None

    clipped_start = (
        x0 + lower * dx,
        y0 + lower * dy,
    )
    clipped_end = (
        x0 + upper * dx,
        y0 + upper * dy,
    )
    return clipped_start, clipped_end
