# kivyfn.ui.theme.theme.py
from kivy.event import EventDispatcher
from kivy.properties import ObjectProperty

from kivyfn.ui.theme.color import ThemeColor
from kivyfn.ui.theme.spacing import ThemeSpacing


class Theme(EventDispatcher):
    color = ObjectProperty(None)
    spacing = ObjectProperty(None)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.color = ThemeColor()
        self.spacing = ThemeSpacing()
