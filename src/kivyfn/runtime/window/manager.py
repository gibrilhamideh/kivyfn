# kivyfn/runtime/window/manager.py
from __future__ import annotations

from threading import RLock

from kivyfn.runtime.process import FnProcessManager
from kivyfn.runtime.window.entry import window_entry
from kivyfn.runtime.window.types import (
    WindowArgs,
    WindowFactory,
    WindowKwargs,
)
from kivyfn.runtime.window.window import FnWindow


class FnWindowManager:
    def __init__(self, processes: FnProcessManager) -> None:
        self._processes = processes
        self._windows: dict[str, FnWindow] = {}
        self._lock = RLock()

    @property
    def registered(self) -> tuple[str, ...]:
        with self._lock:
            return tuple(self._windows)

    @property
    def opened(self) -> tuple[str, ...]:
        with self._lock:
            return tuple(
                name
                for name, window in self._windows.items()
                if window.running
            )

    def __contains__(self, name: str) -> bool:
        with self._lock:
            return name in self._windows

    def register(
        self,
        name: str,
        factory: WindowFactory,
        *,
        async_mode: bool = False,
    ) -> FnWindow:
        if not isinstance(name, str) or not name:
            raise ValueError(
                "Window name must be a non-empty string"
            )

        with self._lock:
            if name in self._windows:
                raise ValueError(
                    f"Window {name!r} is already registered"
                )

            window = FnWindow(
                name=name,
                factory=factory,
                async_mode=async_mode,
            )

            process = self._processes.register(
                name=self._process_name(name),
                target=window_entry,
            )

            window._attach(process)
            self._windows[name] = window
            return window

    def unregister(self, name: str) -> None:
        window = self.get(name)

        if window.running:
            raise RuntimeError(
                f"Cannot unregister open window {name!r}"
            )

        self._processes.unregister(
            self._process_name(name)
        )

        with self._lock:
            self._windows.pop(name, None)

    def get(self, name: str) -> FnWindow:
        with self._lock:
            try:
                return self._windows[name]
            except KeyError:
                raise KeyError(
                    f"Window {name!r} is not registered"
                ) from None

    def open(
        self,
        name: str,
        args: WindowArgs = (),
        kwargs: WindowKwargs | None = None,
        *,
        wait: bool = False,
        timeout: float | None = None,
    ) -> FnWindow:
        window = self.get(name)

        if window.running:
            raise RuntimeError(
                f"Window {name!r} is already open"
            )

        self._processes.start(
            self._process_name(name),
            args=(
                window.factory,
                args,
                {} if kwargs is None else dict(kwargs),
                window.async_mode,
            ),
            wait=wait,
            timeout=timeout,
        )

        return window

    def close(
        self,
        name: str,
        *,
        timeout: float | None = 5.0,
        kill_timeout: float | None = 1.0,
    ) -> None:
        self.get(name)

        self._processes.stop(
            self._process_name(name),
            timeout=timeout,
            kill_timeout=kill_timeout,
        )

    def close_all(
        self,
        *,
        timeout: float | None = 5.0,
        kill_timeout: float | None = 1.0,
    ) -> None:
        with self._lock:
            names = tuple(self._windows)

        for name in names:
            self.close(
                name,
                timeout=timeout,
                kill_timeout=kill_timeout,
            )

    @staticmethod
    def _process_name(name: str) -> str:
        return f"window:{name}"
