# kivyfn/ui/feedback/snackbar/snackbar.py

from __future__ import annotations

from kivy.uix.widget import Widget
from kivyfn.ui.widget import FnWidget


class FnSnackbar(FnWidget, Widget):
    """
    Base class for snackbar widgets.

    The default implementation opens and dismisses immediately.

    Subclasses may override `open()` and `dismiss()` to provide custom
    presentation behavior. Overridden methods must call `dispatch_open()`
    and `dispatch_dismiss()` when their presentation has completed.
    """

    __events__ = (
        "on_open",
        "on_dismiss",
    )

    def open(self) -> None:
        """
        Open the snackbar immediately.

        Animated subclasses should override this method and call
        `dispatch_open()` after the opening animation completes.
        """
        self.dispatch_open()

    def dismiss(self) -> None:
        """
        Dismiss the snackbar immediately.

        Animated subclasses should override this method and call
        `dispatch_dismiss()` after the dismissal animation completes.
        """
        self.dispatch_dismiss()

    def dispatch_open(self) -> None:
        self.dispatch("on_open")

    def dispatch_dismiss(self) -> None:
        self.dispatch("on_dismiss")

    def on_open(self) -> None:
        pass

    def on_dismiss(self) -> None:
        pass
