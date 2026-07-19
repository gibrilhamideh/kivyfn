# kivyfn/runtime/window/types.py
from __future__ import annotations

from typing import TYPE_CHECKING, TypeAlias

from kivyfn.runtime.process.types import (
    ProcessArgs,
    ProcessKwargs,
)


if TYPE_CHECKING:
    from kivyfn.app import FnApp


WindowArgs: TypeAlias = ProcessArgs
WindowKwargs: TypeAlias = ProcessKwargs
WindowFactory: TypeAlias = type["FnApp"]
