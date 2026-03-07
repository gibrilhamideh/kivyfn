from __future__ import annotations
from typing import TYPE_CHECKING

from kivy.app import App
from kivy.lang import Builder

from kivyfn.resources import app_resource
from kivyfn.i18n import i18n
from kivyfn.fonts import fonts
from kivyfn.state import store
from kivyfn.settings import AppSettings

if TYPE_CHECKING:
    from .config import AppConfig


Builder.load_string(
    """
#: import Factory kivy.factory.Factory
#: import store kivyfn.state.store
#: import Address kivyfn.state.Address
#: import tr kivyfn.i18n.i18n

"""
)


class FnApp(App):
    def __init__(self, config: AppConfig, **kwargs):
        super().__init__(**kwargs)

        self.config = config
        self.settings: AppSettings

        self._bootstrap()

    # -------------------------------------------------
    # Bootstrap
    # -------------------------------------------------

    def _bootstrap(self):
        self._load_settings()
        self._load_fonts()
        self._load_i18n()
        self._load_store()

    # -------------------------------------------------
    # Boot Steps
    # -------------------------------------------------
    def _load_settings(self):
        self.settings = AppSettings()

    def _load_fonts(self):
        fonts.load()

    def _load_i18n(self):
        locales_dir = self.config.locales_dir or app_resource("resources", "locales")

        i18n.configure(locales_dir)

        language = self.settings.get("language", "en")

        i18n.load(language)

    def _load_store(self):
        if not self.config.builder:
            return

        root_node, store_config = self.config.builder.build()

        store.configure(root_node, store_config)
        store.boot()
