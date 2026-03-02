from __future__ import annotations

from kivy.app import App
from kivy.base import Builder

from kivyfn.resources import app_path
from kivyfn.i18n import i18n
from kivyfn.fonts import fonts

Builder.load_string(
    """
    #: import tr kivyfn.i18n.i18n
    """
)


class FnApp(App):
    def __init__(self, font=None, lang="en", locales_dir=None, **kwargs):
        super().__init__(**kwargs)

        # --- Load Fonts
        fonts.load()
        if font and font != fonts.current:
            fonts.current = font

        # --- Load Locales
        if locales_dir is None:
            locales_dir = app_path("locales")

        i18n.configure(locales_dir)
        i18n.load(lang)
