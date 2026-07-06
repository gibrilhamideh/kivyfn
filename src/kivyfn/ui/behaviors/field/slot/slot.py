# kivyfn/ui/fields/behaviors/field/slot/slot.py
from __future__ import annotations

from typing import Any

from kivy.clock import Clock
from kivy.graphics import Color
from kivy.graphics.vertex_instructions import SmoothLine, SmoothRoundedRectangle
from kivy.properties import (
    BooleanProperty,
    ColorProperty,
    DictProperty,
    NumericProperty,
    VariableListProperty,
)


class FnFieldSlotBehavior:
    slot_highlight = BooleanProperty(True)
    slot_visuals = BooleanProperty(False)

    slot_background_color = ColorProperty((1, 0, 0, 0.2))
    slot_border_color = ColorProperty((0, 0, 0, 0))

    slot_background_focused_color = ColorProperty((0, 0, 0, 0))
    slot_border_focused_color = ColorProperty((0, 1, 0, 0.2))

    slot_border_width = NumericProperty(1)
    slot_radius = VariableListProperty([0], length=4)
    slot_padding = NumericProperty(5)

    _slot_graphics = DictProperty({})

    def __init__(self, **kwargs: Any) -> None:
        super().__init__(**kwargs)

        self._slot_graphics_trigger = Clock.create_trigger(
            self._update_slots_graphics,
            0,
        )

    def _clear_slots_graphics(self) -> None:
        for graphics in self._slot_graphics.values():
            for instruction in (
                graphics["bg_color"],
                graphics["bg"],
                graphics["border_color"],
                graphics["border"],
            ):
                try:
                    self.canvas.before.remove(instruction) # pyright: ignore
                except ValueError:
                    pass

        self._slot_graphics.clear()

    def _create_slots_graphics(self) -> None:
        self._clear_slots_graphics()

        instructions = []

        for slot in self._editable_positions:  # pyright: ignore
            bg_color = Color(*self.slot_background_color)

            bg = SmoothRoundedRectangle(
                pos=(0, 0),
                size=(0, 0),
                radius=self.slot_radius,
            )

            border_color = Color(*self.slot_border_color)

            border = SmoothLine(
                width=self.slot_border_width,
                rounded_rectangle=[0, 0, 0, 0, *self.slot_radius],
            )

            self._slot_graphics[slot] = {
                "bg_color": bg_color,
                "bg": bg,
                "border_color": border_color,
                "border": border,
            }

            instructions.extend([
                bg_color,
                bg,
                border_color,
                border,
            ])

        # Insert at the beginning of canvas.before,
        # before cursor Color and before text-color Color.
        for instruction in reversed(instructions):
            self.canvas.before.insert(0, instruction)  # pyright: ignore

        self._slot_graphics_trigger()

    def _update_slots_graphics(self, *_: Any) -> None:
        if not self._slot_graphics:
            return

        glyph_width = self._get_text_width( # pyright: ignore
            "0",
            self.tab_width, # pyright: ignore
            self._label_cached, # pyright: ignore
        )

        slot_width = glyph_width + (self.slot_padding * 2)
        slot_height = self.line_height + (self.slot_padding * 2) # pyright: ignore

        left: float | None = None
        right: float | None = None
        bottom: float | None = None
        top: float | None = None

        old_cursor = self.cursor

        for slot, graphics in self._slot_graphics.items():
            index = self._editable_positions.get(slot) # pyright: ignore

            if index is None:
                continue

            col, row = self.get_cursor_from_index(index) # pyright: ignore
            self.cursor = (col, row)

            x, y = self.cursor_pos # pyright: ignore
            y -= self.line_height # pyright: ignore

            x -= self.slot_padding
            y -= self.slot_padding

            graphics["bg"].pos = (x, y)
            graphics["bg"].size = (slot_width, slot_height)

            graphics["border"].width = self.slot_border_width
            graphics["border"].rounded_rectangle = [
                x,
                y,
                slot_width,
                slot_height,
                *self.slot_radius,
            ]

            slot_right = x + slot_width
            slot_top = y + slot_height

            if left is None:
                left = x
                right = slot_right
                bottom = y
                top = slot_top
            else:
                left = min(left, x)
                right = max(right, slot_right) # pyright: ignore
                bottom = min(bottom, y) # pyright: ignore
                top = max(top, slot_top) # pyright: ignore

        self.cursor = old_cursor

        if left is None or right is None or bottom is None or top is None:
            return

        self.width = right - left
        self.height = top - bottom

    def _update_slot_style(self) -> None:
        if not self._slot_graphics:
            return

        active = self._active_slot # pyright: ignore

        for slot, graphics in self._slot_graphics.items():
            if slot == active:
                graphics["bg_color"].rgba = self.slot_background_focused_color
                graphics["border_color"].rgba = self.slot_border_focused_color
            else:
                graphics["bg_color"].rgba = self.slot_background_color
                graphics["border_color"].rgba = self.slot_border_color

    def _unfocus_slots(self) -> None:
        for graphics in self._slot_graphics.values():
            graphics["bg_color"].rgba = self.slot_background_color
            graphics["border_color"].rgba = self.slot_border_color

    def on_size(self, instance, value) -> None:
        self._slot_graphics_trigger()

    def on_pos(self, *_: Any) -> None:
        self._slot_graphics_trigger()

    def on_slot_visuals(self, *_: Any) -> None:
        if self.slot_visuals:
            self._create_slots_graphics()
            self._update_slot_style()
        else:
            self._clear_slots_graphics()

    def on_slot_background_color(self, *_: Any) -> None:
        self._update_slot_style()

    def on_slot_border_color(self, *_: Any) -> None:
        self._update_slot_style()

    def on_slot_background_focused_color(self, *_: Any) -> None:
        self._update_slot_style()

    def on_slot_border_focused_color(self, *_: Any) -> None:
        self._update_slot_style()

    def on_slot_border_width(self, *_: Any) -> None:
        self._slot_graphics_trigger()

    def on_slot_padding(self, *_: Any) -> None:
        self._slot_graphics_trigger()

    def on_slot_radius(self, *_: Any) -> None:
        self._slot_graphics_trigger()
