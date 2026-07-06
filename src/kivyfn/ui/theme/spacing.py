# kivyfn.ui.theme.spacing.py
from __future__ import annotations

from kivy.event import EventDispatcher
from kivy.metrics import dp
from kivy.properties import NumericProperty


class ThemeSpacing(EventDispatcher):
    x0 = NumericProperty(dp(0))
    x1 = NumericProperty(dp(4))
    x2 = NumericProperty(dp(8))
    x3 = NumericProperty(dp(12))
    x4 = NumericProperty(dp(16))
    x5 = NumericProperty(dp(20))
    x6 = NumericProperty(dp(24))
    x7 = NumericProperty(dp(32))
    x8 = NumericProperty(dp(40))
    x9 = NumericProperty(dp(48))
    x10 = NumericProperty(dp(64))

    def get(self, value: str) -> float:
        return getattr(self, value)
