from __future__ import annotations

from abc import ABC, abstractmethod

from ..errors import ChartAxisError
from ..types import ChartValue


class ChartScale(ABC):
    """Convert chart-domain values to and from scalar screen space."""

    def __init__(self) -> None:
        self.minimum: ChartValue | None = None
        self.maximum: ChartValue | None = None
        self._minimum_scalar = 0.0
        self._maximum_scalar = 1.0

    @abstractmethod
    def to_scalar(self, value: ChartValue) -> float:
        """Convert a supported public value to a scalar."""

    @abstractmethod
    def from_scalar(self, value: float) -> ChartValue:
        """Convert a scalar back to the scale's public value."""

    def set_domain(
        self,
        minimum: ChartValue,
        maximum: ChartValue,
    ) -> None:
        lower = self.to_scalar(minimum)
        upper = self.to_scalar(maximum)

        if upper <= lower:
            raise ChartAxisError(
                "Chart scale maximum must be greater than minimum"
            )

        self.minimum = minimum
        self.maximum = maximum
        self._minimum_scalar = lower
        self._maximum_scalar = upper

    @property
    def scalar_domain(self) -> tuple[float, float]:
        return self._minimum_scalar, self._maximum_scalar

    def normalize(self, value: ChartValue) -> float:
        scalar = self.to_scalar(value)
        span = self._maximum_scalar - self._minimum_scalar
        return (scalar - self._minimum_scalar) / span

    def denormalize(self, value: float) -> ChartValue:
        span = self._maximum_scalar - self._minimum_scalar
        return self.from_scalar(self._minimum_scalar + value * span)

    def transform(
        self,
        value: ChartValue,
        start: float,
        length: float,
    ) -> float:
        return start + self.normalize(value) * length

    def invert(
        self,
        pixel: float,
        start: float,
        length: float,
    ) -> ChartValue:
        if length <= 0:
            raise ChartAxisError(
                "Cannot invert a scale with nonpositive pixel length"
            )

        return self.denormalize((pixel - start) / length)
