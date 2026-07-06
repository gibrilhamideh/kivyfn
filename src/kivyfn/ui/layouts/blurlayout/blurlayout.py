from __future__ import annotations

from kivy.properties import BooleanProperty, NumericProperty
from kivy.uix.effectwidget import (
    EffectWidget,
    HorizontalBlurEffect,
    VerticalBlurEffect,
)

from kivyfn.ui.widget import FnWidget


class FnBlurLayout(FnWidget, EffectWidget):
    blur_enabled = BooleanProperty(True)
    blur_size = NumericProperty(8)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.bind(
            blur_enabled=self._refresh_effects,
            blur_size=self._refresh_effects,
        )
        self._refresh_effects()

    def _refresh_effects(self, *_):
        if not self.blur_enabled or self.blur_size <= 0:
            self.effects = []
            return

        size = float(self.blur_size)

        self.effects = [
            HorizontalBlurEffect(size=size),
            VerticalBlurEffect(size=size),
        ]
