from __future__ import annotations

from collections.abc import Callable
from multiprocessing.context import SpawnProcess, SpawnContext
from typing import Any


class FnProcess:
    def __init__(
        self,
        context: SpawnContext,
        name: str,
        target: Callable[..., None],
        args: tuple[Any, ...] = (),
        kwargs: dict[str, Any] | None = None,
    ) -> None:

        self.name = name
        self.target = target
        self.args = args
        self.kwargs = kwargs or {}

        self._ctx: SpawnContext = context
        self._process: SpawnProcess | None = None

    def start(self) -> None:
        if self.running:
            raise RuntimeError(f"Process '{self.name}' is already running")

        self._process = self._ctx.Process(
            target=self.target,
            args=self.args,
            kwargs=self.kwargs,
            daemon=True,
        )

        assert self._process is not None
        self._process.start()

    def stop(self) -> None:
        if self._process is None:
            return

        self._process.terminate()
        self._process.join(timeout=2)

        if self._process.is_alive():
            self._process.kill()
            self._process.join(timeout=2)

        self._process = None

    @property
    def running(self) -> bool:
        return self._process is not None and self._process.is_alive()

    @property
    def pid(self) -> int | None:
        return None if self._process is None else self._process.pid
