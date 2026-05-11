from __future__ import annotations

from json import load as json_load, JSONDecodeError

from pathlib import Path
from typing import Any

from kivy.event import EventDispatcher
from kivy.properties import StringProperty


class I18n(EventDispatcher):
    """
    Internationalization manager.

    - Explicit language loading via `load(lang)`
    - Reactive via `lang` Property
    - KV binding support via `tr("key", tr.lang)`
    """

    lang = StringProperty("en")

    def __init__(self) -> None:
        super().__init__()
        self._base_path: Path | None = None
        self._translations: dict[str, str] = {}

    # -----------------------------------------------------
    # Translation Call
    # -----------------------------------------------------
    def __call__(self, key: str, lang: str, **params: Any) -> str:
        """
        Translate key.

        `lang` parameter exists purely for KV dependency binding.
        The active language is always `self.lang`.
        """
        template = self._translations.get(key, key)

        if not params:
            return template

        try:
            return template.format(**params)
        except Exception:
            return template

    # -----------------------------------------------------
    # Configuration
    # -----------------------------------------------------
    def configure(self, base_path: str | Path) -> None:
        self._base_path = Path(base_path)

    # -----------------------------------------------------
    # Explicit Load
    # -----------------------------------------------------
    def load(self, lang: str) -> None:
        """
        Explicitly load a language file.
        Only updates `self.lang` after successful load.
        """

        #TODO: remove raising exeptions and put loggers

        if not self._base_path:
            raise RuntimeError("i18n base_path not configured")

        file_path = self._base_path / f"{lang}.json"

        if not file_path.exists():
            raise FileNotFoundError(f"Translation file not found: {file_path}")

        # 1️⃣ Load file first (no state mutation yet)
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                translations = json_load(f)
        except JSONDecodeError:
            return

        # Optional validation
        if not isinstance(translations, dict):
            raise ValueError(f"Invalid translation file format: {file_path}")

        # 2️⃣ Commit only after success
        self._translations = translations
        self.lang = lang  # triggers KV re-evaluation
