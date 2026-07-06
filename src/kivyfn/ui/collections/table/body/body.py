from __future__ import annotations

from kivy.app import ObjectProperty
from kivy.uix.scrollview import ScrollView
from kivy.uix.boxlayout import BoxLayout

from kivyfn.ui.widget import FnWidget
from kivyfn.ui.collections.table.cell import FnTableCell


class FnTableBody(FnWidget, ScrollView):
    """
    Scroll content surface for body cells.

    No layout logic lives here.
    FnTable computes and assigns all cell positions/sizes.
    """

    content: BoxLayout = ObjectProperty()

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.content = BoxLayout()
        self.content.orientation = "vertical"
        self.content.size_hint = (None, None)
        self.content.bind(minimum_size=self.content.setter("size"))
        super().add_widget(self.content)

    def add_widget(self, widget, *args, **kwargs):
        self.content.add_widget(widget, *args, **kwargs)

    def remove_widget(self, widget, *args, **kwargs):
        self.content.remove_widget(widget, *args, **kwargs)

    def clear_widgets(self, children=None):
        self.content.clear_widgets(children)

    def add_row(self, cells: list[FnTableCell], height):
        row = BoxLayout(
            orientation="horizontal",
            size_hint=(None, None),
            height=height,
        )

        row.bind(minimum_width=row.setter("width"))

        for cell in cells:
            row.add_widget(cell)

        self.add_widget(row)

    def clear_rows(self):
        self.clear_widgets()
