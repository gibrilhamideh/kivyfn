from __future__ import annotations

import inspect
from collections.abc import Awaitable, Callable
from typing import Any

from kivyfn.runtime.weakref import FnWeakRef


BusCallback = Callable[[Any], Any | Awaitable[Any]]
BusHandler = Callable[[Any], Any | Awaitable[Any]]


class FnBus:
    def __init__(self) -> None:
        self._subscribers: dict[str, list[FnWeakRef[BusCallback]]] = {}
        self._handlers: dict[str, BusHandler] = {}

    def subscribe(
        self,
        topic: str,
        callback: BusCallback,
    ) -> None:
        self._subscribers.setdefault(topic, []).append(
            FnWeakRef(callback)
        )

    def unsubscribe(
        self,
        topic: str,
        callback: BusCallback,
    ) -> None:
        callbacks = self._subscribers.get(topic)

        if callbacks is None:
            return

        callbacks[:] = [
            weak_callback
            for weak_callback in callbacks
            if not weak_callback.matches(callback)
        ]

        if not callbacks:
            self._subscribers.pop(topic, None)

    def handle(
        self,
        topic: str,
        handler: BusHandler,
    ) -> None:
        self._handlers[topic] = handler

    def remove_handler(
        self,
        topic: str,
    ) -> None:
        self._handlers.pop(topic, None)

    async def dispatch(
        self,
        topic: str,
        payload: Any = None,
    ) -> None:
        callbacks = self._subscribers.get(topic)

        if callbacks is None:
            return

        for weak_callback in list(callbacks):
            callback = weak_callback.get()

            if callback is None:
                callbacks.remove(weak_callback)
                continue

            result = callback(payload)

            if inspect.isawaitable(result):
                await result

        if not callbacks:
            self._subscribers.pop(topic, None)

    async def _handle(
        self,
        topic: str,
        payload: Any = None,
    ) -> Any:
        handler = self._handlers.get(topic)

        if handler is None:
            raise RuntimeError(
                f"No bus handler registered for topic {topic!r}"
            )

        result = handler(payload)

        if inspect.isawaitable(result):
            return await result

        return result
