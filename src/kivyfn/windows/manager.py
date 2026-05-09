from __future__ import annotations

from collections.abc import Callable
from typing import Any, Generic, TypeVar

from kivyfn.config import AppConfig
from kivyfn.process import ManagedProcess, ProcessManager
from kivyfn.runtime import RuntimeHost


WindowName = TypeVar("WindowName", bound=str)


class WindowManager(Generic[WindowName]):
    def __init__(
        self,
        processes: ProcessManager[WindowName],
        runtime: RuntimeHost,
        fnconfig: AppConfig,
    ) -> None:
        self._processes = processes
        self._runtime = runtime
        self._fnconfig = fnconfig

    def register(
        self,
        name: WindowName,
        target: Callable[..., None],
        *args: Any,
        **kwargs: Any,
    ) -> None:
        self._processes.register(name, target, *args, **kwargs)

    def spawn(self, name: WindowName) -> ManagedProcess:
        runtime = self._runtime.create_client(str(name))

        return self._processes.spawn(
            name,
            fnconfig=self._fnconfig,
            runtime=runtime,
        )

    def close(self, name: WindowName) -> None:
        self._processes.kill(name)

    def close_all(self) -> None:
        self._processes.kill_all()

    def running(self, name: WindowName) -> bool:
        return self._processes.running(name)

    def registered(self, name: WindowName) -> bool:
        return self._processes.registered(name)
