# runtime/message.py
from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Literal


MessageType = Literal[
    "publish",
    "subscribe",
    "unsubscribe",
    "call",
    "reply",
    "disconnect",
    "stop",
]


@dataclass(frozen=True, slots=True)
class FnBusMessage:
    type: MessageType
    topic: str
    payload: Any = None
    source: str | None = None
    call_id: str | None = None
    error: str | None = None
