from __future__ import annotations

from bisect import bisect_left

from ..data import ChartPoint
from ..data.validation import value_scalar


def nearest_x(
    points: tuple[ChartPoint, ...],
    target: float,
) -> ChartPoint | None:
    """Return the point with the nearest scalar X value."""
    if not points:
        return None

    scalars = [value_scalar(point.x) for point in points]
    index = bisect_left(scalars, target)

    if index == 0:
        return points[0]

    if index == len(points):
        return points[-1]

    before = points[index - 1]
    after = points[index]
    before_distance = abs(value_scalar(before.x) - target)
    after_distance = abs(value_scalar(after.x) - target)
    return before if before_distance <= after_distance else after
