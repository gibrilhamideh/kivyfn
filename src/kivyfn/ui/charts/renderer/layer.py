from __future__ import annotations

from typing import Any

from kivy.graphics import InstructionGroup


class ChartLayers:
    """Stable chart canvas groups with independent invalidation."""

    def __init__(self, canvas: Any) -> None:
        self.background = InstructionGroup(group="chart-background")
        self.grid = InstructionGroup(group="chart-grid")
        self.series = InstructionGroup(group="chart-series")
        self.overlay = InstructionGroup(group="chart-overlay")

        canvas.add(self.background)
        canvas.add(self.grid)
        canvas.add(self.series)
        canvas.add(self.overlay)

    @staticmethod
    def clear(group: InstructionGroup) -> None:
        group.clear()

    @classmethod
    def replace(
        cls,
        target: InstructionGroup,
        staged: InstructionGroup,
    ) -> None:
        """Atomically replace one layer after a successful staged render."""
        cls.clear(target)

        # Keep Kivy's implicit BindTexture / VertexInstruction pairs intact.
        # Removing individual children from a snapshot removes some implicit
        # instructions twice. A nested group also keeps the commit bounded.
        target.add(staged)
