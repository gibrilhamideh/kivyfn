from __future__ import annotations

from collections.abc import Callable
from multiprocessing.context import SpawnContext
from typing import Any, Generic

from kivyfn.process.definition import ProcessDefinition, ProcessName
from kivyfn.process.process import ManagedProcess


class ProcessManager(Generic[ProcessName]):
    def __init__(self, context: SpawnContext) -> None:
        self.context = context
        self._registered: dict[ProcessName, ProcessDefinition[ProcessName]] = {}
        self._running: dict[ProcessName, ManagedProcess] = {}

    def register(
        self,
        name: ProcessName,
        target: Callable[..., None],
        *args: Any,
        **kwargs: Any,
    ) -> None:
        if name in self._registered:
            raise RuntimeError(f"Process '{name}' is already registered")

        self._registered[name] = ProcessDefinition(
            name=name,
            target=target,
            args=args,
            kwargs=kwargs,
        )

    def spawn(self, name: ProcessName, **extra_kwargs: Any) -> ManagedProcess:
        definition = self._registered.get(name)

        if definition is None:
            raise RuntimeError(f"Process '{name}' is not registered")

        existing = self._running.get(name)

        if existing is not None and existing.running:
            raise RuntimeError(f"Process '{name}' is already running")

        kwargs = {
            **definition.kwargs,
            **extra_kwargs,
        }

        process = ManagedProcess(
            context=self.context,
            name=definition.name,
            target=definition.target,
            args=definition.args,
            kwargs=kwargs,
        )

        process.start()
        self._running[name] = process

        return process

    def kill(self, name: ProcessName) -> None:
        process = self._running.get(name)

        if process is None:
            return

        process.stop()
        self._running.pop(name, None)

    def kill_all(self) -> None:
        for name in list(self._running):
            self.kill(name)

    def running(self, name: ProcessName) -> bool:
        process = self._running.get(name)
        return process is not None and process.running

    def registered(self, name: ProcessName) -> bool:
        return name in self._registered
