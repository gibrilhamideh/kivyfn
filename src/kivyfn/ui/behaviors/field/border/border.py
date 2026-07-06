# kivyfn/ui/behaviors/field/border/border.py
from __future__ import annotations

from kivy.properties import (
    ColorProperty,
    NumericProperty,
    VariableListProperty,
    AliasProperty
)


class FnFieldBorderBehavior:
    border_color = ColorProperty(None, allownone=True)
    border_width = NumericProperty(1)
    radius = VariableListProperty([0], length=4)

    border_gap_x = NumericProperty(0)
    border_gap_width = NumericProperty(0)
    border_gap_padding = NumericProperty(0)


    def _get_border_gap_center(self) -> float:
        return (
            self.border_gap_x
            + (self.border_gap_width / 2)
            + (self.radius[0] / 2)
            + (self.border_gap_padding / 2)
        )

    border_gap_center = AliasProperty(
        _get_border_gap_center,
        None,
        bind=("border_gap_x", "border_gap_width", "border_gap_padding"),
        cache=True,
    )

