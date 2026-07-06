from __future__ import annotations

from collections.abc import Awaitable, Callable
from dataclasses import dataclass
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from kivyfn.runtime.runtime import (
        FnClientRuntime,
        FnServerRuntime,
    )


ShutdownHook = Callable[[], Any | Awaitable[Any]]


_current_runtime: FnServerRuntime | FnClientRuntime | None = None


def set_runtime(runtime: FnServerRuntime | FnClientRuntime) -> None:
    global _current_runtime
    _current_runtime = runtime


def get_runtime() -> FnServerRuntime | FnClientRuntime:
    if _current_runtime is None:
        raise RuntimeError("No runtime is active")

    return _current_runtime


@dataclass(slots=True)
class FnBootstrapContext:
    fn: FnServerRuntime | FnClientRuntime

    @property
    def config(self):
        return self.fn.config

    @property
    def fonts(self):
        return self.fn.fonts

    @property
    def i18n(self):
        return self.fn.i18n

    @property
    def settings(self):
        return self.fn.settings

    def on_shutdown(self, hook: ShutdownHook) -> None:
        self.fn.on_shutdown(hook)
