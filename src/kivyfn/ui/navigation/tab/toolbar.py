from __future__ import annotations
from typing import Literal, TYPE_CHECKING

from kivy.metrics import dp
from kivy.uix.label import ListProperty
from kivy.uix.scrollview import ScrollView
from kivy.uix.widget import Widget
from kivy.uix.boxlayout import BoxLayout
from kivy.effects.scroll import ScrollEffect
from kivy.properties import OptionProperty, ObjectProperty

from kivyfn.ui.widget import FnWidget
from kivyfn.ui.layouts.tabs.item import FnTabItem
from kivyfn.ui.behaviors.style import (
    FnBackgroundBehavior,
    FnBorderBehavior,
    FnElevationBehavior,
)

if TYPE_CHECKING:
    from kivyfn.ui.layouts.tabs.layout import FnTabs


class FnTabToolbar(
    FnElevationBehavior, FnBackgroundBehavior, FnBorderBehavior, FnWidget, ScrollView
):
    position: Literal["top", "bottom"] = OptionProperty(
        "top", options=["top", "bottom"]
    )

    content: BoxLayout = ObjectProperty()
    layout: FnTabs = ObjectProperty()

    items: list[FnTabItem] = ListProperty()

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.effect_cls = ScrollEffect

        self.size_hint = (None, None)
        self.height = dp(100)

        self.content = BoxLayout()
        self.content.size_hint_x = None
        self.content.bind(minimum_width=self.content.setter("width"))
        super().add_widget(self.content)

    def add_widget(self, widget, *args, **kwargs):
        selected = False
        index = len(self.content.children)
        if index == 0:
            selected = True

        item = FnTabItem(index, selected=selected)
        item.toolbar = self
        item.add_widget(widget)
        self.items.append(item)
        self.content.add_widget(item, *args, **kwargs)

    def remove_widget(self, widget, *args, **kwargs):
        self.content.remove_widget(widget, *args, **kwargs)

    def clear_widgets(self, children: list[Widget] | None = None) -> None:
        self.content.clear_widgets(children)

    def hide_tab(self, tab):
        pass

    def on_tab_selected(self, tab: FnTabItem):
        self.layout.goto(tab.index)
