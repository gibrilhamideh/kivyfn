from __future__ import annotations
from typing import TYPE_CHECKING, Callable

from kivy.event import EventDispatcher
from kivy.properties import StringProperty, ObjectProperty

if TYPE_CHECKING:
    from ..primitives.widget import FnWidget


class FnBinder(EventDispatcher):
    __events__ = ("on_kv_post",)

    owner: FnWidget = ObjectProperty(None)
    name: str = StringProperty(None)
    address: str = StringProperty()
    field: str = StringProperty(None, allownone=True)
    callback = StringProperty(None, allownone=True)
    subscription: Callable = ObjectProperty(None)

    _callback = None

    def __init__(self, **_) -> None:
        super().__init__()

    def apply_class_lang_rules(self, **_):
        pass

    def on_kv_post(self, *_):
        pass

    def on_name(self, *_):
        self.owner._add_binder(self.name, self)

    def on_callback(self, _, callback: str | None):
        if callback is None:
            self._callback = None
            return

        func = getattr(self.owner, callback, None)
        if not callable(func):
            raise ValueError(
                f"Invalid FnBinder callback '{callback}'. "
                f"{type(self.owner).__name__} has no callable method with that name."
            )

        self._callback = func

    def on_address(self, _, address: str):
        pass

    def on_change(self, value):
        if self.field is not None:
            setattr(self.owner, self.field, value)

        if callable(self._callback):
            self._callback(value)
