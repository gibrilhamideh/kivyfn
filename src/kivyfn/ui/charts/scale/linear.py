from __future__ import annotations

from math import isfinite

from ..errors import ChartAxisError
from ..types import ChartValue
from .base import ChartScale


class LinearScale(ChartScale):
    """Continuous scale for finite numeric values."""

    def to_scalar(self, value: ChartValue) -> float:
        if isinstance(value, bool) or not isinstance(value, (int, float)):
            raise ChartAxisError(
                "Linear axes require finite int or float values"
            )

        scalar = float(value)
        if not isfinite(scalar):
            raise ChartAxisError(
                "Linear axes require finite int or float values"
            )

        return scalar

    def from_scalar(self, value: float) -> float:
        return float(value)
