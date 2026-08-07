from __future__ import annotations

from collections.abc import Iterable

from ..errors import ChartAxisError
from ..scale import DateTimeScale
from ..types import ChartValue
from .axis import ChartAxis


def resolve_domain(
    axis: ChartAxis,
    values: Iterable[ChartValue],
) -> tuple[ChartValue, ChartValue]:
    """Resolve a safe complete domain from data and axis constraints."""
    source_values = list(values)
    fixed_minimum = axis.minimum
    fixed_maximum = axis.maximum
    if isinstance(axis.scale, DateTimeScale):
        axis.scale.prepare_values(
            value
            for value in (
                fixed_minimum,
                fixed_maximum,
                *source_values,
            )
            if value is not None
        )

    scalars = [axis.scale.to_scalar(value) for value in source_values]

    if not scalars and (fixed_minimum is None or fixed_maximum is None):
        lower = 0.0
        upper = 1.0
    else:
        lower = (
            axis.scale.to_scalar(fixed_minimum)
            if fixed_minimum is not None
            else min(scalars)
        )
        upper = (
            axis.scale.to_scalar(fixed_maximum)
            if fixed_maximum is not None
            else max(scalars)
        )

    if axis.include_zero:
        lower = min(lower, 0.0)
        upper = max(upper, 0.0)

    if upper < lower:
        raise ChartAxisError(
            f"Axis {axis.id!r} maximum must be greater than minimum"
        )

    if upper == lower:
        expansion = max(abs(lower) * 0.05, 1.0)
        lower -= expansion
        upper += expansion

    span = upper - lower
    if fixed_minimum is None:
        lower -= span * axis.padding

    if fixed_maximum is None:
        upper += span * axis.padding

    minimum: ChartValue = (
        fixed_minimum
        if fixed_minimum is not None
        else axis.scale.from_scalar(lower)
    )
    maximum: ChartValue = (
        fixed_maximum
        if fixed_maximum is not None
        else axis.scale.from_scalar(upper)
    )
    return minimum, maximum
