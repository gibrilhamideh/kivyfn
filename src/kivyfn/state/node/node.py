from __future__ import annotations

from typing import Any, TYPE_CHECKING
import uuid

from .index import IndexManager

from ..address import Address
from ..errors import NodeError
from ..events.event import NodeEvent
from ..events.listener import Listener
from ..events.subscription import Subscription

if TYPE_CHECKING:
    from ..schema import Schema


class Node:
    def __init__(self, schema: type[Schema]) -> None:
        self.schema = schema

        self.name: str | int | None = None
        self.parent: Node | None = None
        self.children: dict[str | int, Node] = {}

        # many=True  -> {row_id: row}
        # many=False -> {field: value}
        self.value: dict = {}

        self._indexes = IndexManager(schema)
        self._listeners: dict[str, Listener] = {}

    def __repr__(self) -> str:
        return f"Node(schema={self.schema.__name__}, children={len(self.children)})"

    # ---------------------------
    # Build / boot
    # ---------------------------
    def build(self, data: dict | None) -> None:
        if self.schema.many:
            self._build_many(data)
        else:
            self._build_single(data)

    def _build_many(self, data: dict | None) -> None:
        self.value = {}
        self._indexes = IndexManager(self.schema)

        if not isinstance(data, dict):
            return

        for row_id, row in data.items():
            if not isinstance(row, dict):
                continue

            try:
                prepared = self._build_default(row)
                self.insert(str(row_id), prepared)
            except Exception:
                # corrupted row / invalid field / index conflict during boot
                continue

    def _build_single(self, data: dict | None) -> None:
        if not isinstance(data, dict):
            data = {}

        self.value = self._build_default(data)

    def _build_default(self, row: dict) -> dict:
        """
        Build a complete row from schema defaults + provided data.

        No casting.
        No normalization.
        Only:
        - fill missing fields with defaults
        - validate final values
        """

        built = {}

        for name, field in self.schema.fields().items():
            if name in row:
                value = row[name]
            else:
                value = getattr(field, "default", None)

            self.schema.challenge_field(name, value)
            built[name] = value

        return built

    # ---------------------------
    # Tree
    # ---------------------------
    def add_child(self, name: str | int, node: Node) -> None:
        if name in self.children:
            raise NodeError(f"Child '{name}' already exists")

        node.parent = self
        node.name = name
        self.children[name] = node

    def address(self) -> Address:
        parts = []
        node = self

        while node.parent is not None:
            parts.append(node.name)
            node = node.parent

        parts.reverse()
        return Address(*parts)

    # ---------------------------
    # Data API used by operations
    # ---------------------------
    def insert(self, row_id: str, row: dict) -> None:
        if not self.schema.many:
            raise NodeError("insert() is only valid for many schemas")

        if row_id in self.value:
            raise NodeError(f"Row '{row_id}' already exists")

        built = self._build_default(row)

        self._indexes.add(row_id, built)
        self.value[row_id] = built

    def set_row(self, row_id: str, key: str, value: Any) -> Any:
        if not self.schema.many:
            raise NodeError("set_row() is only valid for many schemas")

        if row_id not in self.value:
            raise NodeError(f"Row '{row_id}' does not exist")

        old_row = dict(self.value[row_id])
        old_value = old_row.get(key)

        self.schema.challenge_field(key, value)

        new_row = dict(old_row)
        new_row[key] = value

        self._indexes.update(row_id, old_row, new_row)
        self.value[row_id] = new_row

        return old_value

    def remove(self, row_id: str) -> dict:
        if not self.schema.many:
            raise NodeError("remove() is only valid for many schemas")

        if row_id not in self.value:
            raise NodeError(f"Row '{row_id}' does not exist")

        old_row = dict(self.value[row_id])

        self._indexes.remove(row_id, old_row)
        del self.value[row_id]

        return old_row

    def set(self, key: str, value: Any) -> Any:
        if self.schema.many:
            raise NodeError("set() is only valid for single schemas")

        self.schema.challenge_field(key, value)

        old_value = self.value.get(key)
        self.value[key] = value

        return old_value

    # ---------------------------
    # Read / lookup API
    # ---------------------------
    def exists(self, row_id: str) -> bool:
        if not self.schema.many:
            raise NodeError("exists() is only valid for many schemas")

        return row_id in self.value

    def get(self, row_id: str | None = None) -> dict | None:
        if self.schema.many:
            if row_id is None:
                raise NodeError("row_id is required for many schemas")

            row = self.value.get(row_id)
            return dict(row) if row is not None else None

        return dict(self.value)

    def lookup(
        self,
        fields: str | tuple[str, ...],
        value: Any,
        *,
        first: bool = False,
    ) -> set[str] | str | None:
        return self._indexes.lookup(fields, value, first=first)

    # ---------------------------
    # Subscriptions
    # ---------------------------
    def subscribe(
        self,
        callback,
        *,
        opcode=None,
        id=None,
        key=None,
    ) -> Subscription:
        token = uuid.uuid4().hex

        listener = Listener.create(
            callback,
            opcode=opcode,
            id=id,
            key=key,
        )

        self._listeners[token] = listener
        return Subscription(self, token)

    def unsubscribe(self, token: str) -> None:
        self._listeners.pop(token, None)

    def dispatch(self, event: NodeEvent) -> None:
        dead_tokens = []

        for token, listener in self._listeners.items():
            callback = listener.callback()

            if callback is None:
                dead_tokens.append(token)
                continue

            if listener.matches(event):
                callback(event)

        for token in dead_tokens:
            self._listeners.pop(token, None)
