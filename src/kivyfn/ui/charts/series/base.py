from __future__ import annotations

from collections.abc import Callable, Iterable
from typing import Any
from uuid import uuid4

from ..data import ChartDataset, NormalizedData
from ..data.validation import normalize_data
from ..errors import ChartSeriesError
from ..types import (
    DuplicatePolicy,
    InvalidDataPolicy,
    OrderingPolicy,
    ValueFormatter,
    ValueSelector,
)


SeriesCallback = Callable[["ChartSeries"], None]


class ChartSeries:
    """Stateful public series containing data and visual configuration."""

    kind = "base"

    def __init__(
        self,
        *,
        id: str | None = None,
        label: str = "",
        data: ChartDataset | Iterable[Any] = (),
        x: ValueSelector = 0,
        y: ValueSelector = 1,
        x_axis: str = "x",
        y_axis: str = "y",
        color: tuple[float, float, float, float] | None = None,
        visible: bool = True,
        value_formatter: ValueFormatter | None = None,
        invalid: InvalidDataPolicy = "gap",
        duplicates: DuplicatePolicy = "last",
        ordering: OrderingPolicy = "sort",
    ) -> None:
        if id is not None and not id:
            raise ChartSeriesError("Series id cannot be empty")

        if not x_axis or not y_axis:
            raise ChartSeriesError("Series axis ids cannot be empty")

        self.id = id or f"series-{uuid4()}"
        self.label = label or self.id
        self.x = x
        self.y = y
        self.x_axis = x_axis
        self.y_axis = y_axis
        self.color = _validate_color(color)
        self.visible = bool(visible)
        self.value_formatter = value_formatter
        self.invalid = _validate_choice(
            "invalid",
            invalid,
            {"raise", "drop", "gap"},
        )
        self.duplicates = _validate_choice(
            "duplicates",
            duplicates,
            {"raise", "first", "last", "average"},
        )
        self.ordering = _validate_choice(
            "ordering",
            ordering,
            {"require", "sort"},
        )

        self._callbacks: list[SeriesCallback] = []
        self._normalized_revision = -1
        self._normalized: NormalizedData | None = None
        self._data = _as_dataset(data)
        self._data.subscribe(self._on_data)

    @property
    def data(self) -> ChartDataset:
        return self._data

    @data.setter
    def data(self, value: ChartDataset | Iterable[Any]) -> None:
        replacement = _as_dataset(value)

        if replacement is self._data:
            return

        self._data.unsubscribe(self._on_data)
        self._data = replacement
        self._data.subscribe(self._on_data)
        self._invalidate()

    def normalize(self) -> NormalizedData:
        if self._normalized_revision == self.data.revision:
            assert self._normalized is not None
            return self._normalized

        normalized = normalize_data(
            self.data,
            x=self.x,
            y=self.y,
            invalid=self.invalid,
            duplicates=self.duplicates,
            ordering=self.ordering,
        )
        self._normalized = normalized
        self._normalized_revision = self.data.revision
        return normalized

    def append(self, x: Any, y: Any) -> None:
        """Append one tuple point to a tuple-configured series."""
        if self.x != 0 or self.y != 1:
            raise ChartSeriesError(
                "append(x, y) requires the default tuple selectors; "
                "append a source row to series.data instead"
            )

        self.data.append((x, y))

    def extend(self, points: Iterable[tuple[Any, Any]]) -> None:
        if self.x != 0 or self.y != 1:
            raise ChartSeriesError(
                "extend(points) requires the default tuple selectors; "
                "extend series.data with source rows instead"
            )

        self.data.extend(points)

    def replace(self, points: Iterable[Any]) -> None:
        self.data.replace(points)

    def clear(self) -> None:
        self.data.clear()

    def subscribe(self, callback: SeriesCallback) -> None:
        if callback not in self._callbacks:
            self._callbacks.append(callback)

    def unsubscribe(self, callback: SeriesCallback) -> None:
        if callback in self._callbacks:
            self._callbacks.remove(callback)

    def notify_changed(self) -> None:
        self._invalidate()

    def format_value(self, value: float | None) -> str:
        if value is None:
            return "—"

        if self.value_formatter is None:
            return str(value)

        result = self.value_formatter(value)
        if not isinstance(result, str):
            raise ChartSeriesError(
                f"Formatter for series {self.id!r} must return str"
            )

        return result

    def _on_data(self, dataset: ChartDataset) -> None:
        self._invalidate()

    def _invalidate(self) -> None:
        self._normalized_revision = -1
        self._normalized = None

        for callback in tuple(self._callbacks):
            callback(self)


def _as_dataset(value: ChartDataset | Iterable[Any]) -> ChartDataset:
    if isinstance(value, ChartDataset):
        return value

    return ChartDataset(value)


def _validate_color(
    value: tuple[float, float, float, float] | None,
) -> tuple[float, float, float, float] | None:
    if value is None:
        return None

    if len(value) != 4:
        raise ChartSeriesError("Series color must contain four channels")

    color = tuple(float(channel) for channel in value)
    if any(channel < 0 or channel > 1 for channel in color):
        raise ChartSeriesError(
            "Series color channels must be between 0 and 1"
        )

    return color


def _validate_choice(
    name: str,
    value: Any,
    options: set[str],
) -> Any:
    if value not in options:
        expected = ", ".join(sorted(options))
        raise ChartSeriesError(
            f"Series {name} must be one of {expected}; got {value!r}"
        )

    return value
