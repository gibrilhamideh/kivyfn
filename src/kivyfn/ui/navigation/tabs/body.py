from __future__ import annotations
from typing import TYPE_CHECKING

from kivy.uix.widget import Widget
from kivy.properties import BooleanProperty, ObjectProperty
from kivy.uix.carousel import Carousel
from kivyfn.ui.widget import FnWidget

if TYPE_CHECKING:
    from kivyfn.ui.layouts.tabs.layout import FnTabs


class FnTabBody(FnWidget, Carousel):
    allow_slide: bool = BooleanProperty()
    layout: FnTabs = ObjectProperty()

    def on_kv_post(self, base_widget: Widget) -> None:
        self.size_hint_y = None
        return super().on_kv_post(base_widget)

    def goto(self, index):
        slide = self.slides[index]
        self.load_slide(slide)

    def on_index(self, *args):
        super().on_index(*args)
        self.layout.on_slide_change(self.index)

    def on_touch_down(self, touch):
        if not self.allow_slide:
            return super(Carousel, self).on_touch_down(touch)
        return super().on_touch_down(touch)

    def on_touch_move(self, touch):
        if not self.allow_slide:
            return super(Carousel, self).on_touch_move(touch)
        return super().on_touch_move(touch)

    def on_touch_up(self, touch):
        if not self.allow_slide:
            return super(Carousel, self).on_touch_up(touch)
        return super().on_touch_up(touch)
