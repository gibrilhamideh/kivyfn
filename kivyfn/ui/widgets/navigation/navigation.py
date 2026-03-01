from __future__ import annotations
from typing import TYPE_CHECKING, Type, Iterator

if TYPE_CHECKING:
    from kivycore.components.splash import KcSplashScreen

import os
from kivy.base import Builder
from kivy.animation import Animation
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.screenmanager import ScreenManager
from kivy.properties import (
    StringProperty,
    BooleanProperty,
    NumericProperty,
    ColorProperty,
    ObjectProperty,
)

from kivycore.components.appbar import KcAppBar

from paths import kivycore_path

with open(
    os.path.join(kivycore_path, "components", "navigation", "navigation.kv"),
    encoding="utf-8",
) as kv_file:
    Builder.load_string(kv_file.read())


class KcView(BoxLayout):
    """
    The root layout for the navigation component.
    :attr:`layout` is a :class:`~kivy.uix.boxlayout.BoxLayout`
    """

    pass


class KcNavigation(FloatLayout):
    splash_image: str = StringProperty(
        os.path.join(kivycore_path, "resources", "images", "kivy.png")
    )
    """
    The splash screen instance.
    :attr:`splash` is a :class:`~kivy.properties.ObjectProperty`
    """

    splash_screen: KcSplashScreen = ObjectProperty()
    """
    The splash screen instance.

    :attr:`splash_screen` is a :class:`~kivy.properties.ObjectProperty`
    """

    progress_bar_color: list = ColorProperty([1, 1, 1, 1])
    """
    Color of the loading bar.

    :attr:`progress_bar_color` is a :class:`~kivy.properties.ColorProperty`
    """

    progress_bar_bg_color: list = ColorProperty([1, 1, 1, 0.2])
    """
    Background color of the loading bar.

    :attr:`progress_bar_bg_color` is a :class:`~kivy.properties.ColorProperty`
    """

    progress_bar_limit: int = NumericProperty(0)
    """
    Total number of screens to be loaded.

    :attr:`progress_bar_limit` is a :class:`~kivy.properties.NumericProperty`
    """

    appbar: KcAppBar = ObjectProperty()
    """
    The app bar instance.

    :attr:`appbar` is a :class:`~kivy.properties.ObjectProperty`
    """

    layout: KcView = ObjectProperty()
    """
    The root layout instance.

    :attr:`layout` is a :class:`~kivy.properties.ObjectProperty`
    """

    last_screen: str = StringProperty(None)
    """
    The name of the last screen.

    :attr:`last_screen` is a :class:`~kivy.properties.StringProperty`
    """

    screen_manager: ScreenManager = ObjectProperty()
    """
    The ScreenManager instance that manages the screens.
    :attr:`screen_manager` is a :class:`~kivy.properties.ObjectProperty`
    """

    screens: list = ObjectProperty()
    """
    List of screen classes to be managed by the ScreenManager.

    :attr:`screens` is a :class:`~kivy.properties.ObjectProperty`
    """

    bg_color: list = ColorProperty([0, 0, 0, 0])
    """
    Background color of the root layout.
    :attr:`bg_color` is a :class:`~kivy.properties.ColorProperty`
    """

    animation_duration: float = NumericProperty(0.25)
    """
    Duration of the animation for progress bar transitions between screen.

    :attr:`animation_duration` is a :class:`~kivy.properties.NumericProperty`
    """

    _animation_in_progress: bool = BooleanProperty(False)
    """
    Indicates if an animation is currently in progress.

    :attr:`animation_in_progress` is a :class:`~kivy.properties.BooleanProperty`
    """

    _current_index: int = NumericProperty(0)
    """
    The current index of the loading screen.

    :attr:`current_index` is a :class:`~kivy.properties.NumericProperty`
    """

    _done_loading: bool = BooleanProperty(False)
    """
    Indicates if the animation is done.

    :attr:`_done_loading` is a :class:`~kivy.properties.BooleanProperty`
    """

    _last_loaded: str = StringProperty()
    """
    The last loaded screen instance.

    :attr:`last_loaded` is a :class:`~kivy.properties.StringProperty`
    """

    __events__ = ("on_complete",)

    def __init__(self, **kw):
        super().__init__(**kw)

    # --------------------------------
    # Lazy Loading Screens
    # --------------------------------
    def start(self):
        self.screens_iter = iter(self.screens)
        self.progress_bar_limit = len(list(self.screens))
        self.next_screen()

    def next_screen(self):
        if self._animation_in_progress or self._done_loading:
            return

        try:
            self._current_index += 1
            self._animate_progress_bar()

            instance = next(self.screens_iter)()
            setattr(instance, "navigation", self)
            self.screen_manager.add_widget(instance)
            self._last_loaded = instance.name

        except StopIteration:
            self._done_loading = True
            if self.appbar:
                Animation(opacity=1, d=self.animation_duration).start(self.appbar)

            if self.last_screen:
                self.change_screen(self.last_screen)
            else:
                self.change_screen(self._last_loaded)

            self.dispatch("on_complete")

    def _animation_complete(self, *args):
        if self._animation_in_progress:
            self._animation_in_progress = False
            self.next_screen()

    def _animate_progress_bar(self):
        anim = Animation(value=self._current_index, duration=self.animation_duration)
        anim.bind(on_complete=self._animation_complete)
        anim.start(self.splash_screen.progress_bar)
        self._animation_in_progress = True

    # --------------------------------
    # Screen Management
    # --------------------------------
    def change_screen(self, name: str):
        self.screen_manager.current = name

    # --------------------------------
    # Events
    # --------------------------------
    def on_complete(self, *args):
        pass

    # --------------------------------
    # add widget
    # --------------------------------
    def add_widget(self, widget, *args):
        if isinstance(widget, KcView):
            self.layout = widget
            return super().add_widget(widget, *args)

        if isinstance(widget, KcAppBar):
            self.appbar = widget
            widget.opacity = 0
            anchor = getattr(widget, "anchor")
            if anchor == "top":
                return self.layout.add_widget(widget, index=1)
            else:
                return self.layout.add_widget(widget)

        return super().add_widget(widget, *args)
