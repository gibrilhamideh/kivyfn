from __future__ import annotations
from typing import Any, Generic, TypeVar, cast
from collections.abc import Awaitable, Callable

import asyncio
import inspect

from kivyfn.runtime.server import FnServerBus

T = TypeVar("T")
S = TypeVar("S", bound="FnSharedState")

Callback = Callable[[Any], Any | Awaitable[Any]]
SharedStateType = type["FnSharedState"]


class FnSharedField(Generic[T]):
    def __init__(self, default: T) -> None:
        self.default = default
        self.name: str | None = None

    def __set_name__(
        self,
        owner: type[FnSharedState],
        name: str,
    ) -> None:
        self.name = name

        fields = getattr(owner, "__shared_fields__", None)

        if fields is None:
            fields = {}
            setattr(owner, "__shared_fields__", fields)

        fields[name] = self

    def __get__(
        self,
        instance: FnSharedState | None,
        owner: type[FnSharedState],
    ) -> T | FnSharedField[T]:
        if instance is None:
            return self

        if self.name is None:
            raise RuntimeError("SharedField is missing name")

        return instance._values.get(self.name, self.default)

    def __set__(
        self,
        instance: FnSharedState,
        value: T,
    ) -> None:
        if self.name is None:
            raise RuntimeError("SharedField is missing name")

        instance._set(self.name, value)


class FnSharedState:
    __shared_fields__: dict[str, FnSharedField[Any]]

    def __init__(
        self,
        manager: FnSharedStateManager,
        name: str,
    ) -> None:
        self._manager = manager
        self._name = name
        self._values: dict[str, Any] = {}
        self._callbacks: dict[str, set[Callback]] = {}

    @property
    def name(self) -> str:
        return self._name

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

    def _validate_field(
        self,
        field: str,
    ) -> None:
        if field not in self.__shared_fields__:
            raise AttributeError(
                f"{type(self).__name__!r} has no shared field {field!r}"
            )


class FnSharedStateManager:
    SNAPSHOT_TOPIC = "fn.shared.snapshot"
    UPDATE_TOPIC = "fn.shared.update"

    def __init__(
        self,
        bus: Any,
    ) -> None:
        self._bus = bus

        self._owner = False
        if isinstance(bus, FnServerBus):
            self._owner = True

        self._states: dict[str, FnSharedState] = {}
        self._classes: dict[str, SharedStateType] = {}

        self._setup_bus()

    @property
    def owner(self) -> bool:
        return self._owner

    def register(
        self,
        state_cls: SharedStateType,
        *,
        name: str | None = None,
    ) -> None:
        state_name = name or state_cls.__name__
        self._classes[state_name] = state_cls

    async def get(
        self,
        state_cls: type[S],
        *,
        name: str | None = None,
    ) -> S:
        state_name = name or state_cls.__name__

        existing = self._states.get(state_name)

        if existing is not None:
            return cast(S, existing)

        self.register(state_cls, name=state_name)

        state = state_cls(self, state_name)
        self._states[state_name] = state

        if not self._owner:
            snapshot = await self._bus.call(
                self.SNAPSHOT_TOPIC,
                {
                    "state": state_name,
                },
            )

            if not isinstance(snapshot, dict):
                raise RuntimeError(
                    f"Invalid snapshot for shared state {state_name!r}"
                )

            state.load_snapshot(snapshot)

        return state

    def set(
        self,
        state_name: str,
        field: str,
        value: Any,
    ) -> None:
        if self._owner:
            state = self._states[state_name]
            changed = state._apply(field, value)

            if changed:
                self._publish_update(state_name, field, value)

            return

        self._publish_update(state_name, field, value)

    def _setup_bus(self) -> None:
        self._bus.subscribe(self.UPDATE_TOPIC, self._on_update)

        if self._owner:
            self._bus.handle(self.SNAPSHOT_TOPIC, self._on_snapshot)

    def _publish_update(
        self,
        state_name: str,
        field: str,
        value: Any,
    ) -> None:
        result = self._bus.publish(
            self.UPDATE_TOPIC,
            {
                "state": state_name,
                "field": field,
                "value": value,
            },
        )

        if inspect.iscoroutine(result):
            asyncio.create_task(result)

    async def _on_update(
        self,
        payload: dict[str, Any],
    ) -> None:
        state_name = payload["state"]
        field = payload["field"]
        value = payload["value"]

        state = self._states.get(state_name)

        if state is None:
            return

        changed = state._apply(field, value)

        if changed and self._owner:
            self._publish_update(state_name, field, value)

    async def _on_snapshot(
        self,
        payload: dict[str, Any],
    ) -> dict[str, Any]:
        state_name = payload["state"]

        state = self._states.get(state_name)

        if state is None:
            state_cls = self._classes.get(state_name)

            if state_cls is None:
                raise RuntimeError(
                    f"Shared state {state_name!r} is not registered"
                )

            state = state_cls(self, state_name)
            self._states[state_name] = state

        return state.snapshot()
