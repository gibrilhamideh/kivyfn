from __future__ import annotations

from collections.abc import Iterable
from typing import Any

from .chart import FnChart
from .errors import ChartSeriesError
from .series import ChartSeries, LineSeries


class FnLineChart(FnChart):
    """Convenient FnChart specialization for one or more line series."""

    def __init__(
        self,
        *,
        data: Iterable[Any] | None = None,
        series: Iterable[LineSeries] | None = None,
        label: str = "Series",
        **kwargs: Any,
    ) -> None:
        if data is not None and series is not None:
            raise ChartSeriesError(
                "FnLineChart accepts either data or series, not both"
            )

        configured_series: Iterable[LineSeries]
        if series is not None:
            configured_series = series
        else:
            configured_series = (
                LineSeries(
                    id="line",
                    label=label,
                    data=() if data is None else data,
                ),
            )

        super().__init__(series=configured_series, **kwargs)

    @property
    def primary_series(self) -> LineSeries:
        if not self.series:
            raise ChartSeriesError("FnLineChart has no line series")

        series = self.series[0]
        assert isinstance(series, LineSeries)
        return series

    @property
    def data(self):
        return self.primary_series.data

    def set_data(self, data: Iterable[Any]) -> None:
        self.primary_series.replace(data)

    def add_series(self, series: ChartSeries) -> None:
        if not isinstance(series, LineSeries):
            raise ChartSeriesError(
                "FnLineChart only accepts LineSeries instances"
            )

        super().add_series(series)
