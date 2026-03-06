from __future__ import annotations
from typing import Literal, Iterator
from kivy.uix.screenmanager import ScreenManager
from kivy.properties import (
    OptionProperty,
    DictProperty,
    AliasProperty,
    ObjectProperty,
)

from ..primitives.widget import FnWidget

from .screen import FnScreen
from .splash import FnSplashScreen


class FnScreenManager(FnWidget, ScreenManager):
    splashscreen: FnSplashScreen | None = ObjectProperty(None)
    splashscreen_class: type[FnSplashScreen] = ObjectProperty(None)
    screen_classes: dict[str, type[FnScreen]] = DictProperty()
    mode: Literal["instant", "request", "startup"] = OptionProperty(
        "instant", options=["instant", "request", "startup"]
    )

    def _get_len_screens(self):
        return len(self.screen_classes)

    number_of_screens = AliasProperty(_get_len_screens, None, bind=("routes",))

    _current_index = 0
    _current_name = ""

    _kv_posted = False
    _stack = []
    _screens_iter: Iterator[tuple[str, type[FnScreen]]] | None = None

    def start(self):
        if self.splashscreen_class:
            self.splashscreen = self.splashscreen_class()
            self.add_widget(self.splashscreen)

            self.splashscreen.bind(on_ready=self.on_splash_ready)  # pyright: ignore
            self.splashscreen.start(self.number_of_screens)

        self._screens_iter = iter(self.screen_classes.items())

        if self.mode == "instant":
            for name, screen_cls in self.screen_classes.items():
                self.build(name, screen_cls)

        elif self.mode == "startup":
            pass

    def build(self, name, screen_cls: type[FnScreen]):
        screen = screen_cls(name=name)
        screen.bind(on_ready=self.on_screen_ready)  # pyright: ignore

        self.add_widget(screen)
        screen.on_build()

    def navigate(self, name: str):
        if not self._stack or self._stack[-1] != name:
            self._stack.append(name)

        if self.mode == "request":
            if not self.has_screen(name):
                screen_cls = self.screen_classes[name]
                self.build(name, screen_cls)

        self.current = name
        self._stack.append(name)

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
        if self.splashscreen is None:
            entry = self._next_screen_entry()
            if entry:
                name, screen_cls = entry
                self.build(name, screen_cls)
        else:
            self.splashscreen.update(self._current_name, self._current_index)

    def on_splash_ready(self, *_):
        entry = self._next_screen_entry()
        if entry:
            name, screen_cls = entry
            self.build(name, screen_cls)

    def on_kv_post(self, base_widget):
        self._kv_posted = True

        for name, screen_cls in self.screen_classes.items():
            self.register(name, screen_cls)

        self.start()

        return super().on_kv_post(base_widget)

    # ======================================== #
    # helpers
    # ======================================== #
    def _next_screen_entry(self) -> tuple[str, type[FnScreen]] | None:
        if self._screens_iter is None:
            return None

        try:
            return next(self._screens_iter)
        except StopIteration:
            return None
