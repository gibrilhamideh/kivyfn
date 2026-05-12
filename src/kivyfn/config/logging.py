from __future__ import annotations
from typing import Literal
from dataclasses import dataclass

from kivy.config import Config

LogLevel = Literal[
    "trace",
    "debug",
    "info",
    "warning",
    "error",
    "critical",
]
"""
Logging level.
"""


@dataclass(slots=True)
class FnLoggingConfig:
    enabled: bool = True
    """
    Enable file logging.
    """

    level: LogLevel = "info"
    """
    Logging level.

    Supported values:
    - "trace"
    - "debug"
    - "info"
    - "warning"
    - "error"
    - "critical"
    """

    maxfiles: int = 100
    """
    Maximum number of stored log files.
    """

    directory: str = ""
    """
    Log directory path.

    An empty string uses the Kivy default directory.
    """

    name: str = ""
    """
    Log filename format.

    An empty string uses the Kivy default format.
    """

    def apply(self) -> None:
        Config.set("kivy", "log_enable", str(int(self.enabled)))
        Config.set("kivy", "log_level", self.level)
        Config.set("kivy", "log_maxfiles", str(self.maxfiles))

        if self.directory:
            Config.set("kivy", "log_dir", self.directory)

        if self.name:
            Config.set("kivy", "log_name", self.name)
