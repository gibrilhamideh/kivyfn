from __future__ import annotations


class ChartError(Exception):
    """Base exception for every public chart failure."""


class ChartConfigurationError(ChartError):
    """Raised when chart configuration is invalid."""


class ChartDataError(ChartError):
    """Raised when chart input data cannot be normalized."""


class ChartAxisError(ChartConfigurationError):
    """Raised when an axis is missing or invalid."""


class ChartSeriesError(ChartConfigurationError):
    """Raised when a series is missing or invalid."""


class ChartRenderError(ChartError):
    """Raised when validated chart state cannot be rendered."""
