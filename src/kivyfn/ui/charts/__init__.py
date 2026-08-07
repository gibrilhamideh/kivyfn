from __future__ import annotations

from typing import Any

from .axis import ChartAxis, ChartTick, DateTimeAxis, LinearAxis
from .data import (
    ChartDataset,
    ChartPoint,
    DataDiagnostics,
    NormalizedData,
)
from .errors import (
    ChartAxisError,
    ChartConfigurationError,
    ChartDataError,
    ChartError,
    ChartRenderError,
    ChartSeriesError,
)
from .interaction import (
    ChartInteraction,
    ChartSelection,
    SelectedPoint,
)
from .series import ChartSeries, LineSeries
from .viewport import ChartViewport


__all__ = (
    "ChartAxis",
    "ChartAxisError",
    "ChartConfigurationError",
    "ChartDataError",
    "ChartDataset",
    "ChartError",
    "ChartInteraction",
    "ChartPoint",
    "ChartRenderError",
    "ChartSelection",
    "ChartSeries",
    "ChartSeriesError",
    "ChartTick",
    "ChartViewport",
    "DataDiagnostics",
    "DateTimeAxis",
    "FnChart",
    "FnLineChart",
    "LinearAxis",
    "LineSeries",
    "NormalizedData",
    "SelectedPoint",
)


def __getattr__(name: str) -> Any:
    """Load graphical widgets lazily so the data core remains headless."""
    if name == "FnChart":
        from .chart import FnChart

        return FnChart

    if name == "FnLineChart":
        from .linechart import FnLineChart

        return FnLineChart

    raise AttributeError(name)
