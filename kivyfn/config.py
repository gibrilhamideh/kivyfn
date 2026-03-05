from __future__ import annotations
from typing import TYPE_CHECKING, Optional
from dataclasses import dataclass
from pathlib import Path

if TYPE_CHECKING:
    from .state.builder.builder import Builder


@dataclass(slots=True)
class AppConfig:
    """
    Static application configuration.

    These values define how the application is built and started.
    They are NOT persisted and should not change at runtime.
    """

    builder: Optional[Builder] = None
    locales_dir: Path | None = None
    resources_dir: Path | None = None
    settings_path: Path | None = None
    debug: bool = False
