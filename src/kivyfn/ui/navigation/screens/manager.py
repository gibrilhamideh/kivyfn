from __future__ import annotations
from typing import Literal, Iterator
from kivy.uix.screenmanager import ScreenManager
from kivy.properties import (
    OptionProperty,
    DictProperty,
    ObjectProperty,
    StringProperty
)

from kivyfn.ui.widget import FnWidget
from kivyfn.ui.navigation.screens.screen import FnScreen
from kivyfn.ui.navigation.screens.splash import FnSplashScreen


class FnScreenManager(FnWidget, ScreenManager):
    initial_screen: str | None = StringProperty(None, allownone=True)
    splashscreen: FnSplashScreen | None = ObjectProperty(None, allownone=True)
    splashscreen_class: type[FnSplashScreen] = ObjectProperty(None)
    screen_classes: dict[str, type[FnScreen]] = DictProperty()
    mode: Literal["lazy", "request"] = OptionProperty(
        "lazy", options=["lazy", "request"]
    )

    __events__ = ("on_complete", )

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._current_index = 0
        self._current_name = ""

        self._kv_posted = False
        self._stack = []
        self._screens_iter: Iterator[tuple[str, type[FnScreen]]] | None = None

    def start(self):
        self._screens_iter = iter(self.screen_classes.items())

        if not self.screen_classes:
            raise ValueError(
                "FnScreenManager.start() called with no registered screens."
            )

        if self.mode == "request" and not self.splashscreen_class:
            self.dispatch("on_complete")
            return

        if self.splashscreen_class:
            self.splashscreen = self.splashscreen_class()
            super().add_widget(self.splashscreen)

            self.splashscreen.bind(on_ready=self.on_splash_ready)
            self.splashscreen.start(self._get_len_screens())

        else:
            entry = self._next_screen_entry()
            if entry:
                name, screen_cls = entry
                self.build(name, screen_cls)
            else:
                raise ValueError(
                    "FnScreenManager.start() called with no registered screens."
                )

    def build(self, name, screen_cls: type[FnScreen]):
        if self.has_screen(name):
            raise RuntimeError(
                f"Screen '{name}' has already been built. "
                "Each screen may only be built once."
            )

        screen = screen_cls(name=name)
        if self.mode == "lazy":
            screen.bind(on_ready=self.on_screen_ready)

        super().add_widget(screen)
        screen.on_build()

    def navigate(self, name: str):
        if not self._stack or self._stack[-1] != name:
            self._stack.append(name)

        if self.mode == "request":
            if not self.has_screen(name):
                if name not in self.screen_classes:
                    raise ValueError(f"Screen '{name}' is not registered.")
                screen_cls = self.screen_classes[name]
                self.build(name, screen_cls)

        self.current = name

    def back(self):
        if len(self._stack) < 2:
            return

        self._stack.pop()
        name = self._stack[-1]

        self.current = name

    def register(self, name: str, screen_cls: type[FnScreen]):
        if name in self.screen_classes:
            existing = self.screen_classes[name]
            raise ValueError(
                f"Screen '{name}' is already registered with {existing.__name__}. "
                f"Attempted to register {screen_cls.__name__}."
            )

        self.screen_classes[name] = screen_cls

    def add_widget(self, widget, index=0, canvas=None):
        if not self._kv_posted:
            raise RuntimeError(
                "Screens must be registered using register() in FnScreenManager"
            )
        return super().add_widget(widget, index, canvas)

    # ======================================== #
    # events
    # ======================================== #
    def on_screen_ready(self, *_):
        entry = self._next_screen_entry()

        if entry:
            name, screen_cls = entry
            self.build(name, screen_cls)
            if self.splashscreen:
                self.splashscreen.update(self._current_name, self._current_index)
        else:
            if self.splashscreen:
                super().remove_widget(self.splashscreen)
                self.splashscreen = None

            self.dispatch("on_complete")

    def on_splash_ready(self, *_):
        if self.mode == "lazy":
            entry = self._next_screen_entry()
            if entry:
                name, screen_cls = entry
                self.build(name, screen_cls)
        else:
            if self.splashscreen:
                super().remove_widget(self.splashscreen)
                self.splashscreen = None

            self.dispatch("on_complete")

    def on_kv_post(self, base_widget):
        super().on_kv_post(base_widget)
        self._kv_posted = True

        if self.screen_classes:
            self.start()

    def on_complete(self, *_):
        """ Fires when all screens are loaded. Navigates to the initial target. """
        if self.initial_screen and self.initial_screen in self.screen_classes:
            self.navigate(self.initial_screen)
        elif self.screen_classes:
            first_screen_name = list(self.screen_classes.keys())[0]
            self.navigate(first_screen_name)


    # ======================================== #
    # helpers
    # ======================================== #
    def _next_screen_entry(self) -> tuple[str, type[FnScreen]] | None:
        if self._screens_iter is None:
            return None

        try:
            name, screen_cls = next(self._screens_iter)
            self._current_index += 1
            self._current_name = name
            return name, screen_cls
        except StopIteration:
            return None

    def _get_len_screens(self):
        return len(self.screen_classes)
