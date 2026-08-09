# kivyfn/app.py
from __future__ import annotations

import asyncio
import importlib

from collections.abc import Callable, Coroutine
from typing import (
    TYPE_CHECKING,
    Any,
    ClassVar,
    Literal,
    TypeAlias,
    TypeVar,
)

from kivy.app import App

from kivyfn.bootstrap import bootstrap
from kivyfn.config import FnConfig
from kivyfn.config.logging import FnLoggingConfig
from kivyfn.fonts import FontManager
from kivyfn.i18n import I18n
from kivyfn.logging import get_logger
from kivyfn.runtime.process import FnProcessManager
from kivyfn.runtime.services import Service
from kivyfn.runtime.tasks import FnTasks
from kivyfn.runtime.window import FnWindowManager
from kivyfn.ui.feedback.snackbar import FnSnackbarManager
from kivyfn.ui.keyboard import FnKeyboard
from kivyfn.ui.theme import Theme


if TYPE_CHECKING:
    from kivyfn.ui.root import FnRoot


logger = get_logger(__name__)


T = TypeVar("T")


FnRuntime: TypeAlias = Literal[
    "main",
    "spawn",
]


class FnApp(App):
    """
    Base KivyFN application.

    Services are owned directly by each FnApp instance and exposed through
    descriptors that support both instance-level and class-level access:

        app.tasks
        FnApp.tasks

    Class-level access resolves the currently running FnApp.
    """

    __runtime__: ClassVar[FnRuntime] = "main"
    __config__: ClassVar[FnConfig | None] = None
    keyboard_cls: ClassVar[type[FnKeyboard] | None] = None
    """
    Application virtual keyboard class.

    When set, Kivy uses this class whenever a focusable widget requests a
    virtual keyboard. The class must implement the :class:`FnKeyboard`
    interface. When left as ``None``, Kivy uses its default virtual keyboard.
    """

    tasks = Service[FnTasks]("_tasks")
    theme = Service[Theme]("_theme")
    i18n = Service[I18n]("_i18n")
    fonts = Service[FontManager]("_fonts")
    snackbar = Service[FnSnackbarManager]("_snackbar")
    processes = Service[FnProcessManager]("_processes")
    windows = Service[FnWindowManager]("_windows")

    __events__ = (
        "on_runtime",
    )

    if TYPE_CHECKING:
        root: FnRoot

    def __init__(
        self,
        **kwargs: Any,
    ) -> None:
        self._tasks: FnTasks | None = None
        self._theme: Theme | None = None
        self._i18n: I18n | None = None
        self._fonts: FontManager | None = None
        self._snackbar: FnSnackbarManager | None = None

        # Main-runtime-only services.
        self._processes: FnProcessManager | None = None
        self._windows: FnWindowManager | None = None

        self._runtime_started = False
        self._shutdown_started = False

        super().__init__(**kwargs)

        self._create_services()

        self.bind(
            on_start=lambda *_: self._start_runtime(),
        )

        self._run_bootstrap()

    # =================================== #
    # Running App
    # =================================== #

    @staticmethod
    def require_app() -> FnApp:
        """
        Return the active application as an FnApp.

        Raises when no Kivy application is running or when the running
        application is not an FnApp.
        """
        app = App.get_running_app()

        if app is None:
            raise RuntimeError(
                "This operation requires an active FnApp"
            )

        if not isinstance(
            app,
            FnApp,
        ):
            raise TypeError(
                "Expected the active Kivy application to be "
                f"an FnApp, got {type(app).__name__}"
            )

        return app

    @classmethod
    def require_root(cls) -> FnRoot:
        app = cls.require_app()
        root = app.root

        if root is None:
            raise RuntimeError(
                "This operation requires an active FnApp root"
            )

        return root

    # =================================== #
    # Runtime
    # =================================== #

    @property
    def is_main(self) -> bool:
        return self.__runtime__ == "main"

    @property
    def is_spawn(self) -> bool:
        return self.__runtime__ == "spawn"

    @property
    def runtime_started(self) -> bool:
        return self._runtime_started

    # =================================== #
    # Service Construction
    # =================================== #

    def _create_services(self) -> None:
        """
        Construct the services owned by this application instance.

        Process and window management are only created for the main runtime.
        """
        config = self.__config__

        self._tasks = FnTasks()
        self._theme = Theme()

        self._i18n = I18n(
            locales_dir=(
                config.locales_dir
                if config is not None
                else None
            ),
        )

        self._fonts = FontManager(
            fonts_dir=(
                config.fonts_dir
                if config is not None
                else None
            ),
            default_font=(
                config.fonts.name
                if config is not None
                else "NotoSans"
            ),
        )

        self._snackbar = FnSnackbarManager()

        if not self.is_main:
            return

        logging_config = (
            config.logging
            if config is not None
            else FnLoggingConfig()
        )

        self._processes = FnProcessManager(
            logging_config=logging_config,
        )

        self._windows = FnWindowManager(
            processes=self._processes,
        )

    # =================================== #
    # Bootstrap
    # =================================== #

    def _run_bootstrap(self) -> None:
        bootstrap()
        self._install_keyboard()
        self._load_framework_modules()
        self.on_bootstrap()

    def _install_keyboard(self) -> None:
        """
        Register the application virtual keyboard with Kivy.

        Keyboard registration is main-runtime-only because importing the Kivy
        window provider can create a graphical window. Registration happens
        before the root is built so the keyboard is available to the first
        focusable widget that requests it.
        """
        keyboard_cls = self.keyboard_cls

        if keyboard_cls is None:
            return

        from kivy.core.window import Window
        Window.set_vkeyboard_class(
            keyboard_cls,
        )

    def _load_framework_modules(self) -> None:
        self._try_bootstrap_module(
            "kivyfn.store.bootstrap",
        )

        self._try_bootstrap_module(
            "kivyfn.three.bootstrap",
        )

    @staticmethod
    def _try_bootstrap_module(
        module: str,
    ) -> None:
        try:
            imported = importlib.import_module(module)

        except ModuleNotFoundError as error:
            missing = error.name

            if missing is not None and (
                missing == module
                or module.startswith(f"{missing}.")
            ):
                return

            raise

        module_bootstrap = getattr(
            imported,
            "bootstrap",
            None,
        )

        if module_bootstrap is None:
            raise RuntimeError(
                f"Bootstrap module {module!r} does not "
                "define bootstrap()"
            )

        if not callable(module_bootstrap):
            raise TypeError(
                f"{module!r}.bootstrap must be callable"
            )

        module_bootstrap()

    def on_bootstrap(self) -> None:
        """
        Register application definitions required before the root is built.

        Typical registrations include:

        - KV files
        - Kivy Factory classes
        - fonts
        - screen classes
        - navigation routes
        - framework extensions

        Application runtime work does not belong here because the root and
        window are not available yet.
        """

    # =================================== #
    # Startup
    # =================================== #

    def _start_runtime(self) -> None:
        if self._runtime_started:
            return

        root = self.root

        if root is None:
            raise RuntimeError(
                "FnApp runtime cannot start without a root widget"
            )

        self._attach_services(
            root,
        )

        self._runtime_started = True

        self.dispatch(
            "on_runtime",
        )

    def _attach_services(
        self,
        root: FnRoot,
    ) -> None:
        """
        Attach services that require the application root.
        """
        self.snackbar.attach(
            root,
        )

    def on_runtime(self) -> None:
        """
        Called after the root exists and KivyFN runtime services have been
        attached.

        Runtime work such as starting navigation, activating controllers, or
        beginning application workflows belongs here.
        """

    # =================================== #
    # Tasks
    # =================================== #

    def create_task(
        self,
        coro: Coroutine[Any, Any, T],
        *,
        name: str | None = None,
        callback: Callable[[T], None] | None = None,
    ) -> asyncio.Task[T]:
        return self.tasks.create(
            coro,
            name=name,
            callback=callback,
        )

    # =================================== #
    # Execution
    # =================================== #

    def run(self) -> None:
        try:
            super().run()

        finally:
            self.shutdown()

    async def async_run(
        self,
        async_lib: str | None = None,
    ) -> None:
        try:
            await super().async_run(
                async_lib=async_lib,
            )

        finally:
            await self.async_shutdown()

    # =================================== #
    # Application Shutdown Hooks
    # =================================== #

    def on_shutdown(self) -> None:
        """
        Clean up synchronous application-owned resources.

        This runs for both run() and async_run().
        """

    async def on_async_shutdown(self) -> None:
        """
        Clean up asynchronous application-owned resources.

        This runs only for async_run().
        """

    # =================================== #
    # Framework Shutdown
    # =================================== #

    def shutdown(self) -> None:
        if self._shutdown_started:
            return

        self._shutdown_started = True

        try:
            self.on_shutdown()

        except Exception:
            logger.exception(
                "App shutdown hook failed"
            )

        self._detach_services()
        self._shutdown_processes()

    async def async_shutdown(self) -> None:
        if self._shutdown_started:
            return

        self._shutdown_started = True

        try:
            await self.on_async_shutdown()

        except Exception:
            logger.exception(
                "Async app shutdown hook failed"
            )

        try:
            self.on_shutdown()

        except Exception:
            logger.exception(
                "App shutdown hook failed"
            )

        tasks = self._tasks

        if tasks is not None:
            try:
                await tasks.shutdown()

            except Exception:
                logger.exception(
                    "Task manager shutdown failed"
                )

        self._detach_services()
        self._shutdown_processes()

    def _detach_services(self) -> None:
        snackbar = self._snackbar

        if snackbar is not None:
            try:
                snackbar.detach()

            except Exception:
                logger.exception(
                    "Snackbar manager detachment failed"
                )

        self._runtime_started = False

    def _shutdown_processes(self) -> None:
        if not self.is_main:
            return

        processes = self._processes

        if processes is None:
            return

        try:
            processes.shutdown()

        except Exception:
            logger.exception(
                "Process manager shutdown failed"
            )
