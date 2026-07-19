# kivyfn/runtime/process/state.py
from __future__ import annotations

from enum import StrEnum


class FnProcessState(StrEnum):
    REGISTERED = "registered"
    STARTING = "starting"
    READY = "ready"
    STOPPING = "stopping"
    EXITED = "exited"
    FAILED = "failed"
