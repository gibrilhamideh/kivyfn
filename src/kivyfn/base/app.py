from __future__ import annotations
from typing import TYPE_CHECKING

import asyncio
import importlib

from kivy.app import App
from kivyfn.runtime.context import FnBootstrapContext


if TYPE_CHECKING:
    from kivyfn.runtime.runtime import FnServerRuntime
    from kivyfn.runtime.runtime import FnClientRuntime


class FnBaseApp(App):

    def __init__(self, fn: FnServerRuntime | FnClientRuntime, **kwargs):
        super().__init__(**kwargs)
        self.fn = fn
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
    def create_task(self, coro):
        task = asyncio.create_task(coro)

        def done(t):
            try:
                t.result()
            except asyncio.CancelledError:
                pass
            except Exception as exc:
                print(f"Task failed: {exc!r}")

        task.add_done_callback(done)
        return task

    # -------------------------------------------------
    # Events
    # -------------------------------------------------
    def on_stop(self, *_):
        self.fn.stop()



