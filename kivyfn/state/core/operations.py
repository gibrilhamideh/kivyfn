from __future__ import annotations
from typing import cast, TYPE_CHECKING

from .instruction import Instruction
from ..events.event import NodeEvent


if TYPE_CHECKING:
    from ..node import Node


class Operation:
    def __init__(self, instruction: Instruction) -> None:
        self.instruction = instruction
        self.address = instruction.address
        self.opcode = instruction.opcode
        self.source = instruction.source

    def execute(self):
        raise NotImplementedError()

    def undo(self):
        raise NotImplementedError()

    # ----------------------------
    # Debug Representation
    # ----------------------------
    def _repr_details(self) -> str:
        return ""

    def __repr__(self) -> str:
        base = f"address={self.address}, source={self.source.name}"

        details = self._repr_details()

        if details:
            return f"{self.__class__.__name__}({base}, {details})"

        return f"{self.__class__.__name__}({base})"


class SetOperation(Operation):
    def __init__(self, node: Node, instruction: Instruction):
        super().__init__(instruction)
        self.node = node
        self.key = instruction.key
        self.new_value = instruction.value
        self.old_value = None

    def _repr_details(self):
        return f"key={self.key!r}, value={self.new_value!r}"

    def execute(self):
        self.old_value = self.node.value.get(self.key)
        self.node.value[self.key] = self.new_value

        return NodeEvent(
            opcode=self.opcode,
            address=self.node.address(),
            key=self.key,
            old_value=self.old_value,
            new_value=self.new_value,
        )

    def undo(self):
        current = self.node.value.get(self.key)
        self.node.value[self.key] = self.old_value

        return NodeEvent(
            opcode=self.opcode,
            address=self.node.address(),
            key=self.key,
            old_value=current,
            new_value=self.old_value,
        )


class SetRowOperation(Operation):
    def __init__(self, node: Node, instruction: Instruction):
        super().__init__(instruction)
        self.node = node
        self.id = instruction.id
        self.key = cast(str, instruction.key)
        self.new_value = instruction.value
        self.old_value = None

    def _repr_details(self):
        return f"id={self.id!r}, key={self.key!r}, value={self.new_value!r}"

    def execute(self):
        row = self.node.value[self.id]
        self.old_value = row.get(self.key)

        index = self.node.indexes.get(self.key)
        if index:
            index.update(self.id, self.old_value, self.new_value)

        row[self.key] = self.new_value

        return NodeEvent(
            opcode=self.opcode,
            address=self.node.address(),
            id=self.id,
            key=self.key,
            old_value=self.old_value,
            new_value=self.new_value,
        )

    def undo(self):
        row = self.node.value[self.id]
        current = row.get(self.key)

        index = self.node.indexes.get(self.key)
        if index:
            index.update(self.id, self.new_value, self.old_value)

        row[self.key] = self.old_value

        return NodeEvent(
            opcode=self.opcode,
            address=self.node.address(),
            id=self.id,
            key=self.key,
            old_value=current,
            new_value=self.old_value,
        )


class InsertOperation(Operation):
    def __init__(self, node: Node, instruction: Instruction):
        super().__init__(instruction)
        self.node = node
        self.id = instruction.id
        self.value = cast(dict, instruction.value)

    def execute(self):
        self.node.value[self.id] = self.value

        for field, index in self.node.indexes.items():
            value = self.value.get(field)
            if value is not None:
                index.add(self.id, value)

        return NodeEvent(
            opcode=self.opcode,
            address=self.node.address(),
            id=self.id,
            new_value=self.value,
        )

    def undo(self):
        row = self.node.value[self.id]

        for field, index in self.node.indexes.items():
            value = row.get(field)
            if value is not None:
                index.remove(self.id, value)

        del self.node.value[self.id]

        return NodeEvent(
            opcode=self.opcode,  # REMOVE
            address=self.node.address(),
            id=self.id,
            old_value=row,
        )

    def _repr_details(self):
        return f"id={self.id!r}, value={self.value!r}"


class RemoveOperation(Operation):
    def __init__(self, node: Node, instruction: Instruction):
        super().__init__(instruction)
        self.node = node
        self.id = instruction.id
        self.old_row = {}

    def _repr_details(self):
        return f"id={self.id!r}"

    def execute(self):
        self.old_row = self.node.value[self.id]

        for field, index in self.node.indexes.items():
            value = self.old_row.get(field)
            if value is not None:
                index.remove(self.id, value)

        del self.node.value[self.id]

        return NodeEvent(
            opcode=self.opcode,
            address=self.node.address(),
            id=self.id,
            old_value=self.old_row,
        )

    def undo(self):
        self.node.value[self.id] = self.old_row

        for field, index in self.node.indexes.items():
            value = self.old_row.get(field)
            if value is not None:
                index.add(self.id, value)

        return NodeEvent(
            opcode=self.opcode,  # INSERT
            address=self.node.address(),
            id=self.id,
            new_value=self.old_row,
        )
