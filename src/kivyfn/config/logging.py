
from __future__ import annotations
from typing import Literal
from dataclasses import dataclass, field

from kivyfn.logging import configure_logging


LogLevel = Literal[
    "trace",
    "debug",
    "info",
    "warning",
    "error",
    "critical",
]


DEFAULT_LOGGERS: dict[str, LogLevel] = {
    "kivy": "warning",
    "kivyfn": "info",
    "app": "info",
}


@dataclass(slots=True)
class FnConsoleLogConfig:
    enabled: bool = True
    """
    Enable console logging.
    """

    level: LogLevel = "info"
    """
    Minimum level written to the console.
    """

    use_colors: bool = True
    """
    Enable colored terminal output when supported.
    """


@dataclass(slots=True)
class FnFileLogConfig:
    enabled: bool = False
    """
    Enable file logging.
    """

    level: LogLevel = "debug"
    """
    Minimum level written to the log file.
    """

    directory: str | None = "logs"
    """
    Directory where log files are stored.

    If None, the filename is used as-is.
    """

    filename: str = "kivyfn.log"
    """
    Log filename.
    """


@dataclass(slots=True)
class FnLoggingConfig:
    enabled: bool = True
    """
    Enable KivyFN logging configuration.
    """

    level: LogLevel = "info"
    """
    Default fallback logging level.

    This applies to the root logger and to loggers that do not have
    a more specific configured level.
    """

    loggers: dict[str, LogLevel] = field(default_factory=dict)
    """
    Logger-specific level overrides.

    These values are merged with KivyFN defaults.

    Example:
        {
            "kivyfn.store": "debug",
            "app.dashboard": "debug",
        }
    """

    console: FnConsoleLogConfig = field(default_factory=FnConsoleLogConfig)
    """
    Console logging configuration.
    """

    file: FnFileLogConfig = field(default_factory=FnFileLogConfig)
    """
    File logging configuration.
    """

    capture_stderr: bool = False
    """
    Redirect sys.stderr writes into the logging system.

    Useful for native warnings and third-party libraries, but should be
    enabled carefully because badly configured stderr handlers can cause loops.
    """

    install_exception_hook: bool = True
    """
    Install a global uncaught-exception hook for the current process.
    """

    def resolved_loggers(self) -> dict[str, LogLevel]:
        """
        Return default logger levels merged with user overrides.

        User-provided loggers win over defaults.
        """
        return {
            **DEFAULT_LOGGERS,
            **self.loggers,
        }

    def apply(self) -> None:
        """
        Apply logging configuration to the current process.

        This should normally be called once during application startup.
        """
        configure_logging(self)

