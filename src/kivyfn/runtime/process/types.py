# kivyfn/runtime/process/types.py
from __future__ import annotations

from collections.abc import Callable, Mapping
from typing import Any, Protocol, TYPE_CHECKING, TypeAlias
from multiprocessing.queues import Queue


if TYPE_CHECKING:
    from kivyfn.runtime.process.context import FnProcessContext
    from kivyfn.runtime.process.message import ProcessError
    from kivyfn.runtime.process.process import FnProcess


ProcessPayload: TypeAlias = dict[str, Any]
ProcessArgs: TypeAlias = tuple[Any, ...]
ProcessKwargs: TypeAlias = Mapping[str, Any]

ProcessTarget: TypeAlias = Callable[["FnProcessContext"], None]
ProcessStopCallback: TypeAlias = Callable[[], None]

ProcessReadyCallback: TypeAlias = Callable[
    ["FnProcess", ProcessPayload],
    None,
]

ProcessFailedCallback: TypeAlias = Callable[
    ["FnProcess", "ProcessError"],
    None,
]

ProcessExitCallback: TypeAlias = Callable[
    ["FnProcess", int | None],
    None,
]

ProcessLogQueue: TypeAlias = Queue[Any]


class ProcessStatusQueue(Protocol):
    def put(
        self,
        obj: Any,
        block: bool = True,
        timeout: float | None = None,
    ) -> None: ...

    def get(
        self,
        block: bool = True,
        timeout: float | None = None,
    ) -> Any: ...


class ProcessStopEvent(Protocol):
    def is_set(self) -> bool: ...

    def set(self) -> None: ...

    def wait(
        self,
        timeout: float | None = None,
    ) -> bool: ...
