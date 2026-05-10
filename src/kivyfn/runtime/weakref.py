from __future__ import annotations

import weakref
from collections.abc import Callable
from typing import Any, Generic, TypeVar


T = TypeVar("T", bound=Callable[..., Any])


class FnWeakRef(Generic[T]):
    def __init__(self, callback: T) -> None:
        try:
            self._ref = weakref.WeakMethod(callback)  # bound method
        except TypeError:
            self._ref = weakref.ref(callback)  # function

    def get(self) -> T | None:
        return self._ref()  # type: ignore[return-value]

    def alive(self) -> bool:
        return self.get() is not None

    def matches(self, callback: T) -> bool:
        return self.get() is callback
