from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from kivyfn.runtime.runtime import (
        FnClientRuntime,
        FnServerRuntime,
    )


_current_runtime = None


def set_runtime(runtime) -> None:
    global _current_runtime
    _current_runtime = runtime


def get_runtime():
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
