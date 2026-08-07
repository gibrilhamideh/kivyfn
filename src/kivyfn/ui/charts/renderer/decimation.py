from __future__ import annotations

from ..data import ChartPoint
from ..data.validation import value_scalar


def min_max_decimate(
    points: tuple[ChartPoint, ...],
    limit: int,
) -> tuple[ChartPoint, ...]:
    """Reduce dense data while preserving local extrema and endpoints."""
    if limit <= 0 or len(points) <= limit:
        return points

    if limit == 1:
        return points[:1]

    if limit == 2:
        return points[0], points[-1]

    bucket_count = max((limit - 2) // 2, 1)
    bucket_size = len(points) / bucket_count
    selected: list[ChartPoint] = [points[0]]

    for bucket in range(bucket_count):
        start = int(bucket * bucket_size)
        end = min(int((bucket + 1) * bucket_size), len(points))
        values = points[start:end]
        if not values:
            continue

        minimum = min(values, key=lambda point: point.y or 0.0)
        maximum = max(values, key=lambda point: point.y or 0.0)
        extrema = {
            minimum.source_index: minimum,
            maximum.source_index: maximum,
        }

        for point in sorted(
            extrema.values(),
            key=lambda item: value_scalar(item.x),
        ):
            if point is not selected[-1] and len(selected) < limit - 1:
                selected.append(point)

    if selected[-1] is not points[-1]:
        selected.append(points[-1])

    return tuple(selected)
