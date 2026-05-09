# runtime/state.py

from __future__ import annotations

from typing import Any


class RuntimeState:
    def __init__(self) -> None:
        self._values: dict[str, Any] = {}

    def get(self, key: str, default: Any = None) -> Any:
        return self._values.get(key, default)

    def set(self, key: str, value: Any) -> None:
        self._values[key] = value

    def snapshot(self, prefix: str | None = None) -> dict[str, Any]:
        if prefix is None:
            return dict(self._values)

        prefix = prefix + "."

        return {
            key[len(prefix):]: value
            for key, value in self._values.items()
            if key.startswith(prefix)
        }

    def remove(self, key: str) -> None:
        self._values.pop(key, None)

    def clear(self) -> None:
        self._values.clear()
