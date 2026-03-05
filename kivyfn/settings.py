from __future__ import annotations
import json
from pathlib import Path
from typing import Any


class AppSettings:
    """
    Persistent application settings.

    Stores user preferences (language, theme, etc.)
    and automatically saves them to disk.
    """

    def __init__(self, path: str | Path | None = None):
        self._path = Path(path or "settings.json")
        self._data: dict[str, Any] = {}

        self._load()

    # -------------------------
    # Loading / Saving
    # -------------------------

    def _load(self) -> None:
        if self._path.exists():
            try:
                self._data = json.loads(self._path.read_text())
            except Exception:
                self._data = {}

    def _save(self) -> None:
        self._path.write_text(json.dumps(self._data, indent=2))

    # -------------------------
    # API
    # -------------------------

    def get(self, key: str, default: Any = None) -> Any:
        return self._data.get(key, default)

    def set(self, key: str, value: Any) -> None:
        self._data[key] = value
        self._save()

    def remove(self, key: str) -> None:
        if key in self._data:
            del self._data[key]
            self._save()

    def clear(self) -> None:
        self._data.clear()
        self._save()

    # -------------------------
    # Dict-like access
    # -------------------------

    def __getitem__(self, key: str) -> Any:
        return self._data[key]

    def __setitem__(self, key: str, value: Any) -> None:
        self.set(key, value)

    def __contains__(self, key: str) -> bool:
        return key in self._data

    def as_dict(self) -> dict[str, Any]:
        return dict(self._data)
