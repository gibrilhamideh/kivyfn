from __future__ import annotations

from collections.abc import Iterable
from datetime import datetime, timedelta, timezone
from math import isfinite

from ..errors import ChartAxisError
from ..types import ChartValue
from .base import ChartScale


class DateTimeScale(ChartScale):
    """Continuous scale for naive or timezone-aware datetimes."""

    def __init__(self) -> None:
        super().__init__()
        self._timezone = None

    def set_domain(
        self,
        minimum: ChartValue,
        maximum: ChartValue,
    ) -> None:
        self.prepare_values((minimum, maximum))
        super().set_domain(minimum, maximum)

    def prepare_values(
        self,
        values: Iterable[ChartValue],
    ) -> None:
        candidates = tuple(values)
        if not candidates:
            self._timezone = None
            return

        self._set_exemplar(candidates[0])
        for value in candidates[1:]:
            self._validate_awareness(value)

    def to_scalar(self, value: ChartValue) -> float:
        if not isinstance(value, datetime):
            raise ChartAxisError(
                "Datetime axes require datetime values"
            )

        if value.tzinfo is None:
            epoch = datetime(1970, 1, 1)
            scalar = (value - epoch).total_seconds()
        else:
            scalar = value.astimezone(timezone.utc).timestamp()

        if not isfinite(scalar):
            raise ChartAxisError("Datetime value is outside usable range")

        return scalar

    def from_scalar(self, value: float) -> datetime:
        if self._timezone is not None:
            return datetime.fromtimestamp(value, tz=self._timezone)

        return datetime(1970, 1, 1) + timedelta(seconds=value)

    def _set_exemplar(self, value: ChartValue) -> None:
        if not isinstance(value, datetime):
            raise ChartAxisError(
                "Datetime axes require datetime values"
            )

        self._timezone = value.tzinfo

    def _validate_awareness(self, value: ChartValue) -> None:
        if not isinstance(value, datetime):
            raise ChartAxisError(
                "Datetime axes require datetime values"
            )

        if (value.tzinfo is None) != (self._timezone is None):
            raise ChartAxisError(
                "Datetime domains cannot mix naive and aware values"
            )
