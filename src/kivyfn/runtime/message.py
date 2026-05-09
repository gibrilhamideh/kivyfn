# runtime/message.py
from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Literal


MessageType = Literal["publish", "subscribe", "unsubscribe"]


@dataclass(frozen=True)
class RuntimeMessage:
    type: MessageType
    topic: str
    payload: Any = None
    source: str | None = None
