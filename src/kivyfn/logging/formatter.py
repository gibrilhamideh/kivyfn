from __future__ import annotations

import asyncio
import copy
import logging
import os
import shutil
import sys
import textwrap
import traceback
from types import TracebackType
from typing import Any


RESET = "\033[0m"

TOKYO_COLORS: dict[str, str] = {
    "blue": "\033[38;2;122;162;247m",
    "cyan": "\033[38;2;125;207;255m",
    "green": "\033[38;2;158;206;106m",
    "purple": "\033[38;2;187;154;247m",
    "red": "\033[38;2;247;118;142m",
    "yellow": "\033[38;2;224;175;104m",
    "orange": "\033[38;2;255;158;100m",
    "gray": "\033[38;2;86;95;137m",
    "white": "\033[38;2;192;202;245m",
    "muted": "\033[38;2;128;140;202m",
}

LEVEL_COLORS: dict[str, str] = {
    "TRACE": TOKYO_COLORS["purple"],
    "DEBUG": TOKYO_COLORS["cyan"],
    "INFO": TOKYO_COLORS["green"],
    "WARNING": TOKYO_COLORS["yellow"],
    "ERROR": TOKYO_COLORS["red"],
    "CRITICAL": "\033[1;38;2;247;118;142m",
}

SHUTDOWN_EXCEPTION_TYPES = (
    KeyboardInterrupt,
    asyncio.CancelledError,
)


def supports_color() -> bool:
    if os.environ.get("NO_COLOR"):
        return False

    return any(
        hasattr(stream, "isatty") and stream.isatty()
        for stream in (sys.stderr, sys.stdout)
    )


def colorize(text: str, color: str, enabled: bool) -> str:
    if not enabled:
        return text

    code = TOKYO_COLORS.get(color)

    if code is None:
        return text

    return f"{code}{text}{RESET}"


def colorize_level(text: str, levelname: str, enabled: bool) -> str:
    if not enabled:
        return text

    code = LEVEL_COLORS.get(levelname)

    if code is None:
        return text

    return f"{code}{text}{RESET}"


def is_shutdown_exception(exc: BaseException | None) -> bool:
    return isinstance(exc, SHUTDOWN_EXCEPTION_TYPES)


def is_shutdown_exception_type(exc_type: type[BaseException] | None) -> bool:
    if exc_type is None:
        return False

    return issubclass(exc_type, SHUTDOWN_EXCEPTION_TYPES)


class FnShutdownNoiseFilter(logging.Filter):
    """
    Removes normal shutdown noise from logs.

    This prevents Ctrl+C / asyncio cancellation from being shown as if it
    was an application crash.
    """

    def filter(self, record: logging.LogRecord) -> bool:
        if record.exc_info is not None:
            exc_type, exc_value, _ = record.exc_info

            if is_shutdown_exception_type(exc_type):
                return False

            if is_shutdown_exception(exc_value):
                return False

        message = record.getMessage()

        if "CancelledError" in message and "asyncio" in record.name:
            return False

        return True


class FnFormatter(logging.Formatter):
    def __init__(
        self,
        *,
        use_colors: bool = True,
        width: int | None = None,
    ) -> None:
        super().__init__(datefmt="%Y-%m-%d %H:%M:%S")

        self.use_colors = use_colors and supports_color()
        self.width = width

    def format(self, record: logging.LogRecord) -> str:
        copied = copy.copy(record)

        copied.message = copied.getMessage()
        copied.asctime = self.formatTime(copied, self.datefmt)

        levelname = copied.levelname
        raw_prefix = self._raw_prefix(copied)
        prefix = self._colored_prefix(copied)

        content_width = self._content_width(len(raw_prefix))
        message = self._format_message(copied.message, content_width)

        if self.use_colors:
            message = colorize_level(message, levelname, True)

        output = prefix + message

        if copied.exc_info:
            output += "\n" + self.formatException(copied.exc_info)

        if copied.stack_info:
            output += "\n" + self.formatStack(copied.stack_info)

        return output

    def _raw_prefix(self, record: logging.LogRecord) -> str:
        return (
            f"[{record.levelname:<8}] "
            f"{record.asctime} "
            f"[{record.processName}] "
            f"[{record.name:<24}] "
        )

    def _colored_prefix(self, record: logging.LogRecord) -> str:
        if not self.use_colors:
            return self._raw_prefix(record)

        level = colorize_level(f"[{record.levelname:<8}]", record.levelname, True)
        time = colorize(str(record.asctime), "gray", True)
        process = colorize(f"[{record.processName}]", "purple", True)
        name = colorize(f"[{record.name:<24}]", "cyan", True)

        return f"{level} {time} {process} {name} "

    def _terminal_width(self) -> int:
        if self.width is not None:
            return self.width

        return shutil.get_terminal_size((120, 20)).columns

    def _content_width(self, prefix_width: int) -> int:
        return max(40, self._terminal_width() - prefix_width)

    def _format_message(self, message: str, width: int) -> str:
        wrapped_lines: list[str] = []

        for line in message.splitlines() or [""]:
            if not line.strip():
                wrapped_lines.append("")
                continue

            wrapped_lines.append(
                textwrap.fill(
                    line,
                    width=width,
                    subsequent_indent="    ",
                    break_long_words=False,
                    break_on_hyphens=False,
                )
            )

        return "\n".join(wrapped_lines)

    def formatException(self, ei: Any) -> str:
        exc_type, exc_value, exc_tb = ei

        lines: list[str] = []
        frames = traceback.extract_tb(exc_tb)

        lines.append("")
        lines.append(colorize("  Traceback", "purple", self.use_colors))
        lines.append(colorize("  " + "─" * 72, "gray", self.use_colors))

        for frame in frames:
            lines.extend(self._format_frame(frame))

        lines.append(colorize("  Error", "red", self.use_colors))
        lines.append(colorize("  " + "─" * 72, "gray", self.use_colors))
        lines.append(self._format_error(exc_type, exc_value))

        return "\n".join(lines)

    def _format_frame(self, frame: traceback.FrameSummary) -> list[str]:
        lines: list[str] = []

        lines.append(
            "  "
            + colorize("[path] ", "blue", self.use_colors)
            + colorize(frame.filename, "white", self.use_colors)
        )

        lines.append(
            "  "
            + colorize("[line] ", "cyan", self.use_colors)
            + colorize(str(frame.lineno), "white", self.use_colors)
        )

        lines.append(
            "  "
            + colorize("[func] ", "purple", self.use_colors)
            + colorize(frame.name, "white", self.use_colors)
        )

        if frame.line:
            lines.append(
                "  "
                + colorize("[code] ", "yellow", self.use_colors)
                + colorize(frame.line.strip(), "white", self.use_colors)
            )

        lines.append("")
        return lines

    def _format_error(
        self,
        exc_type: type[BaseException],
        exc_value: BaseException,
    ) -> str:
        error_name = getattr(exc_type, "__name__", str(exc_type))
        error_message = str(exc_value)

        if error_message:
            return (
                "  "
                + colorize(error_name, "red", self.use_colors)
                + colorize(": ", "gray", self.use_colors)
                + colorize(error_message, "white", self.use_colors)
            )

        return "  " + colorize(error_name, "red", self.use_colors)


