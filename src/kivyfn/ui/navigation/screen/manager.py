# kivyfn/ui/navigation/screens/manager.py
from __future__ import annotations

from typing import Any
from collections.abc import Iterator

from kivy.clock import Clock
from kivy.properties import (
    BooleanProperty,
    ListProperty,
    NumericProperty,
    StringProperty,
    ObjectProperty,
)
from kivy.uix.screenmanager import (
    ScreenManager,
    ScreenManagerException,
)

from kivyfn.ui.navigation.screen.screen import FnScreen
from kivyfn.ui.navigation.screen.splash import FnSplashScreen
from kivyfn.ui.widget import FnWidget


class FnScreenManager(FnWidget, ScreenManager):
    """
    Screen manager with explicit KivyFN startup and screen-build lifecycle.

    Screens are declared normally as children in KV. Kivy constructs and
    adds them immediately, while this manager controls when each screen's
    `build()` method runs.

    Loading policies:

    - eager: build when this manager starts;
    - lazy: build when first presented;
    - the startup target is always built, regardless of its load policy.

    When the first declared screen is an FnSplashScreen, it remains current
    while eager screens initialize. The manager updates its progress and
    switches to the startup target after every startup screen is ready.
    """

    initial_screen: str = StringProperty("")
    loading: bool = BooleanProperty(False)
    loaded: bool = BooleanProperty(False)

    _startup_index = NumericProperty(0)
    _startup_target: FnScreen | None = ObjectProperty()
    _startup_pending: str = StringProperty()
    _startup_screens: list[FnScreen] = ListProperty()
    _startup_total: int = NumericProperty()


    def __init__(
        self,
        **kwargs: Any,
    ) -> None:
        self._screen_order: list[FnScreen] = []
        self._splash_screen: FnSplashScreen | None = None
        self._startup_iterator: Iterator[FnScreen] | None = None

        super().__init__(**kwargs)

    # =================================== #
    # Utilities
    # =================================== #
    def navigate(self, name: str):
        self.current = name

    # =================================== #
    # Widget Management
    # =================================== #

    def add_widget(
        self,
        widget: Any,
        *args: Any,
        **kwargs: Any,
    ) -> None:
        if not isinstance(widget, FnScreen):
            raise TypeError(
                f"{type(self).__name__} only accepts FnScreen children, "
                f"got {type(widget).__name__}"
            )

        if isinstance(widget, FnSplashScreen):
            self._validate_splash(widget)

        super().add_widget(widget, *args, **kwargs)

        if isinstance(widget, FnSplashScreen):
            self._splash_screen = widget

        self._screen_order.append(widget)

    def remove_widget(
        self,
        widget: Any,
        *args: Any,
        **kwargs: Any,
    ) -> None:
        if self.loaded:
            raise RuntimeError("cannot remove screens when loading")

        super().remove_widget(
            widget,
            *args,
            **kwargs,
        )

    def _validate_splash(
        self,
        splash: FnSplashScreen,
    ) -> None:
        if self._splash_screen is not None:
            raise ValueError(
                f"{type(self).__name__} can contain only "
                "one FnSplashScreen"
            )

        if self._screen_order:
            raise ValueError(
                f"FnSplashScreen {splash.name!r} must be "
                "the first screen added to its manager"
            )

    # =================================== #
    # Screen Resolution
    # =================================== #

    def _resolve_initial_screen(
        self,
        target: str | None = None,
    ) -> FnScreen:
        name = target or self.initial_screen

        if name:
            screen = self._require_screen(name)

            if isinstance(screen, FnSplashScreen):
                raise ValueError(
                    f"Initial screen {name!r} cannot be "
                    "an FnSplashScreen"
                )

            return screen

        for screen in self._screen_order:
            if not isinstance(screen, FnSplashScreen):
                return screen

        raise RuntimeError(
            f"{type(self).__name__} has no non-splash screen"
        )

    def _resolve_startup_screens(
        self,
        target: FnScreen,
    ) -> list[FnScreen]:
        screens: list[FnScreen] = []

        for screen in self._screen_order:
            if isinstance(screen, FnSplashScreen):
                continue

            if screen.load == "eager":
                screens.append(screen)

        if target not in screens:
            screens.append(target)

        return screens

    def _require_screen(
        self,
        name: str,
    ) -> FnScreen:
        try:
            screen = self.get_screen(name)
        except ScreenManagerException as error:
            raise KeyError(
                f"{type(self).__name__} has no screen "
                f"named {name!r}"
            ) from error

        return screen

    # =================================== #
    # Startup
    # =================================== #
    def start(
        self,
    ) -> None:
        """
        Start this manager.

        `target` overrides `initial_screen` for this startup. This allows
        FnNavigationManager to start a nested manager directly on the screen
        required by a deeper navigation path.
        """

        if self.loading or self.loaded:
            raise RuntimeError("FnScreenManager has already started.")

        startup_target = self._resolve_initial_screen()
        startup_screens = self._resolve_startup_screens(
            startup_target,
        )
        self._startup_iterator = iter(startup_screens)

        self.loading = True

        self._startup_target = startup_target
        self._startup_screens = startup_screens
        self._startup_total = len(startup_screens)

        splash = self._splash_screen
        if splash is not None:
            self._start_with_splash(splash)
            return

        self._start_without_splash()


    def _start_with_splash(
        self,
        splash: FnSplashScreen,
    ) -> None:
        self._setup_splash_screen(splash)
        self._begin_startup_loading()


    def _start_without_splash(self) -> None:
        self._begin_startup_loading()


    # =================================== #
    # Splash
    # =================================== #
    def _setup_splash_screen(self, screen):
        self.bind(
            _startup_index=screen.setter("loaded"),
            _startup_pending=screen.setter("current_screen"),
            _startup_total=screen.setter("total"),
        )

    # =================================== #
    # Loading
    # =================================== #
    def _begin_startup_loading(self) -> None:
        self._startup_iterator = iter(self._startup_screens)
        self._load_next_screen()

    def _load_next_screen(
        self,
        *_: Any,
    ) -> None:
        iterator = self._startup_iterator

        if iterator is None:
            raise RuntimeError(
                "Startup iterator has not been initialized"
            )

        try:
            screen = next(iterator)
        except StopIteration:
            self._finish_startup()
            return

        self._startup_pending = screen.name
        if screen.is_ready:
            self._finish_pending(screen)
            return

        screen.bind(on_ready=self._finish_pending)
        screen._build()

    def _finish_pending(
        self,
        screen: FnScreen,
    ) -> None:
        screen.unbind(on_ready=self._finish_pending)

        self._startup_index += 1
        self._load_next_screen()


    def _finish_startup(self) -> None:
        target = self._startup_target

        if target is None:
            raise RuntimeError(
                f"{type(self).__name__} has no startup target"
            )

        self.current = target.name
        self.loaded = True
        self.loading = False
        Clock.schedule_once(self._cleanup, 0.1)

    def _cleanup(self, *_):

        self._startup_iterator = None
        self._startup_target = None
        self._startup_pending = ""
        self._startup_screens = []





