from __future__ import annotations

from typing import Any

from ..errors import ChartAxisError
from ..scale import ChartScale, DateTimeScale, LinearScale
from ..types import AxisSide, ChartValue, ValueFormatter
from .formatter import format_datetime, format_number


class ChartAxis:
    """Public axis configuration paired with one mathematical scale."""

    kind = "base"

    def __init__(
        self,
        *,
        id: str,
        side: AxisSide,
        scale: ChartScale,
        label: str = "",
        unit: str = "",
        minimum: ChartValue | None = None,
        maximum: ChartValue | None = None,
        formatter: ValueFormatter | None = None,
        include_zero: bool = False,
        padding: float = 0.05,
        target_ticks: int = 6,
        grid: bool = True,
        visible: bool = True,
    ) -> None:
        if not id:
            raise ChartAxisError("Axis id cannot be empty")

        if side not in {"bottom", "left", "right", "top"}:
            raise ChartAxisError(f"Unsupported axis side {side!r}")

        if not 0 <= padding <= 1:
            raise ChartAxisError("Axis padding must be between 0 and 1")

        if target_ticks <= 0:
            raise ChartAxisError("Axis target_ticks must be positive")

        self.id = id
        self.side = side
        self.scale = scale
        self.label = label
        self.unit = unit
        self.minimum = minimum
        self.maximum = maximum
        self.formatter = formatter
        self.include_zero = include_zero
        self.padding = float(padding)
        self.target_ticks = int(target_ticks)
        self.grid = bool(grid)
        self.visible = bool(visible)

        if minimum is not None and maximum is not None:
            self.scale.set_domain(minimum, maximum)

    def format(self, value: Any) -> str:
        formatter = self.formatter or str
        text = formatter(value)
        if not isinstance(text, str):
            raise ChartAxisError(
                f"Formatter for axis {self.id!r} must return str"
            )

        return text


class LinearAxis(ChartAxis):
    kind = "linear"

    def __init__(
        self,
        *,
        id: str = "y",
        side: AxisSide = "left",
        formatter: ValueFormatter | None = None,
        **kwargs: Any,
    ) -> None:
        super().__init__(
            id=id,
            side=side,
            scale=LinearScale(),
            formatter=formatter or format_number,
            **kwargs,
        )


class DateTimeAxis(ChartAxis):
    kind = "datetime"

    def __init__(
        self,
        *,
        id: str = "x",
        side: AxisSide = "bottom",
        formatter: ValueFormatter | None = None,
        **kwargs: Any,
    ) -> None:
        if side not in {"bottom", "top"}:
            raise ChartAxisError(
                "Datetime axes are supported only on the horizontal "
                "dimension"
            )

        if kwargs.get("include_zero"):
            raise ChartAxisError(
                "Datetime axes cannot include numeric zero"
            )

        super().__init__(
            id=id,
            side=side,
            scale=DateTimeScale(),
            formatter=formatter or format_datetime,
            **kwargs,
        )
