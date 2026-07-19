# kivyfn/ui/navigation/screen/screen.py
from __future__ import annotations

from typing import Any, Literal, TypeAlias

from kivy.properties import (
    BooleanProperty,
    OptionProperty,
)
from kivy.uix.screenmanager import Screen

from kivyfn.ui.widget import FnWidget


FnScreenLoad: TypeAlias = Literal[
    "eager",
    "lazy",
]


class FnScreen(FnWidget, Screen):
    load: FnScreenLoad = OptionProperty(
        "eager",
        options=(
            "eager",
            "lazy",
        ),
    )

    is_ready: bool = BooleanProperty(False)

    __events__ = (
        "on_ready",
    )

    def __init__(
        self,
        **kwargs: Any,
    ) -> None:
        self._built = False

        super().__init__(**kwargs)

    @property
    def built(self) -> bool:
        return self._built

    def _build(self) -> None:
        if self._built:
            return

        self._built = True

        try:
            self.build()
        except Exception:
            self._built = False
            raise

    def build(self) -> None:
        """
        Initialize this screen.

        Implementations must call ready() when initialization
        has completed.
        """

    def ready(self) -> None:
        if not self._built:
            raise RuntimeError(
                f"Screen {self.name!r} cannot become ready "
                "before it is built"
            )

        if self.is_ready:
            return

        self.is_ready = True
        self.dispatch("on_ready")

    def on_ready(self) -> None:
        """
        Dispatched when this screen finishes initialization.
        """
