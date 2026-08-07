from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any

from ..series import ChartSeries
from .context import RenderContext


class SeriesRenderer(ABC):
    """Internal rendering contract for one visual series kind."""

    @abstractmethod
    def render(
        self,
        group: Any,
        series: ChartSeries,
        context: RenderContext,
        color: tuple[float, float, float, float],
    ) -> None:
        """Add the series's instructions to one canvas group."""
