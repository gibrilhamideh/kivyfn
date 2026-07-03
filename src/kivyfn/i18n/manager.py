from __future__ import annotations

from json import JSONDecodeError, load as json_load
from pathlib import Path
from typing import Any

from kivy.event import EventDispatcher
from kivy.properties import StringProperty


class I18n(EventDispatcher):
    lang = StringProperty("en")

    def __init__(
        self,
        locales_dir: Path,
        lang: str = "en",
    ) -> None:
        super().__init__()

        self.locales_dir = locales_dir
        self._translations: dict[str, Any] = {}

        self.load(lang)

    def __call__(
        self,
        key: str,
        **params: Any,
    ) -> str:
        template = self._resolve(
            key,
        )

        if template is None:
            return f"<{key}>"

        if not params:
            return template

        try:
            return template.format(**params)
        except Exception:
            return template

    def load(
        self,
        lang: str,
    ) -> None:
        file_path = self.locales_dir / f"{lang}.json"

        if not file_path.exists():
            raise FileNotFoundError(
                f"Translation file not found: {file_path}"
            )

        try:
            with open(file_path, "r", encoding="utf-8") as f:
                translations = json_load(f)
        except JSONDecodeError as exc:
            raise ValueError(
                f"Invalid JSON translation file: {file_path}"
            ) from exc

        if not isinstance(translations, dict):
            raise ValueError(
                f"Invalid translation file format: {file_path}"
            )

        self._translations = translations
        self.lang = lang

    def _resolve(
        self,
        key: str,
    ) -> str | None:
        value: Any = self._translations

        for part in key.split("."):
            if not isinstance(value, dict):
                return None

            value = value.get(part)

            if value is None:
                return None

        if not isinstance(value, str):
            return None

        return value
