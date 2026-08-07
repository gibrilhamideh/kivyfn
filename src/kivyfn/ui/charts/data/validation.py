from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from math import isfinite
from typing import Any

from ..errors import ChartDataError
from ..types import (
    ChartValue,
    DuplicatePolicy,
    InvalidDataPolicy,
    OrderingPolicy,
    ValueSelector,
)
from .dataset import ChartDataset
from .point import ChartPoint
from .selector import select_value


@dataclass(slots=True, frozen=True)
class DataDiagnostics:
    source_count: int = 0
    accepted_count: int = 0
    dropped_count: int = 0
    gap_count: int = 0
    duplicate_count: int = 0
    sorted_input: bool = False


@dataclass(slots=True, frozen=True)
class NormalizedData:
    points: tuple[ChartPoint, ...]
    diagnostics: DataDiagnostics


def value_scalar(value: ChartValue) -> float:
    """Convert a supported chart value into a stable sortable scalar."""
    if isinstance(value, bool):
        raise ChartDataError("Chart X values cannot be boolean")

    if isinstance(value, datetime):
        if value.tzinfo is None:
            epoch = datetime(1970, 1, 1)
            return (value - epoch).total_seconds()

        return value.astimezone(timezone.utc).timestamp()

    if isinstance(value, (int, float)):
        converted = float(value)
        if not isfinite(converted):
            raise ChartDataError(
                f"Chart X value must be finite, got {value!r}"
            )

        return converted

    raise ChartDataError(
        "Chart X values must be int, float, or datetime, got "
        f"{type(value).__name__}"
    )


def normalize_data(
    dataset: ChartDataset,
    *,
    x: ValueSelector,
    y: ValueSelector,
    invalid: InvalidDataPolicy,
    duplicates: DuplicatePolicy,
    ordering: OrderingPolicy,
) -> NormalizedData:
    """Normalize source rows according to explicit data policies."""
    points: list[ChartPoint] = []
    dropped = 0
    gaps = 0

    for index, row in enumerate(dataset):
        try:
            raw_x = select_value(row, x)
            value_scalar(raw_x)
            raw_y = select_value(row, y)
            normalized_y = _normalize_y(raw_y)
        except (ChartDataError, TypeError, ValueError) as error:
            if invalid == "raise":
                raise ChartDataError(
                    f"Invalid chart data at row {index}: {error}"
                ) from error

            dropped += 1
            continue

        if normalized_y is None:
            if invalid == "raise":
                raise ChartDataError(
                    f"Invalid chart Y value at row {index}: {raw_y!r}"
                )

            if invalid == "drop":
                dropped += 1
                continue

            gaps += 1

        points.append(
            ChartPoint(
                x=raw_x,
                y=normalized_y,
                source=row,
                source_index=index,
            )
        )

    was_sorted = _is_sorted(points)
    if not was_sorted and ordering == "require":
        raise ChartDataError(
            "Chart data must be ordered by ascending X value"
        )

    if not was_sorted:
        points.sort(key=lambda point: value_scalar(point.x))

    points, duplicate_count = _resolve_duplicates(
        points,
        duplicates,
    )

    diagnostics = DataDiagnostics(
        source_count=len(dataset),
        accepted_count=len(points),
        dropped_count=dropped,
        gap_count=gaps,
        duplicate_count=duplicate_count,
        sorted_input=was_sorted,
    )
    return NormalizedData(tuple(points), diagnostics)


def _normalize_y(value: Any) -> float | None:
    if value is None or isinstance(value, bool):
        return None

    try:
        converted = float(value)
    except (TypeError, ValueError):
        return None

    return converted if isfinite(converted) else None


def _is_sorted(points: list[ChartPoint]) -> bool:
    return all(
        value_scalar(previous.x) <= value_scalar(current.x)
        for previous, current in zip(points, points[1:])
    )


def _resolve_duplicates(
    points: list[ChartPoint],
    policy: DuplicatePolicy,
) -> tuple[list[ChartPoint], int]:
    if not points:
        return points, 0

    resolved: list[ChartPoint] = []
    index = 0
    duplicate_count = 0

    while index < len(points):
        group = [points[index]]
        scalar = value_scalar(points[index].x)
        index += 1

        while (
            index < len(points)
            and value_scalar(points[index].x) == scalar
        ):
            group.append(points[index])
            index += 1

        if len(group) == 1:
            resolved.append(group[0])
            continue

        duplicate_count += len(group) - 1

        if policy == "raise":
            raise ChartDataError(
                f"Duplicate chart X value {group[0].x!r}"
            )

        if policy == "first":
            resolved.append(group[0])
        elif policy == "last":
            resolved.append(group[-1])
        else:
            valid_values = [
                point.y
                for point in group
                if point.y is not None
            ]
            average = (
                sum(valid_values) / len(valid_values)
                if valid_values
                else None
            )
            resolved.append(
                ChartPoint(
                    x=group[-1].x,
                    y=average,
                    source=tuple(point.source for point in group),
                    source_index=group[-1].source_index,
                )
            )

    return resolved, duplicate_count
