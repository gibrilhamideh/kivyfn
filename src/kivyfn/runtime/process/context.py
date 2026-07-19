# kivyfn/runtime/process/context.py
from __future__ import annotations

from collections.abc import Callable
from threading import Thread
from traceback import format_exception

from kivyfn.runtime.process.message import (
    ProcessError,
    ProcessFailedMessage,
    ProcessReadyMessage,
)
from kivyfn.runtime.process.types import (
    ProcessArgs,
    ProcessKwargs,
    ProcessPayload,
    ProcessStatusQueue,
    ProcessStopEvent,
)


class FnProcessContext:
    def __init__(
        self,
        name: str,
        args: ProcessArgs,
        kwargs: ProcessKwargs,
        status_queue: ProcessStatusQueue,
        stop_event: ProcessStopEvent,
    ) -> None:
        self._name = name
        self._args = args
        self._kwargs = kwargs
        self._status_queue = status_queue
        self._stop_event = stop_event
        self._listener: Thread | None = None
        self._ready = False
        self._failed = False

    @property
    def name(self) -> str:
        return self._name

    @property
    def args(self) -> ProcessArgs:
        return self._args

    @property
    def kwargs(self) -> ProcessKwargs:
        return self._kwargs

    @property
    def running(self) -> bool:
        return not self._stop_event.is_set()

    def listen(self, callback: Callable[[], None]) -> None:
        if self._listener is not None:
            raise RuntimeError(
                f"Process {self.name!r} already has a running listener"
            )

        self._listener = Thread(
            target=self._listen,
            args=(callback,),
            name=f"{self.name}-listener",
            daemon=True,
        )
        self._listener.start()

    def ready(self, payload: ProcessPayload | None = None) -> None:
        if self._ready:
            raise RuntimeError(
                f"Process {self.name!r} has already reported readiness"
            )

        if self._failed:
            raise RuntimeError(
                f"Process {self.name!r} has already reported failure"
            )

        self._status_queue.put(
            ProcessReadyMessage(
                process=self.name,
                payload={} if payload is None else payload,
            )
        )

        self._ready = True

    def failed(
        self,
        error: str | BaseException,
        payload: ProcessPayload | None = None,
    ) -> None:
        if self._failed:
            raise RuntimeError(
                f"Process {self.name!r} has already reported failure"
            )

        self._status_queue.put(
            ProcessFailedMessage(
                process=self.name,
                error=self._create_error(error),
                payload={} if payload is None else payload,
            )
        )

        self._failed = True

    def _listen(self, callback: Callable[[], None]) -> None:
        self._stop_event.wait()
        callback()

    @staticmethod
    def _create_error(error: str | BaseException) -> ProcessError:
        if isinstance(error, str):
            return ProcessError(
                type="ProcessFailure",
                message=error,
                traceback="",
            )

        return ProcessError(
            type=type(error).__name__,
            message=str(error),
            traceback="".join(
                format_exception(
                    type(error),
                    error,
                    error.__traceback__,
                )
            ),
        )
