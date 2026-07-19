# kivyfn/ui/navigation/screen/spalsh.py
from __future__ import annotations

from kivy.properties import (
    AliasProperty,
    NumericProperty,
    StringProperty,
)

from kivyfn.ui.navigation.screen.screen import FnScreen


class FnSplashScreen(FnScreen):
    """
    Startup screen displayed while an FnScreenManager builds its eager
    screens.

    FnScreenManager controls these progress properties. Application code
    should normally only read or bind to them.
    """

    total: int = NumericProperty(0)
    loaded: int = NumericProperty(0)
    current_screen: str = StringProperty("")

    def _get_progress(self) -> float:
        if not self.total:
            return 0

        return self.loaded / self.total

    progress: float = AliasProperty(
        _get_progress,
        None,
        bind=["total", "loaded"]
    )

