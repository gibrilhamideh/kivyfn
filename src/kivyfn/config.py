from __future__ import annotations
from dataclasses import dataclass
from pathlib import Path


@dataclass(slots=True)
class AppConfig:
    app_dir: Path

    resources_dir: Path | None = None
    locales_dir: Path | None = None
    settings_path: Path | None = None
    debug: bool = False

    def __post_init__(self):
        if self.resources_dir is None:
            self.resources_dir = self.app_dir / "resources"

        if self.locales_dir is None:
            self.locales_dir = self.resources_dir / "locales"

        if self.settings_path is None:
            self.settings_path = self.app_dir / "settings.json"
