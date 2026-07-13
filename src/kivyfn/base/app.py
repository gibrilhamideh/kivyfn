# kivyfn/base/app.py

from __future__ import annotations

from typing import TYPE_CHECKING, Any, Coroutine

import asyncio
import importlib

from kivy.app import App
from kivy.properties import ObjectProperty

from kivyfn.logging import get_logger
from kivyfn.runtime.asyncio import FnTasks
from kivyfn.runtime.context import FnBootstrapContext

from kivyfn.ui.theme import Theme
from kivyfn.ui.feedback.snackbar import FnSnackbarManager


if TYPE_CHECKING:
    from kivyfn.ui.root import FnRoot
    from kivyfn.runtime.runtime import FnClientRuntime
    from kivyfn.runtime.runtime import FnServerRuntime


logger = get_logger(__name__)


class FnBaseApp(App):
    theme: Theme = ObjectProperty(rebind=True)


    if TYPE_CHECKING:
        root: FnRoot

    def __init__(
        self,
        fn: FnServerRuntime | FnClientRuntime,
        **kwargs: Any,
    ) -> None:
        self.fn = fn
        self.theme = Theme()
        self._shutdown_started = False

        super().__init__(**kwargs)

        self._run_bootstrap()

    # =================================== #
    # Bootstrap
    # =================================== #

    def _run_bootstrap(self) -> None:
        ctx = FnBootstrapContext(self.fn)

        self._load_framework_modules(ctx)
        self.on_load_modules(ctx)
        self.on_bootstrap(ctx)

    def _load_framework_modules(
        self,
        ctx: FnBootstrapContext,
    ) -> None:
        self._try_module("kivyfn.bootstrap", ctx)
        self._try_module("kivyfn.ui.bootstrap", ctx)
        self._try_module("kivyfn.store.bootstrap", ctx)
        self._try_module("kivyfn.three.bootstrap", ctx)

    def _try_module(
        self,
        module: str,
        ctx: FnBootstrapContext,
    ) -> None:
        try:
            imported = importlib.import_module(module)
        except ModuleNotFoundError as exc:
            if exc.name == module:
                return

            raise

        bootstrap = getattr(imported, "bootstrap", None)

        if bootstrap is not None:
            bootstrap(ctx)

    def on_load_modules(
        self,
        ctx: FnBootstrapContext,
    ) -> None:
        """
        Register application-owned modules and components.
        """

    def on_bootstrap(
        self,
        ctx: FnBootstrapContext,
    ) -> None:
        """
        Start application-owned bootstrap work.
        """

    # =================================== #
    # App Helpers
    # =================================== #

    def create_task(
        self,
        coro: Coroutine[Any, Any, Any],
        *,
        name: str | None = None,
    ) -> asyncio.Task[Any]:
        return FnTasks.create(coro, name=name)

    # =================================== #
    # Shutdown
    # =================================== #

    async def on_shutdown(self) -> None:
        """
        Override for application-owned cleanup.

        Framework cleanup runs afterward.
        """

    async def shutdown(self) -> None:
        if self._shutdown_started:
            return

        self._shutdown_started = True

        try:
            await self.on_shutdown()
        except Exception:
            logger.exception("App shutdown hook failed")
        finally:
            await self.fn.shutdown()

    def on_stop(self, *_: Any) -> None:
        """
        Kivy synchronous stop event.

        Async cleanup is performed by shutdown() from the entry point.
        """

    def on_start(self, *_: Any) -> None:
        """
        Kivy synchronous start event.

        Subclasses that override this method must call
        `super().on_start(*args)`.
        """
        FnSnackbarManager.attach(self.root)
        



