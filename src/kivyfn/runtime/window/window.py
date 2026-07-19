# kivyfn/runtime/window/window.py
from __future__ import annotations

from kivyfn.runtime.process import FnProcess
from kivyfn.runtime.window.types import WindowFactory


class FnWindow:
    def __init__(
        self,
        name: str,
        factory: WindowFactory,
        *,
        async_mode: bool = False,
    ) -> None:
        self._name = name
        self._factory = factory
        self._async_mode = async_mode
        self._process: FnProcess | None = None

    @property
    def name(self) -> str:
        return self._name

    @property
    def factory(self) -> WindowFactory:
        return self._factory

    @property
    def async_mode(self) -> bool:
        return self._async_mode

    @property
    def process(self) -> FnProcess:
        if self._process is None:
            raise RuntimeError(
                f"Window {self.name!r} is not attached to a process"
            )

        return self._process

    @property
    def pid(self) -> int | None:
        return None if self._process is None else self._process.pid

    @property
    def running(self) -> bool:
        return (
            self._process is not None
            and self._process.running
        )

    @property
    def ready(self) -> bool:
        return (
            self._process is not None
            and self._process.ready
        )

    @property
    def failed(self) -> bool:
        return (
            self._process is not None
            and self._process.failed
        )

    @property
    def exited(self) -> bool:
        return (
            self._process is not None
            and self._process.exited
        )

    def _attach(self, process: FnProcess) -> None:
        if self._process is not None:
            raise RuntimeError(
                f"Window {self.name!r} already has an attached process"
            )

        self._process = process
