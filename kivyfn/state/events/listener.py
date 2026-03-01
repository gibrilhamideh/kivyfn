from __future__ import annotations

import weakref
from dataclasses import dataclass
from typing import Callable, Optional, Any

from .event import NodeEvent
from ..constants import InstructionOpCode


@dataclass(slots=True)
class Listener:
    """
    Internal reactive listener descriptor.

    Stores:
        - Weak reference to callback
        - Optional filtering constraints
    """

    _callback_ref: weakref.ReferenceType

    opcode: Optional[InstructionOpCode] = None
    id: Optional[str] = None
    key: Optional[str] = None

    # ============================================================
    # Construction
    # ============================================================

    @staticmethod
    def create(
        callback: Callable[[NodeEvent], Any],
        *,
        opcode: Optional[InstructionOpCode] = None,
        id: Optional[str] = None,
        key: Optional[str] = None,
    ) -> Listener:
        """
        Create listener with proper weak reference handling.
        """

        # Bound method
        if hasattr(callback, "__self__") and callback.__self__ is not None:
            ref = weakref.WeakMethod(callback)
        else:
            ref = weakref.ref(callback)

        return Listener(
            _callback_ref=ref,
            opcode=opcode,
            id=id,
            key=key,
        )

    # ============================================================
    # Runtime
    # ============================================================

    def callback(self) -> Optional[Callable[[NodeEvent], Any]]:
        """
        Returns live callback or None if dead.
        """
        return self._callback_ref()

    def matches(self, event: NodeEvent) -> bool:
        """
        Fast filtering logic.
        """

        if self.opcode is not None and event.opcode is not self.opcode:
            return False

        if self.id is not None and event.id != self.id:
            return False

        if self.key is not None and event.key != self.key:
            return False

        return True
