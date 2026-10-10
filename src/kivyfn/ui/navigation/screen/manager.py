# kivyfn/ui/navigation/screens/manager.py
from __future__ import annotations

from typing import Any
from collections.abc import Callable, Iterator
from functools import partial

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
)

from kivyfn.ui.navigation.screen.screen import FnScreen
from kivyfn.ui.navigation.screen.splash import FnSplashScreen
from kivyfn.ui.widget import FnWidget


class FnScreenManager(FnWidget, ScreenManager):
    """
    Screen manager with explicit KivyFN startup and screen-build lifecycle.

    Screens are declared normally as children in KV. Kivy constructs and
    adds them immediately, while this manager controls when each screen's
    `build()` method runs. Use register_screen() to defer construction of
    the entire widget tree until that screen reaches its loading step.

    Loading policies:

    - eager: build when this manager starts;
    - lazy: build when first presented;
    - the startup target is always built, regardless of its load policy.

    When the first declared screen is an FnSplashScreen, it remains current
    while eager screens initialize. The manager updates its progress and
    switches to the startup target after every startup screen is ready.

    Alternatively, set splash_screen to an external FnSplashScreen overlay.
    Its owner controls visibility; this manager supplies progress. Each
    screen is initialized on a separate frame so progress can be drawn.
    """

    __events__ = ("on_startup_failed",)

    initial_screen: str = StringProperty("")
    loading: bool = BooleanProperty(False)
    loaded: bool = BooleanProperty(False)
    splash_screen: FnSplashScreen | None = ObjectProperty(
        None, allownone=True
    )

    _startup_index = NumericProperty(0)
    _startup_target: str = StringProperty("")
    _startup_pending: str = StringProperty()
    _startup_screens: list[str] = ListProperty()
    _startup_total: int = NumericProperty()


    def __init__(
        self,
        **kwargs: Any,
    ) -> None:
        self._screen_order: list[FnScreen | str] = []
        self._screen_factories: dict[str, Callable[[], FnScreen]] = {}
        self._startup_iterator: Iterator[str] | None = None
        self._pending_screen: FnScreen | None = None
        self._started = False
        self._splash_bindings: dict[str, int] = {}

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
            self.splash_screen = widget

        if widget.name in self._screen_factories:
            index = self._screen_order.index(widget.name)
            self._screen_order[index] = widget
        else:
            # KV can assign names after add_widget(). Keep the widget so
            # its eventual name is resolved when startup begins.
            self._screen_order.append(widget)

    def remove_widget(
        self,
        widget: Any,
        *args: Any,
        **kwargs: Any,
    ) -> None:
        if self.loaded:
            raise RuntimeError("cannot remove screens when loading")

        super().remove_widget(widget, *args, **kwargs)
        if widget in self._screen_order:
            self._screen_order.remove(widget)

    def _validate_splash(
        self,
        splash: FnSplashScreen,
    ) -> None:
        if self.splash_screen is not None:
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

    def register_screen(
        self, name: str, factory: Callable[[], FnScreen]
    ) -> None:
        """Register an eager screen without constructing its widget tree.

        The factory must return an FnScreen with the registered name.
        It is called once, after the splash displays that screen's name.
        """
        if self._started:
            raise RuntimeError("Register screens before startup")
        names = [
            item if isinstance(item, str) else item.name
            for item in self._screen_order
        ]
        if not name or name in names:
            raise ValueError(f"Invalid or duplicate screen name: {name!r}")
        self._screen_order.append(name)
        self._screen_factories[name] = factory

    def _resolve_initial_screen(self) -> str:
        name = self.initial_screen
        if name:
            if (
                name not in self._screen_factories
                and not self.has_screen(name)
            ):
                raise KeyError(f"Unknown initial screen: {name!r}")
            if self.has_screen(name) and isinstance(
                self.get_screen(name), FnSplashScreen
            ):
                raise ValueError("The initial screen cannot be a splash")
            return name

        for item in self._screen_order:
            if isinstance(item, str):
                return item
            if not isinstance(item, FnSplashScreen):
                return item.name
        raise RuntimeError(f"{type(self).__name__} has no non-splash screen")

    def _resolve_startup_screens(self, target: str) -> list[str]:
        screens = []
        for item in self._screen_order:
            if isinstance(item, str):
                screens.append(item)
            elif not isinstance(item, FnSplashScreen):
                if item.load == "eager" or item.name == target:
                    screens.append(item.name)
        return screens

    def _require_screen(self, name: str) -> FnScreen:
        if not self.has_screen(name):
            factory = self._screen_factories[name]
            screen = factory()
            if not isinstance(screen, FnScreen) or isinstance(
                screen, FnSplashScreen
            ):
                raise TypeError("Screen factories must return an FnScreen")
            if screen.name != name:
                raise ValueError(f"Screen factory changed its name: {name!r}")
            self.add_widget(screen)
            del self._screen_factories[name]
        return self.get_screen(name)

    # =================================== #
    # Startup
    # =================================== #
    def start(
        self,
    ) -> None:
        """
        Initialize eager screens and the initial target across frames.
        """

        if self._started:
            raise RuntimeError("FnScreenManager has already started.")

        startup_target = self._resolve_initial_screen()
        startup_screens = self._resolve_startup_screens(
            startup_target,
        )
        self._started = True
        self._startup_index = 0
        self._startup_target = startup_target
        self._startup_screens = startup_screens
        self._startup_total = len(startup_screens)
        self.loading = True

        splash = self.splash_screen
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
    def _setup_splash_screen(self, screen: FnSplashScreen) -> None:
        properties = {
            "_startup_index": "loaded",
            "_startup_pending": "current_screen",
            "_startup_total": "total",
        }
        for source, target in properties.items():
            setattr(screen, target, getattr(self, source))
            self._splash_bindings[source] = self.fbind(
                source, screen.setter(target)
            )

    # =================================== #
    # Loading
    # =================================== #
    def _begin_startup_loading(self) -> None:
        self._startup_iterator = iter(self._startup_screens)
        Clock.schedule_once(self._load_next_screen, 0)

    def _load_next_screen(self, *_: Any) -> None:
        if not self.loading:
            return
        iterator = self._startup_iterator
        if iterator is None:
            raise RuntimeError("Startup iterator has not been initialized")

        try:
            name = next(iterator)
        except StopIteration:
            self._finish_startup()
            return

        self._startup_pending = name
        # Show the pending name before constructing any of its widgets.
        Clock.schedule_once(partial(self._build_pending, name), 0)

    def _build_pending(self, name: str, _dt: float) -> None:
        if not self.loading:
            return
        try:
            screen = self._require_screen(name)
            self._pending_screen = screen
            self.initialize_screen(screen)
        except Exception as error:
            self.fail_startup(error)

    def initialize_screen(self, screen: FnScreen) -> None:
        """Build a screen, then report its readiness to the startup queue.

        Applications may override this hook to await their own data and
        rendering work. Call screen_initialized() only when it is complete.
        """
        if screen.is_ready:
            self.screen_initialized(screen)
            return
        screen.bind(on_ready=self.screen_initialized)
        screen._build()

    def screen_initialized(self, screen: FnScreen) -> None:
        """Advance after the pending screen and its application data load."""
        if not self.loading or self._pending_screen is not screen:
            return
        if not screen.is_ready:
            raise RuntimeError("A screen must be ready before advancing")
        screen.unbind(on_ready=self.screen_initialized)
        self._pending_screen = None
        self._startup_index += 1
        Clock.schedule_once(self._load_next_screen, 0)

    def fail_startup(self, error: Exception) -> None:
        """Stop progress and leave failure presentation to the owner."""
        if not self.loading:
            return
        screen = self._pending_screen
        if screen is not None:
            screen.unbind(on_ready=self.screen_initialized)
        self._pending_screen = None
        self.loading = False
        self.dispatch("on_startup_failed", error)

    def on_startup_failed(self, error: Exception) -> None:
        """Dispatched if screen construction or initialization fails."""
        pass

    def _finish_startup(self) -> None:
        target = self._startup_target

        if not target:
            raise RuntimeError(
                f"{type(self).__name__} has no startup target"
            )

        for name, uid in self._splash_bindings.items():
            self.unbind_uid(name, uid)
        self._splash_bindings.clear()

        self.current = target
        self.loading = False
        self.loaded = True
        Clock.schedule_once(self._cleanup, 0.1)

    def _cleanup(self, *_):

        self._startup_iterator = None
        self._startup_target = ""
        self._startup_pending = ""
        self._startup_screens = []
