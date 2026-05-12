from __future__ import annotations

import os
from dataclasses import dataclass, field


@dataclass(slots=True)
class FnEnvironmentConfig:
    kivy_log_mode: str = "PYTHON"
    custom: dict[str, str] = field(default_factory=dict)

    def apply(self) -> None:
        os.environ["KIVY_LOG_MODE"] = self.kivy_log_mode

        for key, value in self.custom.items():
            os.environ[key] = value
