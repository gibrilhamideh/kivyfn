from __future__ import annotations
from dataclasses import dataclass
from pathlib import Path


@dataclass(slots=True)
class AppConfig:
    """
    Static application configuration.

    These values define how the application is built and started.
    They are NOT persisted and should not change at runtime.
    """

    locales_dir: Path | None = None
    resources_dir: Path | None = None
    settings_path: Path | None = None
    debug: bool = False
