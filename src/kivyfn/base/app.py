# kivyfn/base/app.py
from __future__ import annotations

from typing import TYPE_CHECKING, Coroutine, Any

import asyncio
import importlib

from kivy.app import App

from kivyfn.logging import get_logger
from kivyfn.runtime.context import FnBootstrapContext


if TYPE_CHECKING:
    from kivyfn.runtime.runtime import FnServerRuntime
    from kivyfn.runtime.runtime import FnClientRuntime


logger = get_logger(__name__)


class FnBaseApp(App):
    def __init__(self, fn: FnServerRuntime | FnClientRuntime, **kwargs):
        super().__init__(**kwargs)
        self.fn = fn
        self._runtime_stopped = False
        self._bootstrap()

    # -------------------------------------------------
    # Bootstrap
    # -------------------------------------------------
    def _bootstrap(self) -> None:
        ctx = FnBootstrapContext(self.fn)
        self._load_modules(ctx)

    def _load_modules(self, ctx: FnBootstrapContext) -> None:
        self._try_module("kivyfn.bootstrap", ctx)
        self._try_module("kivyfn.ui.bootstrap", ctx)
        self._try_module("kivyfn.store.bootstrap", ctx)
        self._try_module("kivyfn.three.bootstrap", ctx)

    def _try_module(self, module: str, ctx: FnBootstrapContext) -> None:
        try:
            m = importlib.import_module(module)
        except ModuleNotFoundError:
            return

        bootstrap = getattr(m, "bootstrap", None)

        if bootstrap is not None:
            bootstrap(ctx)

    # -------------------------------------------------
    # App Helpers
    # -------------------------------------------------
    def create_task(
        self,
        coro: Coroutine[Any, Any, Any],
        *,
        name: str | None = None,
    ) -> asyncio.Task[Any]:
        task = asyncio.create_task(coro, name=name)

        def done(t: asyncio.Task[Any]) -> None:
            try:
                t.result()
            except asyncio.CancelledError:
                pass
            except Exception:
                logger.exception("Task failed")

        task.add_done_callback(done)
        return task

    # -------------------------------------------------
    # Events
    # -------------------------------------------------
    def stop_runtime(self) -> None:
        if self._runtime_stopped:
            return

        self._runtime_stopped = True
        self.fn.stop()

    def on_stop(self, *_):
        self.stop_runtime()


