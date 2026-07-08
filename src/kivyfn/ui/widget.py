from __future__ import annotations

from typing import TYPE_CHECKING, Any, cast
from kivy.app import App
from kivy.properties import BooleanProperty, ColorProperty

if TYPE_CHECKING:
    from kivyfn.base.app import FnBaseApp


class FnWidget:
    attached = BooleanProperty(False)
    fg_color = ColorProperty(None, allownone=True)

    __events__ = ("on_attach", "on_detach")

    @property
    def app(self) -> FnBaseApp:
        app = App.get_running_app()
        if app is None:
            raise RuntimeError(
                f"{type(self).__name__} has no running application."
            )

        return cast("FnBaseApp", app)

    def add_widget(self, widget: Any, *args: Any, **kwargs: Any) -> None:
        self._validate_fn_child(widget)

        super().add_widget(widget, *args, **kwargs) # pyright: ignore

        uid = self.fbind("attached", widget.setter("attached")) # pyright: ignore
        widget._fn_attached_uid = uid
        widget.attached = self.attached

    def remove_widget(self, widget: Any, *args: Any, **kwargs: Any) -> None:
        uid = getattr(widget, "_fn_attached_uid", None)

        if uid is not None:
            self.unbind_uid("attached", uid) # pyright: ignore
            widget._fn_attached_uid = None

        widget.attached = False

        super().remove_widget(widget, *args, **kwargs) # pyright: ignore

    def _validate_fn_child(self, widget: Any) -> None:
        try:
            has_attached = widget.property("attached", quiet=True) is not None
        except AttributeError:
            has_attached = False

        if not has_attached:
            raise TypeError(
                f"{self.__class__.__name__} only accepts FnWidget-compatible children. "
                f"Got {widget.__class__.__name__}. "
                "Every framework widget must inherit from FnWidget."
            )

    def on_attached(self, instance: Any, value: bool) -> None:
        if value:
            self.dispatch("on_attach") # pyright: ignore
        else:
            self.dispatch("on_detach") # pyright: ignore

    def on_attach(self) -> None:
        pass

    def on_detach(self) -> None:
        pass

    # BUG: inherited text colors do not recompute when a closer ancestor gains or changes fg_color
    # def on_fg_color(self, *_):
    #     self._dispatch_inherited_fg_dirty()
    # def _dispatch_inherited_fg_dirty(self) -> None:
    #     for child in self.children:
    #         if hasattr(child, "on_inherited_fg_dirty"):
    #             child.on_inherited_fg_dirty()
    #         if hasattr(child, "_dispatch_inherited_fg_dirty"):
    #             child._dispatch_inherited_fg_dirty()
