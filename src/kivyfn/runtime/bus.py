# runtime/bus.py
from __future__ import annotations

import inspect
from collections.abc import Callable, Awaitable
from typing import Any

BusCallback = Callable[[Any], Any | Awaitable[Any]]


class FnBus:
    def __init__(self) -> None:
        self._handlers: dict[str, list[BusCallback]] = {}

    def subscribe(self, topic: str, callback: BusCallback) -> None:
        self._handlers.setdefault(topic, []).append(callback)

    async def _dispatch(self, topic: str, payload: Any) -> None:
        for callback in self._handlers.get(topic, []):
            result = callback(payload)

            if inspect.isawaitable(result):
                await result
