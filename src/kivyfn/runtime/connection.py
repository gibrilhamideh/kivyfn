# kivyfn/runtime/connection.py

from __future__ import annotations

from dataclasses import dataclass
from multiprocessing.queues import Queue


@dataclass(frozen=True)
class RuntimeConnection:
    name: str
    host_inbox: Queue
    inbox: Queue
