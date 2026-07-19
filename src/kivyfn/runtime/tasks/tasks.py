# kivyfn/runtime/asyncio/tasks.py
from __future__ import annotations

import asyncio

from collections.abc import Callable, Coroutine
from typing import Any, TypeVar

from kivyfn.logging import get_logger


logger = get_logger(__name__)


T = TypeVar("T")


class FnTasks:
    def __init__(self) -> None:
        self._tasks: set[asyncio.Task[Any]] = set()
        self._closing = False
        self._stopped = False

    @property
    def closing(self) -> bool:
        return self._closing

    @property
    def stopped(self) -> bool:
        return self._stopped

    @property
    def pending_count(self) -> int:
        return sum(
            1
            for task in self._tasks
            if not task.done()
        )

    def create(
        self,
        coro: Coroutine[Any, Any, T],
        *,
        name: str | None = None,
        callback: Callable[[T], None] | None = None,
    ) -> asyncio.Task[T]:
        if self._closing or self._stopped:
            coro.close()

            raise RuntimeError(
                "Cannot create tasks after task shutdown has started"
            )

        task = asyncio.create_task(
            coro,
            name=name or self._resolve_coro_name(coro),
        )

        self._tasks.add(task)

        task.add_done_callback(
            lambda completed: self._on_done(
                completed,
                callback,
            )
        )

        return task

    async def shutdown(self) -> None:
        if self._stopped:
            return

        self._closing = True

        current = asyncio.current_task()

        pending = tuple(
            task
            for task in self._tasks
            if task is not current
            and not task.done()
        )

        for task in pending:
            task.cancel()

        if pending:
            await asyncio.gather(
                *pending,
                return_exceptions=True,
            )

        self._tasks.clear()
        self._stopped = True

    def _on_done(
        self,
        task: asyncio.Task[T],
        callback: Callable[[T], None] | None,
    ) -> None:
        self._tasks.discard(task)

        try:
            result = task.result()
        except asyncio.CancelledError:
            return
        except Exception:
            logger.exception(
                "Async task failed: %s",
                task.get_name(),
            )
            return

        if callback is None:
            return

        try:
            callback(result)
        except Exception:
            logger.exception(
                "Async task callback failed: %s",
                task.get_name(),
            )

    @staticmethod
    def _resolve_coro_name(
        coro: Coroutine[Any, Any, Any],
    ) -> str:
        qualname = getattr(coro, "__qualname__", None)

        if isinstance(qualname, str):
            return qualname

        name = getattr(coro, "__name__", None)

        if isinstance(name, str):
            return name

        code = getattr(coro, "cr_code", None)

        if code is not None:
            return code.co_name

        return type(coro).__name__
