from __future__ import annotations


from kivy.metrics import dp
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.scrollview import ScrollView
from kivy.properties import ObjectProperty, NumericProperty


from kivyfn.ui.widget import FnWidget
from kivyfn.ui.collections.table.cell import FnTableCell
from kivyfn.ui.behaviors.style import (
    FnBackgroundBehavior,
    FnElevationBehavior,
    FnBorderBehavior,
)


class FnTableHeader(
    FnElevationBehavior, FnBackgroundBehavior, FnBorderBehavior, FnWidget, ScrollView
):
    content: BoxLayout = ObjectProperty()
    spacing: int = NumericProperty()

    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)

        self.size_hint_y = None
        self.height = dp(48)
        self.do_scroll = (False, False)

        self.content = BoxLayout()
        self.content.orientation = "horizontal"
        self.content.size_hint_x = None
        self.content.bind(minimum_width=self.content.setter("width"))

        self.bind(spacing=self.content.setter("spacing"))
        super().add_widget(self.content)

    def add_widget(self, widget, *args, **kwargs):
        self.content.add_widget(widget)

    def remove_widget(self, widget, *args, **kwargs):
        self.content.remove_widget(widget)

    def clear_widgets(self, children=None):
        self.content.clear_widgets()

    @property
    def cells(self) -> dict[str, FnTableCell]:
        if self.content is None:
            return {}

        return {cell.column_key: cell for cell in self.content.children}
