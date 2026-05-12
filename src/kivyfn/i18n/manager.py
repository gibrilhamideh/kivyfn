from __future__ import annotations

from json import JSONDecodeError, load as json_load
from pathlib import Path
from typing import Any

from kivy.event import EventDispatcher
from kivy.properties import StringProperty


class I18n(EventDispatcher):
    lang = StringProperty("en")

    def __init__(self, locales_dir: Path, lang: str = "en") -> None:
        super().__init__()
        self.locales_dir = locales_dir
        self._translations: dict[str, str] = {}

        self.load(lang)

    def __call__(self, key: str, lang: str, **params: Any) -> str:
        template = self._translations.get(key, key)

        if not params:
            return template

        try:
            return template.format(**params)
        except Exception:
            return template

    def load(self, lang: str) -> None:
        if self.locales_dir is None:
            return

        file_path = self.locales_dir / f"{lang}.json"

        if not file_path.exists():
            raise FileNotFoundError(f"Translation file not found: {file_path}")

        try:
            with open(file_path, "r", encoding="utf-8") as f:
                translations = json_load(f)
        except JSONDecodeError:
            return

        if not isinstance(translations, dict):
            raise ValueError(f"Invalid translation file format: {file_path}")

        self._translations = translations
        self.lang = lang
