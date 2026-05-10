from __future__ import annotations
from typing import TYPE_CHECKING

import asyncio
import inspect
from typing import Any, TypeVar, cast

from kivyfn.runtime.transport.server import FnServerBus

if TYPE_CHECKING:
    from kivyfn.runtime.state.shared import FnSharedState


S = TypeVar("S", bound="FnSharedState")
SharedStateType = type["FnSharedState"]


class FnSharedStateManager:
    SNAPSHOT_TOPIC = "fn.shared.snapshot"
    UPDATE_TOPIC = "fn.shared.update"

    def __init__(
        self,
        bus: Any,
    ) -> None:
        self._bus = bus
        self._owner = isinstance(bus, FnServerBus)

        self._states: dict[str, FnSharedState] = {}
        self._classes: dict[str, SharedStateType] = {}

        self._setup_bus()

    @property
    def owner(self) -> bool:
        return self._owner

    def register(
        self,
        state_cls: type[S],
    ) -> None:
        state_name = state_cls.__name__

        existing = self._classes.get(state_name)

        if existing is not None and existing is not state_cls:
            raise RuntimeError(
                f"Shared state name conflict: {state_name!r} is already registered"
            )

        self._classes[state_name] = state_cls

    def instance(
        self,
        state_cls: type[S],
    ) -> S:
        state_name = state_cls.__name__

        existing = self._states.get(state_name)

        if existing is not None:
            return cast(S, existing)

        self.register(state_cls)

        state = object.__new__(state_cls)
        state._init_shared_state(self, state_name)

        self._states[state_name] = state

        return state

    async def snapshot(
        self,
        state_name: str,
    ) -> dict[str, Any]:
        return await self._bus.call(
            self.SNAPSHOT_TOPIC,
            {"state": state_name},
        )

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
                    f"Shared state {state_name!r} is not registered in owner runtime"
                )

            state = object.__new__(state_cls)
            state._init_shared_state(self, state_name)
            self._states[state_name] = state

        return state.snapshot()
