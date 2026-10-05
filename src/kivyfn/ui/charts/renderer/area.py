from __future__ import annotations

from collections.abc import Iterable, Iterator
from typing import TypeAlias

from ..geometry import ChartBounds
from .gradient import GRADIENT_SIZE

PixelPoint: TypeAlias = tuple[float, float]
AreaVertex: TypeAlias = tuple[float, float, float, float]
MeshData: TypeAlias = tuple[list[float], list[int]]

# Kivy Mesh indices are unsigned shorts. Keep both vertices and indices below
# that limit, leaving room for one clipped polygon before starting a new mesh.
_MESH_LIMIT = 60000


def area_meshes(
    segments: Iterable[tuple[PixelPoint, ...]],
    baseline: float,
    bounds: ChartBounds,
    *,
    gradient: bool,
) -> Iterator[MeshData]:
    """Batch non-overlapping, clipped trapezoids into indexed triangles.

    Each input segment is one uninterrupted line. Vertical step edges and
    isolated points have no area. Baseline crossings are split first, making
    every polygon convex and preventing inverted or overlapping triangles.
    """
    vertices: list[float] = []
    indices: list[int] = []

    for points in segments:
        for start, end in zip(points, points[1:]):
            for left, right in _split_crossing(start, end, baseline):
                polygon = _area_polygon(left, right, baseline)
                polygon = _clip_polygon(polygon, bounds)
                if len(polygon) < 3:
                    continue

                extra_indices = (len(polygon) - 2) * 3
                if (
                    len(vertices) // 4 + len(polygon) > _MESH_LIMIT
                    or len(indices) + extra_indices > _MESH_LIMIT
                ):
                    yield vertices, indices
                    vertices, indices = [], []

                first = len(vertices) // 4
                height_scale = max(vertex[2] for vertex in polygon)
                if height_scale == 0:
                    continue

                for x, y, height, distance in polygon:
                    uv = (0.0, 0.0)
                    if gradient:
                        # Sample texel centers; the lookup texture stores
                        # alpha=distance/height. Normalize after clipping to
                        # retain precision even near an offscreen crossing.
                        scale = (GRADIENT_SIZE - 1) / height_scale
                        uv = (
                            (height * scale + 0.5) / GRADIENT_SIZE,
                            (distance * scale + 0.5) / GRADIENT_SIZE,
                        )

                    vertices.extend((x, y, *uv))

                for offset in range(1, len(polygon) - 1):
                    indices.extend((first, first + offset, first + offset + 1))

    if indices:
        yield vertices, indices


def _split_crossing(
    start: PixelPoint, end: PixelPoint, baseline: float
) -> tuple[tuple[PixelPoint, PixelPoint], ...]:
    if start[0] == end[0]:
        return ()

    first_height = start[1] - baseline
    last_height = end[1] - baseline
    if first_height == last_height == 0:
        return ()

    if (first_height < 0 < last_height) or (last_height < 0 < first_height):
        fraction = first_height / (first_height - last_height)
        crossing = (start[0] + fraction * (end[0] - start[0]), baseline)
        return (start, crossing), (crossing, end)

    return ((start, end),)


def _area_polygon(
    start: PixelPoint, end: PixelPoint, baseline: float
) -> list[AreaVertex]:
    first_height = abs(start[1] - baseline)
    last_height = abs(end[1] - baseline)
    return [
        (start[0], start[1], first_height, first_height),
        (end[0], end[1], last_height, last_height),
        (end[0], baseline, last_height, 0.0),
        (start[0], baseline, first_height, 0.0),
    ]


def _clip_polygon(
    polygon: list[AreaVertex], bounds: ChartBounds
) -> list[AreaVertex]:
    # Sutherland-Hodgman preserves the interpolated gradient coordinates at
    # every viewport edge, including when the true baseline is offscreen.
    for axis, edge, keep_greater in (
        (0, bounds.left, True),
        (0, bounds.right, False),
        (1, bounds.bottom, True),
        (1, bounds.top, False),
    ):
        if not polygon:
            break

        clipped: list[AreaVertex] = []
        previous = polygon[-1]
        previous_inside = _inside(previous[axis], edge, keep_greater)
        for current in polygon:
            current_inside = _inside(current[axis], edge, keep_greater)
            if previous_inside != current_inside:
                ratio = (edge - previous[axis]) / (
                    current[axis] - previous[axis]
                )
                intersection = tuple(
                    first + ratio * (last - first)
                    for first, last in zip(previous, current, strict=True)
                )
                clipped.append(intersection)  # type: ignore[arg-type]

            if current_inside:
                clipped.append(current)

            previous = current
            previous_inside = current_inside

        polygon = clipped

    return polygon


def _inside(value: float, edge: float, keep_greater: bool) -> bool:
    return value >= edge if keep_greater else value <= edge
