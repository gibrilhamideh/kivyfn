from __future__ import annotations

from collections.abc import Callable
from multiprocessing.context import SpawnContext
from typing import Any, Generic

from kivyfn.process.config import FnProcessConfig, ProcessName
from kivyfn.process.process import FnProcess


CleanupCallback = Callable[[ProcessName], None]


class FnProcessManager(Generic[ProcessName]):
    def __init__(self, context: SpawnContext) -> None:
        self._ctx = context
        self._registered: dict[ProcessName, FnProcessConfig[ProcessName]] = {}
        self._running: dict[ProcessName, FnProcess] = {}
        self._cleanup_callbacks: list[CleanupCallback[ProcessName]] = []

    def register(
        self,
        name: ProcessName,
        target: Callable[..., None],
        *args: Any,
        **kwargs: Any,
    ) -> None:
        if name in self._registered:
            raise RuntimeError(f"Process '{name}' is already registered")

        self._registered[name] = FnProcessConfig(
            name=name,
            target=target,
            args=args,
            kwargs=kwargs,
        )

    def bind_cleanup(
        self,
        callback: CleanupCallback[ProcessName],
    ) -> None:
        self._cleanup_callbacks.append(callback)

    def spawn(
        self,
        name: ProcessName,
        **extra_kwargs: Any,
    ) -> FnProcess:
        process_config = self._registered.get(name)

        if process_config is None:
            raise RuntimeError(f"Process '{name}' is not registered")

        existing = self._running.get(name)

        if existing is not None and existing.running:
            raise RuntimeError(f"Process '{name}' is already running")

        kwargs = {
            **process_config.kwargs,
            **extra_kwargs,
        }

        process = FnProcess(
            context=self._ctx,
            name=process_config.name,
            target=process_config.target,
            args=process_config.args,
            kwargs=kwargs,
        )

        process.start()
        self._running[name] = process

        return process

    def kill(
        self,
        name: ProcessName,
    ) -> None:
        process = self._running.get(name)

        if process is None:
            return

        process.stop()
        self._cleanup(name)

    def kill_all(self) -> None:
        for name in list(self._running):
            self.kill(name)

    def running(
        self,
        name: ProcessName,
    ) -> bool:
        process = self._running.get(name)
        return process is not None and process.running

    def registered(
        self,
        name: ProcessName,
    ) -> bool:
        return name in self._registered

    def _cleanup(
        self,
        name: ProcessName,
    ) -> None:
        self._running.pop(name, None)

        for callback in list(self._cleanup_callbacks):
            callback(name)
