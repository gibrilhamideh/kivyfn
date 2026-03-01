from __future__ import annotations
from typing import Any, TYPE_CHECKING

import uuid


from .index import HashIndex, CompositeIndex

from ..address import Address
from ..errors import NodeError, FieldError, ConstraintError
from ..events.event import NodeEvent
from ..events.listener import Listener
from ..events.subscription import Subscription

if TYPE_CHECKING:
    from ..schema import Schema


class Node:
    """
    A Node represents one depth in the tree.

    - `value` holds data at this depth
      - single item if many=False
      - list of items if many=True
    - `children` holds deeper nodes (structure only)
    """

    def __init__(
        self,
        schema: type[Schema],
    ) -> None:
        self._indexes: dict[str, HashIndex] = {}
        self._composite_indexes: list[CompositeIndex] = []

        # --- register Indexes
        for field_name in schema.indexed_fields():
            field = schema.get_field(field_name)
            self._indexes[field_name] = HashIndex(unique=field.unique)

        for fields in schema.__composite_uniques__:
            self._composite_indexes.append(CompositeIndex(fields))

        # --- Listeners
        self._listeners: dict[str, Listener] = {}

        # --- register nodes
        self.schema = schema
        self.name = None
        self.parent = None
        self.children: dict[str | int, Node] = {}
        self.value: dict = {}

    def __repr__(self) -> str:
        schema_name = self.schema.__name__
        return f"Node(schema={schema_name}, children={len(self.children)})"

    # ---------------------------
    # build
    # ---------------------------
    def build(self, data: dict | None):
        if self.schema.many:
            if isinstance(data, dict):
                for id, row in data.items():
                    if not isinstance(row, dict):
                        continue

                    cast = {}
                    for name, field in self.schema.fields().items():
                        try:
                            value = row[name]
                            cast[name] = self.schema.challenge_field(name, value)
                        except FieldError:
                            cast[name] = field.defualt

                        except KeyError:
                            continue

                        index = self.indexes.get(name)
                        if index is not None:
                            try:
                                index.add(row_id=id, value=cast[name])
                            except ConstraintError:
                                del cast[name]

                    for composite in self._composite_indexes:
                        composite.add(id, cast)

                    self.value[id] = cast

        else:
            if isinstance(data, dict):
                cast = {}
                for name, field in self.schema.fields().items():
                    try:
                        value = data[name]
                        cast[name] = self.schema.challenge_field(name, value)
                    except FieldError:
                        cast[field] = field.defualt

                    except KeyError:
                        pass

                self.value = cast

            else:
                self.value = self.schema.defaults()

    # ---------------------------
    # Utilities
    # ---------------------------
    def add_child(self, name: str, node: "Node") -> None:
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
        """
        Register reactive listener on this node.

        Returns Subscription handle.
        """

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
        """
        Internal dispatch after commit.
        """

        dead_tokens = []

        for token, listener in self._listeners.items():
            callback = listener.callback()

            # Auto-cleanup dead weakrefs
            if callback is None:
                dead_tokens.append(token)
                continue

            if listener.matches(event):
                callback(event)

        # Cleanup dead listeners
        for token in dead_tokens:
            self._listeners.pop(token, None)

    # ---------------------------
    # Index lookup
    # ---------------------------
    @property
    def indexes(self):
        return self._indexes.copy()

    @property
    def composite_indexes(self):
        return self._composite_indexes.copy()

    def lookup(self, field: str, value: Any) -> set[str]:
        index = self._indexes.get(field)
        if not index:
            return set()
        return index.get_all(value)

    def lookup_unique(self, field: str, value: Any) -> str | None:
        index = self._indexes.get(field)
        if not index:
            return None
        return index.get_one(value)
