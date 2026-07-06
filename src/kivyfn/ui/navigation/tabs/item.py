from __future__ import annotations
from typing import Protocol, TYPE_CHECKING

from kivy.app import ObjectProperty
from kivy.properties import BooleanProperty, NumericProperty
from kivy.uix.widget import Widget

from kivyfn.ui.widget import FnWidget
from kivyfn.ui.behaviors.input.touch import FnTouchBehavior

if TYPE_CHECKING:
    from kivyfn.ui.layouts.tabs.toolbar import FnTabToolbar


class FnTabItemProtocl(Protocol):
    tab_selected: bool


class FnTabItem(FnTouchBehavior, FnWidget, Widget):
    selected: bool = BooleanProperty(False)
    toolbar: FnTabToolbar = ObjectProperty()
    index: int = NumericProperty(None)

    def __init__(self, index: int, **kwargs):
        super().__init__(**kwargs)

        self.index = index

    def on_kv_post(self, base_widget: Widget) -> None:
        self.size_hint_x = None
        return super().on_kv_post(base_widget)

    def add_widget(self, widget: Widget, index: int = 0, canvas=None) -> None:
        widget.tab_selected = self.selected  # pyright: ignore
        widget.bind(width=self.setter("width"))
        self.bind(
            selected=widget.setter("tab_selected"),
            pos=widget.setter("pos"),
            height=widget.setter("height"),
        )
        return super().add_widget(widget, index, canvas)

    def on_touch_down(self, touch):
        touched = super().on_touch_down(touch)
        if touched:
            self.toolbar.on_tab_selected(self)

        return False
