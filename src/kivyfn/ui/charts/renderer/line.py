from __future__ import annotations

from collections.abc import Iterable

from kivy.graphics import Color, Ellipse, Line

from ..data import ChartPoint
from ..geometry import ChartBounds, clip_segment
from ..series import ChartSeries, LineSeries
from .base import SeriesRenderer
from .context import RenderContext
from .decimation import min_max_decimate


class LineRenderer(SeriesRenderer):
    """Render validated line data into clipped Kivy instructions."""

    def render(
        self,
        group: object,
        series: ChartSeries,
        context: RenderContext,
        color: tuple[float, float, float, float],
    ) -> None:
        if not isinstance(series, LineSeries):
            raise TypeError("LineRenderer requires a LineSeries")

        normalized = series.normalize()
        segments = split_at_gaps(normalized.points)
        group.add(Color(*color))  # type: ignore[attr-defined]

        rendered_points: list[tuple[float, float]] = []
        for segment in segments:
            reduced = min_max_decimate(segment, context.max_points)
            data_pixels = transform_points(reduced, context)
            rendered_points.extend(data_pixels)
            line_pixels = data_pixels

            if series.interpolation == "step":
                line_pixels = step_points(line_pixels)

            for clipped in clip_polyline(line_pixels, context.bounds):
                kwargs = {
                    "points": flatten_points(clipped),
                    "width": series.width,
                }

                if series.dash_length:
                    kwargs["dash_length"] = series.dash_length
                    kwargs["dash_offset"] = series.dash_offset

                group.add(Line(**kwargs))  # type: ignore[attr-defined]

        if series.marker_size and len(rendered_points) <= 2000:
            radius = series.marker_size / 2
            for x, y in rendered_points:
                if context.bounds.contains(x, y):
                    group.add(  # type: ignore[attr-defined]
                        Ellipse(
                            pos=(x - radius, y - radius),
                            size=(series.marker_size, series.marker_size),
                        )
                    )


def split_at_gaps(
    points: Iterable[ChartPoint],
) -> tuple[tuple[ChartPoint, ...], ...]:
    segments: list[tuple[ChartPoint, ...]] = []
    current: list[ChartPoint] = []

    for point in points:
        if point.is_gap:
            if current:
                segments.append(tuple(current))
                current.clear()

            continue

        current.append(point)

    if current:
        segments.append(tuple(current))

    return tuple(segments)


def transform_points(
    points: tuple[ChartPoint, ...],
    context: RenderContext,
) -> tuple[tuple[float, float], ...]:
    transformed: list[tuple[float, float]] = []

    for point in points:
        if point.y is None:
            continue

        x = context.x_axis.scale.transform(
            point.x,
            context.bounds.left,
            context.bounds.width,
        )
        y = context.y_axis.scale.transform(
            point.y,
            context.bounds.bottom,
            context.bounds.height,
        )
        transformed.append((x, y))

    return tuple(transformed)


def step_points(
    points: tuple[tuple[float, float], ...],
) -> tuple[tuple[float, float], ...]:
    if len(points) < 2:
        return points

    stepped = [points[0]]
    for point in points[1:]:
        stepped.append((point[0], stepped[-1][1]))
        stepped.append(point)

    return tuple(stepped)


def clip_polyline(
    points: tuple[tuple[float, float], ...],
    bounds: ChartBounds,
) -> tuple[tuple[tuple[float, float], ...], ...]:
    if len(points) < 2:
        return ()

    lines: list[tuple[tuple[float, float], ...]] = []
    current: list[tuple[float, float]] = []

    for start, end in zip(points, points[1:]):
        clipped = clip_segment(start, end, bounds)
        if clipped is None:
            if len(current) >= 2:
                lines.append(tuple(current))

            current.clear()
            continue

        clipped_start, clipped_end = clipped
        if current and _same_point(current[-1], clipped_start):
            current.append(clipped_end)
            continue

        if len(current) >= 2:
            lines.append(tuple(current))

        current = [clipped_start, clipped_end]

    if len(current) >= 2:
        lines.append(tuple(current))

    return tuple(lines)


def flatten_points(
    points: Iterable[tuple[float, float]],
) -> list[float]:
    return [coordinate for point in points for coordinate in point]


def _same_point(
    first: tuple[float, float],
    second: tuple[float, float],
) -> bool:
    return (
        abs(first[0] - second[0]) < 1e-9
        and abs(first[1] - second[1]) < 1e-9
    )
