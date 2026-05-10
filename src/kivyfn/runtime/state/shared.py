from __future__ import annotations
from typing import Any, TypeVar, cast, TYPE_CHECKING

import asyncio
import inspect
from collections.abc import Awaitable, Callable

from kivyfn.runtime.context import get_runtime


if TYPE_CHECKING:
    from kivyfn.runtime.state.field import FnSharedField
    from kivyfn.runtime.state.manager import FnSharedStateManager

T = TypeVar("T")
S = TypeVar("S", bound="FnSharedState")

Callback = Callable[[Any], Any | Awaitable[Any]]
SharedStateType = type["FnSharedState"]



class FnSharedState:
    __shared_fields__: dict[str, FnSharedField[Any]]

    def __new__(cls: type[S]) -> S:
        runtime = get_runtime()
        return runtime.state.instance(cls)

    def _init_shared_state(
        self,
        manager: FnSharedStateManager,
        name: str,
    ) -> None:
        self._manager = manager
        self._name = name
        self._values: dict[str, Any] = {}
        self._callbacks: dict[str, set[Callback]] = {}
        self._sync_task: asyncio.Task[None] | None = None
        self._synced = asyncio.Event()

        if manager.owner:
            self._synced.set()
        else:
            self._schedule_sync()

    @property
    def name(self) -> str:
        return self._name

    async def sync(self) -> None:
        if self._manager.owner:
            self._synced.set()
            return

        if self._synced.is_set():
            return

        if self._sync_task is not None:
            await self._sync_task
            return

        await self._sync()

    def bind(
        self,
        field: str,
        callback: Callback,
    ) -> None:
        self._validate_field(field)
        self._callbacks.setdefault(field, set()).add(callback)

    def unbind(
        self,
        field: str,
        callback: Callback,
    ) -> None:
        callbacks = self._callbacks.get(field)

        if callbacks is None:
            return

        callbacks.discard(callback)

        if not callbacks:
            self._callbacks.pop(field, None)

    def snapshot(self) -> dict[str, Any]:
        return {
            field: self._values.get(field, descriptor.default)
            for field, descriptor in self.__shared_fields__.items()
        }

    def load_snapshot(
        self,
        values: dict[str, Any],
    ) -> None:
        for field, value in values.items():
            self._apply(field, value)

    def _set(
        self,
        field: str,
        value: Any,
    ) -> None:
        self._validate_field(field)
        self._manager.set(self._name, field, value)

    def _apply(
        self,
        field: str,
        value: Any,
    ) -> bool:
        self._validate_field(field)

        old_value = self._get_value(field)

        if old_value == value:
            return False

        self._values[field] = value
        self._dispatch(field, value)

        return True

    def _get_value(
        self,
        field: str,
    ) -> Any:
        descriptor = self.__shared_fields__[field]
        return self._values.get(field, descriptor.default)

    def _dispatch(
        self,
        field: str,
        value: Any,
    ) -> None:
        for callback in list(self._callbacks.get(field, ())):
            result = callback(value)

            if inspect.iscoroutine(result):
                asyncio.create_task(result)

    def _schedule_sync(self) -> None:
        try:
            asyncio.get_running_loop()
        except RuntimeError:
            return

        self._sync_task = asyncio.create_task(self._sync())

    async def _sync(self) -> None:
        snapshot = await self._manager.snapshot(self._name)

        if not isinstance(snapshot, dict):
            raise RuntimeError(
                f"Invalid snapshot for shared state {self._name!r}"
            )

        self.load_snapshot(snapshot)
        self._synced.set()

    def _validate_field(
        self,
        field: str,
    ) -> None:
        if field not in self.__shared_fields__:
            raise AttributeError(
                f"{type(self).__name__!r} has no shared field {field!r}"
            )



