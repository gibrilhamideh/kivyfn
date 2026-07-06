from __future__ import annotations

from typing import Any

from kivy.clock import Clock
from kivy.graphics import Color
from kivy.graphics.vertex_instructions import SmoothLine, SmoothRoundedRectangle
from kivy.properties import (
    BooleanProperty,
    ColorProperty,
    NumericProperty,
    OptionProperty,
    StringProperty,
    VariableListProperty,
)


class FnFieldCursorBehavior:
    cursor_box_visible = BooleanProperty(False)
    cursor_box_show_when_unfocused = BooleanProperty(False)

    cursor_box_color = ColorProperty((0.2, 0.45, 1, 0.18))
    cursor_box_border_color = ColorProperty((0.2, 0.45, 1, 0.65))

    cursor_box_border_width = NumericProperty(1)
    cursor_box_padding = NumericProperty(0)
    cursor_box_radius = VariableListProperty([3], length=4)

    cursor_box_end_mode = OptionProperty(
        "line",
        options=["box", "line"],
    )

    cursor_box_line_width = NumericProperty(2)

    cursor_box_width = NumericProperty(0)
    cursor_box_height = NumericProperty(0)
    cursor_box_measure_char = StringProperty("0")

    def __init__(self, **kwargs: Any) -> None:
        self._cursor_box_bg_color: Color | None = None
        self._cursor_box_bg: SmoothRoundedRectangle | None = None
        self._cursor_box_border_color_instruction: Color | None = None
        self._cursor_box_border: SmoothLine | None = None

        super().__init__(**kwargs)

        self._cursor_box_trigger = Clock.create_trigger(
            self._update_cursor_box,
            -1,
        )

        self.bind(  # pyright: ignore
            cursor=self._trigger_cursor_box_update,
            text=self._trigger_cursor_box_update,
            focus=self._trigger_cursor_box_update,
            pos=self._trigger_cursor_box_update,
            size=self._trigger_cursor_box_update,
            font_size=self._trigger_cursor_box_update,
            line_height=self._trigger_cursor_box_update,
            padding=self._trigger_cursor_box_update,
            cursor_box_visible=self._trigger_cursor_box_update,
            cursor_box_color=self._trigger_cursor_box_update,
            cursor_box_border_color=self._trigger_cursor_box_update,
            cursor_box_border_width=self._trigger_cursor_box_update,
            cursor_box_padding=self._trigger_cursor_box_update,
            cursor_box_radius=self._trigger_cursor_box_update,
            cursor_box_end_mode=self._trigger_cursor_box_update,
            cursor_box_line_width=self._trigger_cursor_box_update,
            cursor_box_width=self._trigger_cursor_box_update,
            cursor_box_height=self._trigger_cursor_box_update,
            cursor_box_measure_char=self._trigger_cursor_box_update,
        )

    def show_cursor_box(self) -> None:
        self.cursor_box_visible = True
        self._trigger_cursor_box_update()

    def hide_cursor_box(self) -> None:
        self.cursor_box_visible = False
        self._trigger_cursor_box_update()

    def refresh_cursor_box(self) -> None:
        self._trigger_cursor_box_update()

    def _ensure_cursor_box_graphics(self) -> None:
        if self._cursor_box_bg is not None:
            return

        with self.canvas.after:  # pyright: ignore
            self._cursor_box_bg_color = Color(0, 0, 0, 0)

            self._cursor_box_bg = SmoothRoundedRectangle(
                pos=(0, 0),
                size=(0, 0),
                radius=self.cursor_box_radius,
            )

            self._cursor_box_border_color_instruction = Color(0, 0, 0, 0)

            self._cursor_box_border = SmoothLine(
                width=self.cursor_box_border_width,
                rounded_rectangle=[
                    0,
                    0,
                    0,
                    0,
                    *self.cursor_box_radius,
                ],
            )

    def _trigger_cursor_box_update(self, *_: Any) -> None:
        self._cursor_box_trigger()

    def _cursor_box_should_draw(self) -> bool:
        if not self.cursor_box_visible:
            return False

        if self.focus:  # pyright: ignore
            return True

        return bool(self.cursor_box_show_when_unfocused)

    def _hide_cursor_box_graphics(self) -> None:
        if self._cursor_box_bg_color is not None:
            self._cursor_box_bg_color.rgba = (0, 0, 0, 0)

        if self._cursor_box_border_color_instruction is not None:
            self._cursor_box_border_color_instruction.rgba = (0, 0, 0, 0)

    def _get_cursor_box_width(self) -> float:
        if self.cursor_box_width > 0:
            return self.cursor_box_width

        measure_char = self.cursor_box_measure_char or "0"
        measure_char = measure_char[0]

        return self._get_text_width(  # pyright: ignore
            measure_char,
            self.tab_width,  # pyright: ignore
            self._label_cached,  # pyright: ignore
        )

    def _get_cursor_box_height(self) -> float:
        if self.cursor_box_height > 0:
            return self.cursor_box_height

        return self.line_height  # pyright: ignore

    def _cursor_box_is_at_end(self) -> bool:
        try:
            return self.cursor_index() >= len(self.text)  # pyright: ignore
        except Exception:
            return False

    def _cursor_box_should_draw_line(self) -> bool:
        return (
            self.cursor_box_end_mode == "line"
            and self._cursor_box_is_at_end()
        )

    def _update_cursor_box(self, *_: Any) -> None:
        self._ensure_cursor_box_graphics()

        if not self._cursor_box_should_draw():
            self._hide_cursor_box_graphics()
            return

        if (
            self._cursor_box_bg_color is None
            or self._cursor_box_bg is None
            or self._cursor_box_border_color_instruction is None
            or self._cursor_box_border is None
        ):
            return

        x, y = self.cursor_pos  # pyright: ignore

        width = self._get_cursor_box_width()
        height = self._get_cursor_box_height()
        padding = self.cursor_box_padding

        draw_line = self._cursor_box_should_draw_line()

        if draw_line:
            box_x = x
            box_width = max(1, self.cursor_box_line_width)
            radius = [0, 0, 0, 0]

            bg_color = self.cursor_box_border_color
            border_color = self.cursor_box_border_color
        else:
            box_x = x - padding
            box_width = width + (padding * 2)
            radius = self.cursor_box_radius

            bg_color = self.cursor_box_color
            border_color = [0, 0, 0, 0]

        box_y = y - self.line_height - padding  # pyright: ignore
        box_height = height + (padding * 2)

        self._cursor_box_bg_color.rgba = bg_color
        self._cursor_box_bg.pos = (box_x, box_y)
        self._cursor_box_bg.size = (box_width, box_height)
        self._cursor_box_bg.radius = radius

        self._cursor_box_border_color_instruction.rgba = border_color # pyright: ignore
        self._cursor_box_border.width = self.cursor_box_border_width
        self._cursor_box_border.rounded_rectangle = [  # pyright: ignore
            box_x,
            box_y,
            box_width,
            box_height,
            *radius,
        ]
