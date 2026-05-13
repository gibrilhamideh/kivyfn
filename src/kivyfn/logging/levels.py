from __future__ import annotations

import logging
from typing import Any, Literal


TRACE_LEVEL = 9


LogLevel = Literal[
    "trace",
    "debug",
    "info",
    "warning",
    "error",
    "critical",
]


LOG_LEVELS: dict[LogLevel, int] = {
    "trace": TRACE_LEVEL,
    "debug": logging.DEBUG,
    "info": logging.INFO,
    "warning": logging.WARNING,
    "error": logging.ERROR,
    "critical": logging.CRITICAL,
}


def install_trace_level() -> None:
    if not hasattr(logging, "TRACE"):
        logging.addLevelName(TRACE_LEVEL, "TRACE")
        logging.TRACE = TRACE_LEVEL  # pyright: ignore[reportAttributeAccessIssue]

    if not hasattr(logging.Logger, "trace"):

        def trace(
            self: logging.Logger,
            message: object,
            *args: Any,
            **kwargs: Any,
        ) -> None:
            if self.isEnabledFor(TRACE_LEVEL):
                self.log(TRACE_LEVEL, message, *args, **kwargs)

        logging.Logger.trace = trace  # pyright: ignore[reportAttributeAccessIssue]


def resolve_level(level: LogLevel | int) -> int:
    if isinstance(level, int):
        return level

    return LOG_LEVELS[level]
