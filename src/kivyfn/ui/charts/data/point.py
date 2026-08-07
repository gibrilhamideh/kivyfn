from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from ..types import ChartValue


@dataclass(slots=True, frozen=True)
class ChartPoint:
    """One normalized point retained by a chart series."""

    x: ChartValue
    y: float | None
    source: Any = None
    source_index: int = -1

    @property
    def is_gap(self) -> bool:
        return self.y is None
