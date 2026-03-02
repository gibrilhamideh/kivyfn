from __future__ import annotations
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from kivycore.components.progress import KcProgressBar
import os
from kivy.base import Builder
from kivy.uix.screenmanager import Screen
from kivy.properties import StringProperty, ColorProperty, ObjectProperty, NumericProperty

from paths import kivycore_path

with open(
    os.path.join(kivycore_path, "components", "splash", "splash.kv"), encoding="utf-8"
) as kv_file:
    Builder.load_string(kv_file.read())


class KcSplashScreen(Screen):
    image: str = StringProperty()
    '''
    The source path of the splash image.
    :attr:`image` is a :class:`~kivy.properties.StringProperty`
    '''

    bg_color = ColorProperty([0, 0, 0, 0])
    '''
    Background color of the splash screen.

    :attr:`bg_color` is a :class:`~kivy.properties.ColorProperty`
    '''

    progress_bar: KcProgressBar = ObjectProperty()
    '''
    The progress bar widget instance.
    :attr:`progress_bar` is a :class:`~kivy.properties.ObjectProperty`
    '''

    progress_bar_color: list = ColorProperty([1, 1, 1, 1])
    '''
    Color of the loading bar.

    :attr:`progress_bar_color` is a :class:`~kivy.properties.ColorProperty`
    '''

    progress_bar_bg_color: list = ColorProperty([1, 1, 1, 0.2])
    '''
    Background color of the loading bar.

    :attr:`progress_bar_bg_color` is a :class:`~kivy.properties.ColorProperty`
    '''

    progress_bar_limit: int = NumericProperty(100)
    '''
    The maximum value of the progress bar.

    :attr:`progress_bar_limit` is a :class:`~kivy.properties.NumericProperty`
    '''
