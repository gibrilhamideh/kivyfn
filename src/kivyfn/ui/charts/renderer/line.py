from __future__ import annotations

from collections.abc import Iterable
from math import exp
from typing import Any

from kivy.graphics import Color, Ellipse, Line, Mesh

from ..data import ChartPoint
from ..geometry import ChartBounds, clip_segment
from ..series import ChartSeries, LineSeries
from .area import area_meshes
from .base import SeriesRenderer
from .context import RenderContext
from .decimation import min_max_decimate
from .gradient import gradient_texture


class LineRenderer(SeriesRenderer):
    """Render validated line data into clipped Kivy instructions."""

    def render_background(
        self,
        group: Any,
        series: ChartSeries,
        context: RenderContext,
        color: tuple[float, float, float, float],
    ) -> None:
        if not isinstance(series, LineSeries):
            raise TypeError("LineRenderer requires a LineSeries")

        if series.fill == "none" or not series.fill_opacity:
            return

        baseline = context.bounds.bottom
        if series.fill_baseline != "bottom":
            baseline = context.y_axis.scale.transform(
                series.fill_baseline,
                context.bounds.bottom,
                context.bounds.height,
            )

        gradient = series.fill == "gradient"
        meshes = area_meshes(
            self._line_segments(series, context),
            baseline,
            context.bounds,
            gradient=gradient,
        )
        added_color = False
        for vertices, indices in meshes:
            if not added_color:
                group.add(Color(*color[:3], series.fill_opacity))
                added_color = True

            group.add(
                Mesh(
                    vertices=vertices,
                    indices=indices,
                    mode="triangles",
                    texture=gradient_texture() if gradient else None,
                )
            )

    def render(
        self,
        group: object,
        series: ChartSeries,
        context: RenderContext,
        color: tuple[float, float, float, float],
    ) -> None:
        if not isinstance(series, LineSeries):
            raise TypeError("LineRenderer requires a LineSeries")

        segments = self._data_segments(series, context)
        rendered_points: list[tuple[float, float]] = []
        line_segments: list[tuple[tuple[float, float], ...]] = []
        for data_pixels in segments:
            rendered_points.extend(data_pixels)
            line_pixels = data_pixels
            if series.interpolation == "step":
                line_pixels = step_points(line_pixels)

            line_segments.append(line_pixels)

        if series.glow and series.glow_radius and series.glow_opacity:
            self._render_glow(group, series, context, color, line_segments)

        group.add(Color(*color))  # type: ignore[attr-defined]
        self._render_lines(group, series, line_segments, context.bounds)

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

    @staticmethod
    def _data_segments(
        series: LineSeries, context: RenderContext
    ) -> tuple[tuple[tuple[float, float], ...], ...]:
        segments = split_at_gaps(series.normalize().points)
        return tuple(
            transform_points(
                min_max_decimate(segment, context.max_points), context
            )
            for segment in segments
        )

    @classmethod
    def _line_segments(
        cls, series: LineSeries, context: RenderContext
    ) -> tuple[tuple[tuple[float, float], ...], ...]:
        segments = cls._data_segments(series, context)
        if series.interpolation == "step":
            return tuple(step_points(segment) for segment in segments)

        return segments

    @classmethod
    def _render_glow(
        cls,
        group: Any,
        series: LineSeries,
        context: RenderContext,
        color: tuple[float, float, float, float],
        segments: Iterable[tuple[tuple[float, float], ...]],
    ) -> None:
        # A bounded eight-stroke Gaussian approximation avoids offscreen
        # buffers. Expanded CPU clipping keeps halos from nearby offscreen
        # samples; the chart's stencil clips the final pixels to the plot.
        padding = series.width + series.glow_radius
        bounds = ChartBounds(
            context.bounds.left - padding,
            context.bounds.bottom - padding,
            context.bounds.right + padding,
            context.bounds.top + padding,
        )
        clipped = [
            flatten_points(line)
            for segment in segments
            for line in clip_polyline(segment, bounds)
        ]
        if not clipped:
            return

        layers = 8
        accumulated = 0.0
        for layer in range(layers, 0, -1):
            fraction = layer / layers
            falloff = exp(-4 * (fraction**2 - (1 / layers) ** 2))
            target = series.glow_opacity * falloff
            alpha = (target - accumulated) / (1 - accumulated)
            accumulated = target
            group.add(Color(*color[:3], alpha))
            width = series.width + series.glow_radius * fraction
            for points in clipped:
                group.add(Line(**cls._line_kwargs(series, points, width)))

    @classmethod
    def _render_lines(
        cls,
        group: Any,
        series: LineSeries,
        segments: Iterable[tuple[tuple[float, float], ...]],
        bounds: ChartBounds,
    ) -> None:
        for segment in segments:
            for clipped in clip_polyline(segment, bounds):
                points = flatten_points(clipped)
                group.add(
                    Line(**cls._line_kwargs(series, points, series.width))
                )

    @staticmethod
    def _line_kwargs(
        series: LineSeries, points: list[float], width: float
    ) -> dict[str, Any]:
        kwargs: dict[str, Any] = {"points": points, "width": width}
        if series.dash_length:
            kwargs["dash_length"] = series.dash_length
            kwargs["dash_offset"] = series.dash_offset

        return kwargs


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
    points: tuple[ChartPoint, ...], context: RenderContext
) -> tuple[tuple[float, float], ...]:
    transformed: list[tuple[float, float]] = []

    for point in points:
        if point.y is None:
            continue

        x = context.x_axis.scale.transform(
            point.x, context.bounds.left, context.bounds.width
        )
        y = context.y_axis.scale.transform(
            point.y, context.bounds.bottom, context.bounds.height
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
    points: tuple[tuple[float, float], ...], bounds: ChartBounds
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


def flatten_points(points: Iterable[tuple[float, float]]) -> list[float]:
    return [coordinate for point in points for coordinate in point]


def _same_point(
    first: tuple[float, float], second: tuple[float, float]
) -> bool:
    return (
        abs(first[0] - second[0]) < 1e-9 and abs(first[1] - second[1]) < 1e-9
    )
