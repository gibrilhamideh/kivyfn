from __future__ import annotations

from typing import Any

from .base import SeriesRenderer
from .context import RenderContext


__all__ = (
    "LineRenderer",
    "RenderContext",
    "SeriesRenderer",
)


def __getattr__(name: str) -> Any:
    if name == "LineRenderer":
        from .line import LineRenderer

        return LineRenderer

    raise AttributeError(name)
