from __future__ import annotations

import logging

from kivyfn.logging.levels import LogLevel
from kivyfn.logging.setup import configure_logging
from kivyfn.logging.multiprocessing import (
    configure_process_logging,
    create_queue_listener,
)

def get_logger(name: str | None = None) -> logging.Logger:
    if not name:
        return logging.getLogger("kivyfn")

    if name.startswith("kivyfn."):
        return logging.getLogger(name)

    return logging.getLogger(f"kivyfn.{name}")


def get_app_logger(name: str | None = None) -> logging.Logger:
    if not name:
        return logging.getLogger("app")

    if name.startswith("app."):
        return logging.getLogger(name)

    return logging.getLogger(f"app.{name}")


__all__ = (
    "LogLevel",
    "configure_logging",
    "configure_process_logging",
    "create_queue_listener",
    "get_logger",
    "get_app_logger",
)
