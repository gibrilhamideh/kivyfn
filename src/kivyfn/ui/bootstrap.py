# kivyfn/ui/bootstrap.py
from __future__ import annotations

from kivy.lang import Builder
from kivyfn.runtime.context import FnBootstrapContext
from kivyfn.ui.paths import UI_FONT_PATH

_bootstrapped = False


def bootstrap(ctx: FnBootstrapContext) -> None:
    global _bootstrapped

    if _bootstrapped:
        return
    _bootstrapped = True

    _load_fonts(ctx)
    _register_widgets()
    _register_kv_globals()


def _load_fonts(ctx: FnBootstrapContext) -> None:

    ctx.fonts.register(
        name="FnIcons",
        fn_regular=str(UI_FONT_PATH / "Material-Design-Icons.ttf"),
    )

    ctx.fonts.register(
        name="NotoSansMono",
        fn_regular=str(UI_FONT_PATH / "NotoSansMono-Bold.ttf"),
        fn_bold=str(UI_FONT_PATH / "NotoSansMono-Bold.ttf"),
    )


def _register_widgets() -> None:
    from .factory import register
    register()

def _register_kv_globals():
    Builder.load_string(
        """
        #: import md_icons kivyfn.ui.constants.icons.md_icons

    """
    )
