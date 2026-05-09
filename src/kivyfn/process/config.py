from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass, field
from typing import Any, Generic, TypeVar

ProcessName = TypeVar("ProcessName", bound=str)


@dataclass(frozen=True)
class FnProcessConfig(Generic[ProcessName]):
    name: ProcessName
    target: Callable[..., None]
    args: tuple[Any, ...] = ()
    kwargs: dict[str, Any] = field(default_factory=dict)
