# kivyfn/i18n/manager.py
from __future__ import annotations

from json import JSONDecodeError, load as json_load
from pathlib import Path
from typing import Any

from kivy.event import EventDispatcher
from kivy.properties import StringProperty

from kivyfn.logging import get_logger

from .ref import I18nRef


logger = get_logger(__name__)


class I18n(EventDispatcher):
    lang = StringProperty("en")

    def __init__(
        self,
        locales_dir: Path | None = None,
        lang: str = "en",
    ) -> None:
        super().__init__()

        self.locales_dir = locales_dir
        self._translations: dict[str, Any] = {}
        self._loaded = False
        self.lang = lang

        if locales_dir is None:
            logger.warning(
                "I18n has no locales directory configured"
            )
            return

        self.load(lang)

    @property
    def loaded(self) -> bool:
        return self._loaded

    def __call__(
        self,
        key: str,
        **params: Any,
    ) -> str:
        template = self._resolve(key)

        if template is None:
            return f"<{key}>"

        if not params:
            return template

        resolved_params = {
            name: self._resolve_param(value)
            for name, value in params.items()
        }

        try:
            return template.format(**resolved_params)
        except Exception:
            return template

    def load(
        self,
        lang: str,
    ) -> None:
        locales_dir = self.locales_dir

        if locales_dir is None:
            logger.warning(
                "Cannot load language %r because no locales "
                "directory is configured",
                lang,
            )
            return

        file_path = locales_dir / f"{lang}.json"

        if not file_path.exists():
            logger.warning(
                "Translation file not found: %s",
                file_path,
            )

            self._translations = {}
            self._loaded = False
            self.lang = lang
            return

        try:
            with file_path.open(
                "r",
                encoding="utf-8",
            ) as file:
                translations = json_load(file)
        except JSONDecodeError as error:
            raise ValueError(
                f"Invalid JSON translation file: {file_path}"
            ) from error

        if not isinstance(translations, dict):
            raise ValueError(
                f"Invalid translation file format: {file_path}"
            )

        self._translations = translations
        self._loaded = True
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

    def _resolve_param(
        self,
        value: Any,
    ) -> Any:
        if isinstance(value, I18nRef):
            return self(
                value.key,
                **value.params,
            )

        return value
