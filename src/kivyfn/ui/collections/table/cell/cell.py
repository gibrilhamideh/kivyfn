from __future__ import annotations

from kivy.uix.stencilview import StencilView
from kivy.uix.boxlayout import BoxLayout
from kivy.properties import StringProperty, AliasProperty

from kivyfn.ui.widget import FnWidget
from kivyfn.ui.behaviors.style import FnBackgroundBehavior, FnBorderBehavior
from kivyfn.ui.collections.table.protocol import TableContentProtocol


class FnTableCell(FnBorderBehavior, FnBackgroundBehavior, FnWidget, BoxLayout, StencilView):
    row_id: str | None = StringProperty(None)
    column_key: str = StringProperty(None)

    def _get_content(self):
        if self.children:
            return self.children[0]

        return None

    content: TableContentProtocol = AliasProperty(_get_content, None, bind=["children"])

    __events__ = ("on_press",)

    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)

    def set_table_content(self, value):
        self.content.set_table_content(value, row_id=self.row_id)

    def add_widget(self, widget, *args, **kwargs):
        if len(self.children) > 0:
            raise ValueError("cell can only have one child!")

        return super().add_widget(widget, *args, **kwargs)

    def on_touch_down(self, touch):
        if not self.collide_point(*touch.pos):
            return super().on_touch_down(touch)

        self.dispatch("on_press")
        return True

    def on_press(self):
        pass
