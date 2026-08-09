# kivyfn/logging/multiprocessing.py
from __future__ import annotations

import logging
import sys

from logging.handlers import QueueHandler, QueueListener
from multiprocessing.queues import Queue
from pathlib import Path
from typing import TYPE_CHECKING

from kivyfn.logging.formatter import FnFormatter
from kivyfn.logging.levels import install_trace_level, resolve_level


if TYPE_CHECKING:
    from kivyfn.config.logging import FnLoggingConfig


def create_queue_listener(
    log_queue: Queue,
    config: FnLoggingConfig,
) -> QueueListener:
    install_trace_level()

    handlers: list[logging.Handler] = []

    if config.console.enabled:
        console_handler = logging.StreamHandler(
            stream=sys.__stderr__,
        )
        console_handler.setLevel(
            resolve_level(config.console.level)
        )
        console_handler.setFormatter(
            FnFormatter(
                use_colors=config.console.use_colors,
            )
        )
        handlers.append(console_handler)

    if config.file.enabled:
        if config.file.directory is None:
            path = Path(config.file.filename)
        else:
            directory = Path(config.file.directory)
            directory.mkdir(
                parents=True,
                exist_ok=True,
            )
            path = directory / config.file.filename

        file_handler = logging.FileHandler(
            path,
            encoding="utf-8",
        )
        file_handler.setLevel(
            resolve_level(config.file.level)
        )
        file_handler.setFormatter(
            FnFormatter(
                use_colors=False,
            )
        )
        handlers.append(file_handler)

    return QueueListener(
        log_queue,
        *handlers,
        respect_handler_level=True,
    )


def configure_process_logging(
    log_queue: Queue,
) -> None:
    install_trace_level()

    root = logging.getLogger()
    root.handlers.clear()
    root.disabled = False
    root.setLevel(logging.NOTSET)

    root.addHandler(
        QueueHandler(log_queue)
    )
