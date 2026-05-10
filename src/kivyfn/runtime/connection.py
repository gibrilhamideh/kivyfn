# kivyfn/runtime/connection.py

from __future__ import annotations

from dataclasses import dataclass
from multiprocessing.queues import Queue


@dataclass(frozen=True)
class FnBusConnection:
    name: str
    server_inbox: Queue
    client_inbox: Queue