def install_logging(
    *,
    level: int = logging.INFO,
    use_colors: bool = True,
) -> None:
    """
    Installs the formatter on the root logger.

    Call this once near the start of your application.
    """

    handler = logging.StreamHandler()
    handler.setFormatter(FnFormatter(use_colors=use_colors))
    handler.addFilter(FnShutdownNoiseFilter())

    root = logging.getLogger()
    root.handlers.clear()
    root.addHandler(handler)
    root.setLevel(level)


def install_exception_hooks(
    *,
    logger_name: str = "kivyfn.exception",
) -> None:
    """
    Installs global exception hooks.

    Normal shutdown exceptions are ignored:
    - KeyboardInterrupt
    - asyncio.CancelledError

    Real unhandled exceptions are logged using FnFormatter.
    """

    logger = logging.getLogger(logger_name)

    def excepthook(
        exc_type: type[BaseException],
        exc_value: BaseException,
        exc_tb: TracebackType | None,
    ) -> None:
        if is_shutdown_exception_type(exc_type):
            return

        logger.critical(
            "Unhandled exception",
            exc_info=(exc_type, exc_value, exc_tb),
        )

    def unraisablehook(unraisable: Any) -> None:
        exc_type = unraisable.exc_type
        exc_value = unraisable.exc_value
        exc_tb = unraisable.exc_traceback

        if is_shutdown_exception_type(exc_type):
            return

        message = "Unhandled unraisable exception"

        if unraisable.err_msg:
            message = str(unraisable.err_msg)

        if unraisable.object is not None:
            message = f"{message}: {unraisable.object!r}"

        logger.critical(
            message,
            exc_info=(exc_type, exc_value, exc_tb),
        )

    sys.excepthook = excepthook
    sys.unraisablehook = unraisablehook


def install_asyncio_exception_handler(
    loop: asyncio.AbstractEventLoop | None = None,
    *,
    logger_name: str = "asyncio",
) -> None:
    """
    Installs an asyncio exception handler.

    This keeps asyncio cancellation during shutdown from printing ugly logs.
    """

    logger = logging.getLogger(logger_name)

    if loop is None:
        loop = asyncio.get_event_loop()

    def handler(
        loop: asyncio.AbstractEventLoop,
        context: dict[str, Any],
    ) -> None:
        exception = context.get("exception")

        if is_shutdown_exception(exception):
            return

        message = context.get("message", "Unhandled asyncio exception")

        if (
            isinstance(message, str)
            and message == "Task was destroyed but it is pending!"
            and loop.is_closed()
        ):
            return

        if isinstance(exception, BaseException):
            logger.error(message, exc_info=exception)
            return

        logger.error(message)

    loop.set_exception_handler(handler)


def setup_fn_logging(
    *,
    level: int = logging.INFO,
    use_colors: bool = True,
    install_hooks: bool = True,
) -> None:
    """
    One-call setup for your app.

    Use this near the very beginning of main.py before Kivy starts logging.
    """

    install_logging(level=level, use_colors=use_colors)

    if install_hooks:
        install_exception_hooks()
