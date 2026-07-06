from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Literal


InputKind = Literal[
    "insert",
    "delete",
    "backspace",
    "paste",
    "replace",
]


@dataclass(slots=True, frozen=True)
class InputEvent:
    field: Any
    kind: InputKind
    before: Any
    after: Any
    text: str | None = None

    @property
    def is_insert(self) -> bool:
        return self.kind == "insert"

    @property
    def is_delete(self) -> bool:
        return self.kind in {"delete", "backspace"}

    @property
    def is_paste(self) -> bool:
        return self.kind == "paste"
