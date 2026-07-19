from __future__ import annotations
from kivy.uix.widget import Widget
from kivy.uix.relativelayout import RelativeLayout
from kivy.properties import (
    BooleanProperty,
    DictProperty,
    ObjectProperty,
    NumericProperty,
)

from kivyfn.ui.widget import FnWidget
from kivyfn.ui.layouts.tabs.body import FnTabBody
from kivyfn.ui.layouts.tabs.toolbar import FnTabToolbar


class FnTabs(FnWidget, RelativeLayout):
    toolbar: FnTabToolbar = ObjectProperty()
    body: FnTabBody = ObjectProperty()
    content: dict[str, Widget] = DictProperty()

    allow_slide: bool = BooleanProperty(True)
    last_command: int = NumericProperty()

    def on_kv_post(self, base_widget: Widget) -> None:
        self._update_layout()
        self.bind(size=self._update_layout)

        self.body.allow_slide = self.allow_slide
        self.bind(allow_slide=self.body.setter("allow_slide"))
        return super().on_kv_post(base_widget)

    def add_widget(self, widget, *args, **kwargs):
        if isinstance(widget, FnTabToolbar):
            widget.layout = self
            widget.bind(size=self._update_layout)
            self.toolbar = widget
        elif isinstance(widget, FnTabBody):
            widget.layout = self
            self.body = widget
        else:
            raise ValueError(
                "children of FnTabs must be instance of FnTabBody or FnTabToolbar"
            )

        return super().add_widget(widget, *args, **kwargs)

    def goto(self, index):
        self.on_slide_change(index)
        self.body.goto(index)

    def on_slide_change(self, index):
        if self.last_command == index:
            return

        length = len(self.toolbar.items)
        middle = length // 2
        next_index = (index - 1) if index < middle else (index + 1)
        scroll_to = (
            self.toolbar.items[next_index]
            if 0 <= next_index < length
            else self.toolbar.items[index]
        )
        self.toolbar.scroll_to(scroll_to, padding=10)

        tab = self.toolbar.items[index]
        for item in self.toolbar.items:
            if item is tab:
                continue
            item.selected = False

        tab.selected = True
        self.last_command = index

    def _update_layout(self, *args):
        if not self.toolbar or not self.body:
            return

        position = self.toolbar.position

        toolbar_height = self.toolbar.height

        if position == "top":
            # Toolbar at top
            self.toolbar.pos = (0, self.height - toolbar_height)
            self.toolbar.size = (self.width, toolbar_height)

            # Body fills below
            self.body.pos = (0, 0)
            self.body.size = (self.width, self.height - toolbar_height)

        elif position == "bottom":
            # Toolbar at bottom
            self.toolbar.pos = (0, 0)
            self.toolbar.size = (self.width, toolbar_height)

            # Body fills above
            self.body.pos = (0, toolbar_height)
            self.body.size = (self.width, self.height - toolbar_height)

        else:
            raise ValueError("position must be 'top' or 'bottom'")
