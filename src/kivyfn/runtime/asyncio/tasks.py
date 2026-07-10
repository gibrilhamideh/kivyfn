# kivyfn/runtime/asyncio/tasks.py
from __future__ import annotations

from typing import Any, Callable, ClassVar, Coroutine, TypeVar

import asyncio

from kivyfn.logging import get_logger


logger = get_logger(__name__)


T = TypeVar("T")


class FnTasks:
    _tasks: ClassVar[set[asyncio.Task[Any]]] = set()
    _closing: ClassVar[bool] = False
    _stopped: ClassVar[bool] = False

    def __new__(cls) -> FnTasks:
        raise TypeError(
            f"{cls.__name__} is a global runtime service "
            "and cannot be instantiated"
        )

    @classmethod
    def create(
        cls,
        coro: Coroutine[Any, Any, T],
        *,
        name: str | None = None,
        callback: Callable[[T], None] | None = None,
    ) -> asyncio.Task[T]:
        if cls._closing:
            coro.close()

            raise RuntimeError(
                "Cannot create task while task manager is closing"
            )

        task = asyncio.create_task(
            coro,
            name=name or cls._resolve_coro_name(coro),
        )

        cls._tasks.add(task)

        task.add_done_callback(
            lambda completed: cls._on_done(
                completed,
                callback,
            )
        )

        return task

    @classmethod
    async def stop(cls) -> None:
        if cls._stopped:
            return

        cls._closing = True

        current = asyncio.current_task()

        pending = tuple(
            task
            for task in cls._tasks
            if task is not current
            and not task.done()
        )

        if not pending:
            cls._tasks.clear()
            cls._stopped = True
            return

        for task in pending:
            task.cancel()

        await asyncio.gather(
            *pending,
            return_exceptions=True,
        )

        cls._tasks.difference_update(
            pending,
        )

        cls._stopped = True

    @classmethod
    def pending_count(cls) -> int:
        return sum(
            1
            for task in cls._tasks
            if not task.done()
        )

    @classmethod
    def _on_done(
        cls,
        task: asyncio.Task[T],
        callback: Callable[[T], None] | None,
    ) -> None:
        cls._tasks.discard(
            task,
        )

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
            callback(
                result,
            )

        except Exception:
            logger.exception(
                "Async task callback failed: %s",
                task.get_name(),
            )

    @staticmethod
    def _resolve_coro_name(
        coro: Coroutine[Any, Any, Any],
    ) -> str:
        qualname = getattr(
            coro,
            "__qualname__",
            None,
        )

        if isinstance(qualname, str):
            return qualname

        name = getattr(
            coro,
            "__name__",
            None,
        )

        if isinstance(name, str):
            return name

        code = getattr(
            coro,
            "cr_code",
            None,
        )

        if code is not None:
            return code.co_name

        return type(coro).__name__
