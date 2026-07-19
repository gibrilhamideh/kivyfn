# kivyfn/runtime/process/process.py
from __future__ import annotations

from multiprocessing.context import SpawnProcess
from multiprocessing.synchronize import Event
from threading import Event as ThreadEvent

from kivyfn.runtime.process.message import ProcessError
from kivyfn.runtime.process.state import FnProcessState
from kivyfn.runtime.process.types import (
    ProcessExitCallback,
    ProcessFailedCallback,
    ProcessPayload,
    ProcessReadyCallback,
    ProcessTarget,
)


class FnProcess:
    def __init__(
        self,
        name: str,
        target: ProcessTarget,
        *,
        on_ready: ProcessReadyCallback | None = None,
        on_failed: ProcessFailedCallback | None = None,
        on_exit: ProcessExitCallback | None = None,
    ) -> None:
        self._name = name
        self._target = target
        self._on_ready = on_ready
        self._on_failed = on_failed
        self._on_exit = on_exit

        self._native_process: SpawnProcess | None = None
        self._stop_event: Event | None = None

        self._state = FnProcessState.REGISTERED
        self._ready_payload: ProcessPayload | None = None
        self._failure: ProcessError | None = None
        self._exitcode: int | None = None

        self._ready_event = ThreadEvent()
        self._failed_event = ThreadEvent()
        self._exit_event = ThreadEvent()

    @property
    def name(self) -> str:
        return self._name

    @property
    def target(self) -> ProcessTarget:
        return self._target

    @property
    def state(self) -> FnProcessState:
        return self._state

    @property
    def pid(self) -> int | None:
        if self._native_process is None:
            return None

        return self._native_process.pid

    @property
    def exitcode(self) -> int | None:
        return self._exitcode

    @property
    def ready_payload(self) -> ProcessPayload | None:
        return self._ready_payload

    @property
    def failure(self) -> ProcessError | None:
        return self._failure

    @property
    def registered(self) -> bool:
        return self.state is FnProcessState.REGISTERED

    @property
    def starting(self) -> bool:
        return self.state is FnProcessState.STARTING

    @property
    def ready(self) -> bool:
        return self.state is FnProcessState.READY

    @property
    def stopping(self) -> bool:
        return self.state is FnProcessState.STOPPING

    @property
    def failed(self) -> bool:
        return self.state is FnProcessState.FAILED

    @property
    def exited(self) -> bool:
        return self.state is FnProcessState.EXITED

    @property
    def running(self) -> bool:
        return (
            self._native_process is not None
            and self._native_process.is_alive()
        )

    def wait_ready(self, timeout: float | None = None) -> bool:
        return self._ready_event.wait(timeout)

    def wait_failed(self, timeout: float | None = None) -> bool:
        return self._failed_event.wait(timeout)

    def wait_exit(self, timeout: float | None = None) -> bool:
        return self._exit_event.wait(timeout)

    def _prepare(
        self,
        native_process: SpawnProcess,
        stop_event: Event,
    ) -> None:
        if self.running:
            raise RuntimeError(
                f"Process {self.name!r} is already running"
            )

        self._native_process = native_process
        self._stop_event = stop_event
        self._state = FnProcessState.STARTING
        self._ready_payload = None
        self._failure = None
        self._exitcode = None

        self._ready_event.clear()
        self._failed_event.clear()
        self._exit_event.clear()

    def _mark_ready(self, payload: ProcessPayload) -> None:
        if self.state is FnProcessState.FAILED:
            return

        self._state = FnProcessState.READY
        self._ready_payload = dict(payload)
        self._ready_event.set()

        if self._on_ready is not None:
            self._on_ready(self, self._ready_payload)

    def _mark_failed(self, error: ProcessError) -> None:
        if self.state is FnProcessState.EXITED:
            return

        self._state = FnProcessState.FAILED
        self._failure = error
        self._failed_event.set()

        if self._on_failed is not None:
            self._on_failed(self, error)

    def _mark_stopping(self) -> None:
        if self.state is FnProcessState.EXITED:
            return

        self._state = FnProcessState.STOPPING

        if self._stop_event is not None:
            self._stop_event.set()

    def _mark_exited(self, exitcode: int | None) -> None:
        self._state = FnProcessState.EXITED
        self._exitcode = exitcode
        self._exit_event.set()

        if self._on_exit is not None:
            self._on_exit(self, exitcode)

    def _reset(self) -> None:
        if self.running:
            raise RuntimeError(
                f"Cannot reset running process {self.name!r}"
            )

        self._native_process = None
        self._stop_event = None
        self._state = FnProcessState.REGISTERED
        self._ready_payload = None
        self._failure = None
        self._exitcode = None

        self._ready_event.clear()
        self._failed_event.clear()
        self._exit_event.clear()
