from __future__ import annotations
from typing import Any

from ..errors import ConstraintError, ConstraintType


class HashIndex:
    def __init__(self, *, unique: bool = False):
        self.unique = unique
        self._map: dict[Any, set[str]] = {}

    def add(self, row_id: str, value: Any) -> None:
        rows = self._map.setdefault(value, set())

        if self.unique and rows and row_id not in rows:
            # NOTE: might be RunTime Error will be better fit here
            raise ConstraintError(
                "Unique constraint violated", constraint_type=ConstraintType.UNIQUE
            )

        rows.add(row_id)

    def remove(self, row_id: str, value: Any) -> None:
        rows = self._map.get(value)
        if not rows:
            return

        rows.discard(row_id)
        if not rows:
            del self._map[value]

    def update(self, row_id: str, old_value: Any, new_value: Any) -> None:
        if old_value == new_value:
            return

        if old_value is not None:
            self.remove(row_id, old_value)

        if new_value is not None:
            self.add(row_id, new_value)

    def get_all(self, value: Any) -> set[str]:
        return self._map.get(value, set())

    def get_one(self, value: Any) -> str | None:
        rows = self._map.get(value)
        if not rows:
            return None
        return next(iter(rows))


class CompositeIndex:
    def __init__(self, fields: tuple[str, ...]):
        self.fields = fields
        self._map: dict[tuple[Any, ...], str] = {}

    def build_key(self, row: dict) -> tuple:
        return tuple(row.get(f) for f in self.fields)

    def add(self, row_id: str, row: dict):
        key = self.build_key(row)

        existing = self._map.get(key)
        if existing and existing != row_id:
            raise ConstraintError(
                "Composite unique constraint violated",
                constraint_type=ConstraintType.UNIQUE,
            )

        self._map[key] = row_id

    def remove(self, row_id: str, row: dict):
        key = self.build_key(row)
        if self._map.get(key) == row_id:
            del self._map[key]

    def update(self, row_id: str, old_row: dict, new_row: dict):
        old_key = self.build_key(old_row)
        new_key = self.build_key(new_row)

        if old_key == new_key:
            return

        self.remove(row_id, old_row)
        self.add(row_id, new_row)
