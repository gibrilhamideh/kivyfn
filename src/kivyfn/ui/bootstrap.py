# kivyfn/ui/bootstrap.py
from __future__ import annotations

from kivy.lang import Builder

from kivyfn.app import FnApp
from kivyfn.ui.paths import UI_FONT_PATH


_bootstrapped = False


def bootstrap() -> None:
    global _bootstrapped

    if _bootstrapped:
        return

    _bootstrapped = True

    _load_fonts()
    _register_widgets()
    _register_kv_globals()


def _load_fonts() -> None:
    fonts = FnApp.fonts

    fonts.register(
        name="FnIcons",
        fn_regular=(
            UI_FONT_PATH
            / "Material-Design-Icons.ttf"
        ),
    )

    fonts.register(
        name="NotoSansMono",
        fn_regular=(
            UI_FONT_PATH
            / "NotoSansMono-Regular.ttf"
        ),
        fn_bold=(
            UI_FONT_PATH
            / "NotoSansMono-Bold.ttf"
        ),
    )


def _register_widgets() -> None:
    from kivyfn.ui.factory import register

    register()


def _register_kv_globals() -> None:
    Builder.load_string(
        """
        #: import md_icons kivyfn.ui.constants.icons.md_icons
        #: import FnApp kivyfn.app.FnApp
        """
    )
