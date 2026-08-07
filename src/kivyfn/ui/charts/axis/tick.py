from __future__ import annotations

from dataclasses import dataclass
from math import ceil, floor, log10

from ..types import ChartValue
from .axis import ChartAxis


@dataclass(slots=True, frozen=True)
class ChartTick:
    value: ChartValue
    label: str


_DATETIME_INTERVALS = (
    1,
    5,
    15,
    30,
    60,
    300,
    900,
    1800,
    3600,
    10800,
    21600,
    43200,
    86400,
    172800,
    604800,
    2592000,
    7776000,
    31536000,
)


def locate_ticks(axis: ChartAxis) -> tuple[ChartTick, ...]:
    """Generate readable ticks for the axis's current scale domain."""
    lower, upper = axis.scale.scalar_domain
    span = upper - lower
    if span <= 0:
        return ()

    if axis.kind == "datetime":
        raw_step = span / max(axis.target_ticks, 1)
        step = min(
            _DATETIME_INTERVALS,
            key=lambda interval: abs(interval - raw_step),
        )
    else:
        step = _nice_step(span, axis.target_ticks)

    first = ceil(lower / step) * step
    last = floor(upper / step) * step
    ticks: list[ChartTick] = []
    current = first
    guard = 0

    while current <= last + step * 1e-9 and guard < 1000:
        value = axis.scale.from_scalar(current)
        ticks.append(
            ChartTick(
                value=value,
                label=axis.format(value),
            )
        )
        current += step
        guard += 1

    return tuple(ticks)


def _nice_step(span: float, target_ticks: int) -> float:
    target = max(target_ticks, 1)
    rough = span / target
    power = 10 ** floor(log10(rough))
    fraction = rough / power

    if fraction <= 1:
        nice_fraction = 1
    elif fraction <= 2:
        nice_fraction = 2
    elif fraction <= 5:
        nice_fraction = 5
    else:
        nice_fraction = 10

    return nice_fraction * power
