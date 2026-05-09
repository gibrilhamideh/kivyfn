from __future__ import annotations

import asyncio
import importlib

from kivy.app import App

from kivyfn.i18n import i18n
from kivyfn.fonts import fonts
from kivyfn.settings import AppSettings
from kivyfn.config import AppConfig


class FnBaseApp(App):
    def __init__(self, config: AppConfig, **kwargs):
        super().__init__(**kwargs)

        self.fnconfig = config
        self.fnsettings: AppSettings
        self._bootstrap()

    # -------------------------------------------------
    # Bootstrap
    # -------------------------------------------------

    def _bootstrap(self):
        self._load_modules()
        self._load_settings()
        self._load_fonts()
        self._load_i18n()

    # -------------------------------------------------
    # Boot Steps
    # -------------------------------------------------
    def _load_settings(self):
        self.settings = AppSettings()

    def _load_fonts(self):
        if self.fnconfig.locales_dir is None:
            return

        path = self.fnconfig.locales_dir / "fonts"
        fonts.load(path)

    def _load_i18n(self):
        locales_dir = self.fnconfig.locales_dir

        if locales_dir is None:
            return

        i18n.configure(locales_dir)
        language = self.settings.get("language", "en")
        i18n.load(language)

    def _load_modules(self):
        self._try_module("kivyfn.bootstrap")
        self._try_module("kivyfn.ui.bootstrap")
        self._try_module("kivyfn.store.bootstrap")

    def _try_module(self, module: str) -> None:
        try:
            m = importlib.import_module(module)
            m.bootstrap()
        except ModuleNotFoundError:
            pass

    # -------------------------------------------------
    # App Helpers
    # -------------------------------------------------
    def create_task(self, coro):
        task = asyncio.create_task(coro)

        def done(t):
            try:
                t.result()
            except asyncio.CancelledError:
                pass
            except Exception as exc:
                print(f"Task failed: {exc!r}")

        task.add_done_callback(done)
        return task
