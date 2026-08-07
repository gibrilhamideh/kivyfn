from __future__ import annotations

from dataclasses import dataclass, field

from .types import ChartValue


@dataclass(slots=True)
class ChartViewport:
    """User-selected chart ranges that override automatic domains."""

    x_min: ChartValue | None = None
    x_max: ChartValue | None = None
    y_ranges: dict[str, tuple[float, float]] = field(
        default_factory=dict,
    )

    @property
    def has_x_range(self) -> bool:
        return self.x_min is not None and self.x_max is not None

    def set_x(
        self,
        minimum: ChartValue,
        maximum: ChartValue,
    ) -> None:
        self.x_min = minimum
        self.x_max = maximum

    def clear_x(self) -> None:
        self.x_min = None
        self.x_max = None

    def set_y(
        self,
        axis_id: str,
        minimum: float,
        maximum: float,
    ) -> None:
        self.y_ranges[axis_id] = minimum, maximum

    def clear_y(self, axis_id: str | None = None) -> None:
        if axis_id is None:
            self.y_ranges.clear()
            return

        self.y_ranges.pop(axis_id, None)

    def reset(self) -> None:
        self.clear_x()
        self.clear_y()
