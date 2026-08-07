from __future__ import annotations

from collections.abc import Callable, Iterable, Iterator
from contextlib import contextmanager
from typing import Any


DatasetCallback = Callable[["ChartDataset"], None]


class ChartDataset:
    """Observable row storage shared by one or more chart series."""

    def __init__(self, rows: Iterable[Any] = ()) -> None:
        self._rows = list(rows)
        self._callbacks: list[DatasetCallback] = []
        self._revision = 0
        self._batch_depth = 0
        self._batch_dirty = False

    @property
    def revision(self) -> int:
        return self._revision

    @property
    def rows(self) -> tuple[Any, ...]:
        return tuple(self._rows)

    def __len__(self) -> int:
        return len(self._rows)

    def __iter__(self) -> Iterator[Any]:
        return iter(self._rows)

    def __getitem__(self, index: int) -> Any:
        return self._rows[index]

    def append(self, row: Any) -> None:
        self._rows.append(row)
        self._changed()

    def extend(self, rows: Iterable[Any]) -> None:
        additions = list(rows)
        if not additions:
            return

        self._rows.extend(additions)
        self._changed()

    def replace(self, rows: Iterable[Any]) -> None:
        replacement = list(rows)
        self._rows = replacement
        self._changed()

    def remove_before(
        self,
        value: Any,
        *,
        key: Callable[[Any], Any] | None = None,
    ) -> int:
        selector = key or (lambda row: row[0])
        first_kept = 0

        for first_kept, row in enumerate(self._rows):
            if selector(row) >= value:
                break
        else:
            first_kept = len(self._rows)

        if first_kept == 0:
            return 0

        del self._rows[:first_kept]
        self._changed()
        return first_kept

    def clear(self) -> None:
        if not self._rows:
            return

        self._rows.clear()
        self._changed()

    def subscribe(self, callback: DatasetCallback) -> None:
        if callback not in self._callbacks:
            self._callbacks.append(callback)

    def unsubscribe(self, callback: DatasetCallback) -> None:
        if callback in self._callbacks:
            self._callbacks.remove(callback)

    @contextmanager
    def update(self) -> Iterator[ChartDataset]:
        self._batch_depth += 1

        try:
            yield self
        finally:
            self._batch_depth -= 1

            if self._batch_depth == 0 and self._batch_dirty:
                self._batch_dirty = False
                self._dispatch()

    def _changed(self) -> None:
        self._revision += 1

        if self._batch_depth:
            self._batch_dirty = True
            return

        self._dispatch()

    def _dispatch(self) -> None:
        for callback in tuple(self._callbacks):
            callback(self)
