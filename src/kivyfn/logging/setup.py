# kivyfn/logging/setup.py
from __future__ import annotations
from typing import TYPE_CHECKING


from pathlib import Path
from types import TracebackType

from kivyfn.logging.formatter import FnFormatter
from kivyfn.logging.levels import install_trace_level, resolve_level

import logging
import sys

if TYPE_CHECKING:
    from kivyfn.config.logging import FnLoggingConfig


class StderrCapture:
    def __init__(
        self,
        logger: logging.Logger,
        original,
    ) -> None:
        self.logger = logger
        self.original = original
        self.buffer = ""

    def write(self, text: str) -> int:
        self.buffer += text

        while "\n" in self.buffer:
            line, self.buffer = self.buffer.split("\n", 1)

            if line.strip():
                self.logger.warning(line)

        return len(text)

    def flush(self) -> None:
        if self.buffer.strip():
            self.logger.warning(self.buffer.rstrip())
            self.buffer = ""

        self.original.flush()

    def isatty(self) -> bool:
        return False


def configure_logging(config: FnLoggingConfig) -> None:
    install_trace_level()

    root = logging.getLogger()
    root.handlers.clear()
    root.disabled = False
    root.setLevel(resolve_level(config.level))

    if not config.enabled:
        root.disabled = True
        return

    if config.console.enabled:
        console_handler = logging.StreamHandler()
        console_handler.setLevel(resolve_level(config.console.level))
        console_handler.setFormatter(
            FnFormatter(use_colors=config.console.use_colors)
        )
        root.addHandler(console_handler)

    if config.file.enabled:
        if config.file.directory is None:
            path = Path(config.file.filename)
        else:
            directory = Path(config.file.directory)
            directory.mkdir(parents=True, exist_ok=True)
            path = directory / config.file.filename

        file_handler = logging.FileHandler(path, encoding="utf-8")
        file_handler.setLevel(resolve_level(config.file.level))
        file_handler.setFormatter(FnFormatter(use_colors=False))
        root.addHandler(file_handler)

    for name, level in config.resolved_loggers().items():
        logging.getLogger(name).setLevel(resolve_level(level))

    if config.install_exception_hook:
        install_exception_hook()

    if config.capture_stderr:
        install_stderr_capture()


def install_exception_hook() -> None:
    logger = logging.getLogger("kivyfn.exception")

    def hook(
        exc_type: type[BaseException],
        exc_value: BaseException,
        exc_traceback: TracebackType | None,
    ) -> None:
        if issubclass(exc_type, KeyboardInterrupt):
            sys.__excepthook__(exc_type, exc_value, exc_traceback)
            return

        logger.critical(
            "Unhandled exception",
            exc_info=(exc_type, exc_value, exc_traceback),
        )

    sys.excepthook = hook


def install_stderr_capture() -> None:
    if isinstance(sys.stderr, StderrCapture):
        return

    original = sys.__stderr__

    if original is None:
        return

    sys.stderr = StderrCapture(
        logging.getLogger("stderr"),
        original,
    )
