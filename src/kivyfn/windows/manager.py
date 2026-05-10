from __future__ import annotations

from collections.abc import Callable
from typing import Any, Generic, TypeVar

from kivyfn.config import FnConfig
from kivyfn.process import FnProcess, FnProcessManager
from kivyfn.runtime import FnServerBus


WindowName = TypeVar("WindowName", bound=str)


class FnWindowManager(Generic[WindowName]):
    def __init__(
        self,
        processes: FnProcessManager[WindowName],
        bus: FnServerBus,
        config: FnConfig,
    ) -> None:
        self._processes = processes
        self._bus = bus
        self._config = config

        self._processes.bind_cleanup(
            lambda name: self._bus.remove_connection(str(name))
        )

        self._bus.subscribe(
            "fn.window.close.requested",
            self._on_close_requested,
        )

    def register(
        self,
        name: WindowName,
        target: Callable[..., None],
        *args: Any,
        **kwargs: Any,
    ) -> None:
        self._processes.register(name, target, *args, **kwargs)

    def spawn(self, name: WindowName) -> FnProcess:
        connection = self._bus.create_connection(str(name))

        return self._processes.spawn(
            name,
            config=self._config,
            connection=connection,
        )

    def close(self, name: WindowName) -> None:
        self._processes.kill(name)

    def close_all(self) -> None:
        self._processes.kill_all()

    def running(self, name: WindowName) -> bool:
        return self._processes.running(name)

    def registered(self, name: WindowName) -> bool:
        return self._processes.registered(name)

    def _on_close_requested(
        self,
        payload: dict[str, Any],
    ) -> None:
        name = payload.get("name")

        if name is None:
            return

        self.close(name)
