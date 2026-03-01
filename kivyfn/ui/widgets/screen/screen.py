from __future__ import annotations
from typing import TYPE_CHECKING, cast

if TYPE_CHECKING:
    from kivycore.components.navigation import KcNavigation
    from main import MainApp

import os
from kivy.base import Builder
from kivy.clock import Clock
from kivy.uix.screenmanager import Screen
from kivy.properties import ColorProperty, ObjectProperty

from paths import kivycore_path

with open(
    os.path.join(kivycore_path, "components", "screen", "screen.kv"), encoding="utf-8"
) as kv_file:
    Builder.load_string(kv_file.read())


class KcScreen(Screen):
    app = cast("MainApp", ObjectProperty())
    """
    Reference to the App instance.
    
    :attr:`app` is a :class:`~kivy.properties.ObjectProperty`
    """
    navigation: KcNavigation = ObjectProperty()
    """
    Reference to the KcNavigation instance.

    :attr:`navigation` is a :class:`~kivy.properties.ObjectProperty`
    """

    bg_color: list = ColorProperty([0, 0, 0, 0])
    """
    Background color of the screen.

    :attr:`bg_color` is a :class:`~kivy.properties.ColorProperty`
    """

    def __init__(self, **kw):
        super().__init__(**kw)
        Clock.schedule_once(lambda dt: self.next_screen())

    def next_screen(self, *args):
        self.navigation.next_screen()
