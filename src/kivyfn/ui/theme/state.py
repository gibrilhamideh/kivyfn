"""Material interaction styling, independent of application color roles."""

from __future__ import annotations

from collections.abc import Iterable, Sequence
from typing import Literal, TypeAlias

from kivy.event import EventDispatcher
from kivy.properties import BoundedNumericProperty

from kivyfn.ui.theme.utils import alpha


InteractionState: TypeAlias = Literal[
    "hovered", "focused", "pressed", "dragged", "selected", "disabled"
]


class ThemeState(EventDispatcher):
    """State layer and disabled opacity defaults, overridable per theme.

    Selection determines a component's base colors. Hover, focus, press, and
    drag layer over those colors; states may coexist. Disabled suppresses
    interaction layers. Components choose the source color for each layer.
    """

    hoveredOpacity = BoundedNumericProperty(0.08, min=0, max=1)
    focusedOpacity = BoundedNumericProperty(0.10, min=0, max=1)
    pressedOpacity = BoundedNumericProperty(0.10, min=0, max=1)
    draggedOpacity = BoundedNumericProperty(0.16, min=0, max=1)
    disabledContentOpacity = BoundedNumericProperty(0.38, min=0, max=1)
    disabledContainerOpacity = BoundedNumericProperty(0.12, min=0, max=1)

    def layer(
        self,
        color: Sequence[float],
        states: Iterable[InteractionState],
    ) -> list[float]:
        states = set(states)
        opacity = 0.0
        if "disabled" not in states:
            for state in ("dragged", "pressed", "focused", "hovered"):
                if state in states:
                    opacity = getattr(self, state + "Opacity")
                    break
        return alpha(color, opacity)
