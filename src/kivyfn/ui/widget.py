from __future__ import annotations

from typing import TYPE_CHECKING, Any, cast
from kivy.app import App
from kivy.properties import (
        BooleanProperty,
        ColorProperty,
)

if TYPE_CHECKING:
    from kivyfn.app import FnApp


class FnWidget:
    attached = BooleanProperty(False)
    display: bool = BooleanProperty(True)
    fg_color = ColorProperty(None, allownone=True)

    _fn_child_order: int = -1
    _fn_attached_uid: int | None = None

    __events__ = ("on_attach", "on_detach")

    # ============================== #
    # External properties 
    # ============================== #
    @property
    def app(self) -> FnApp:
        app = App.get_running_app()
        if app is None:
            raise RuntimeError(
                f"{type(self).__name__} has no running application."
            )

        return cast("FnApp", app)

    # ============================== #
    # LifeCycle
    # ============================== #
    def add_widget(
        self,
        widget: Any,
        *args: Any,
        **kwargs: Any,
    ) -> None:
        self._validate_fn_child(widget)

        super().add_widget(widget, *args, **kwargs)  # pyright: ignore

        self._sync_child_order()

        widget.fbind(
            "display",
            self._on_child_display,
        )

        if not widget.display:
            self._detach_child_canvas(widget)

        uid = self.fbind(  # pyright: ignore
            "attached",
            widget.setter("attached"),
        )
        widget._fn_attached_uid = uid
        widget.attached = self.attached

    def remove_widget(
        self,
        widget: Any,
        *args: Any,
        **kwargs: Any,
    ) -> None:
        if widget not in self.children:  # pyright: ignore
            return

        widget.funbind(
            "display",
            self._on_child_display,
        )

        uid = widget._fn_attached_uid

        if uid is not None:
            self.unbind_uid("attached", uid)  # pyright: ignore
            widget._fn_attached_uid = None

        widget.attached = False

        super().remove_widget(widget, *args, **kwargs)  # pyright: ignore

        widget._fn_child_order = -1
        self._sync_child_order()

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

    def _sync_child_order(self) -> None:
        for index, child in enumerate(self.children):  # pyright: ignore
            child._fn_child_order = index

    def _on_child_display(
        self,
        widget: FnWidget,
        display: bool,
    ) -> None:
        if display:
            self._attach_child_canvas(widget)
        else:
            self._detach_child_canvas(widget)

    # ============================== #
    # Canvas 
    # ============================== #
    def _detach_child_canvas(
        self,
        widget: FnWidget,
    ) -> None:
        canvas = self.canvas  # pyright: ignore
        child_canvas = widget.canvas  # pyright: ignore

        if canvas.indexof(child_canvas) != -1:
            canvas.remove(child_canvas)



    def _attach_child_canvas(
        self,
        widget: FnWidget,
    ) -> None:
        canvas = self.canvas  # pyright: ignore
        child_canvas = widget.canvas  # pyright: ignore

        if canvas.indexof(child_canvas) != -1:
            return

        child_order = widget._fn_child_order

        if child_order < 0:
            return

        children = self.children  # pyright: ignore

        # Children after this widget in `children` are rendered beneath it.
        # Insert immediately above the nearest displayed lower sibling.
        for sibling in children[child_order + 1:]:
            sibling_canvas = sibling.canvas
            sibling_canvas_index = canvas.indexof(sibling_canvas)

            if sibling_canvas_index != -1:
                canvas.insert(
                    sibling_canvas_index + 1,
                    child_canvas,
                )
                return

        # No mounted lower sibling exists. Put this widget at the bottom of
        # the child-canvas region, after canvas.before when it exists.
        canvas.insert(
            1 if canvas.has_before else 0,
            child_canvas,
        )

    # ============================== #
    # Attach Events
    # ============================== #

    def on_attached(self, instance: Any, value: bool) -> None:
        if value:
            self.dispatch("on_attach") # pyright: ignore
        else:
            self.dispatch("on_detach") # pyright: ignore

    def on_attach(self) -> None:
        pass

    def on_detach(self) -> None:
        pass

    # ============================== #
    # Touch Events
    # ============================== #
    def on_touch_down(self, touch: Any) -> bool:
        if not self.display:
            return False

        return bool(super().on_touch_down(touch))  # pyright: ignore


    def on_touch_move(self, touch: Any) -> bool:
        if not self.display:
            return False

        return bool(super().on_touch_move(touch))  # pyright: ignore


    def on_touch_up(self, touch: Any) -> bool:
        if not self.display:
            return False

        return bool(super().on_touch_up(touch))  # pyright: ignore

    # ============================== #
    # Todo
    # ============================== #
    # BUG: inherited text colors do not recompute when a closer ancestor gains or changes fg_color
    # def on_fg_color(self, *_):
    #     self._dispatch_inherited_fg_dirty()
    # def _dispatch_inherited_fg_dirty(self) -> None:
    #     for child in self.children:
    #         if hasattr(child, "on_inherited_fg_dirty"):
    #             child.on_inherited_fg_dirty()
    #         if hasattr(child, "_dispatch_inherited_fg_dirty"):
    #             child._dispatch_inherited_fg_dirty()
