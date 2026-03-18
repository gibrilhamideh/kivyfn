from __future__ import annotations

from kivy.clock import Clock
from kivy.properties import (
    NumericProperty,
    BooleanProperty,
    ListProperty,
    OptionProperty,
    StringProperty,
    ColorProperty,
    VariableListProperty,
    DictProperty,
    AliasProperty,
)
from kivy.graphics import Color
from kivy.graphics.vertex_instructions import SmoothRoundedRectangle
from kivy.graphics.vertex_instructions import SmoothLine

from .field import FnFieldBaseBehavior


class FnCompositeFieldBehavior(FnFieldBaseBehavior):
    segments = ListProperty([])
    lengths = ListProperty([])
    separator = StringProperty(":")
    jump_chars = ListProperty([])

    segment_spacing = NumericProperty(0)
    segment_direction = OptionProperty("left", options=["left", "right"])
    editable_segments = ListProperty(None, allownone=True)

    auto_jump = BooleanProperty(True)
    unfocus_on_fill = BooleanProperty(False)

    segment_highlight = BooleanProperty(True)
    segment_visuals = BooleanProperty(False)
    segment_background_color = ColorProperty((0, 0, 0, 0))
    segment_border_color = ColorProperty((1, 0, 0, 1))
    segment_background_focused_color = ColorProperty((0, 0, 0, 0))
    segment_border_focused_color = ColorProperty((0, 1, 0, 1))
    segment_border_width = NumericProperty(1)
    segment_radius = VariableListProperty([0], length=4)
    segment_padding = VariableListProperty([20, 4, 20, 4], length=4)

    _segment_graphics = DictProperty({})

    def _get_is_complete(self):
        if not self.segments or not self.lengths:
            return False

        if len(self.segments) != len(self.lengths):
            return False

        for index, length in enumerate(self.lengths):
            if len(self.segments[index]) != length:
                return False

        return True

    completed = AliasProperty(
        _get_is_complete,
        None,
        bind=("segments", "lengths"),
    )

    def _get_default_segments(self):
        return ["" for _ in self.lengths]

    default_segments = AliasProperty(
        _get_default_segments,
        None,
        bind=("lengths",),
    )

    # ---------------------------------------------------------
    # Initialization
    # ---------------------------------------------------------
    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)

        self._active_segment = 0
        self._segment_cursor = 0

        self._editable_positions = {}
        self._segment_navigation = []
        self._segment_navigation_lookup = {}

        self._segment_graphics_trigger = Clock.create_trigger(
            self._update_segments_graphics, 0
        )
        self._active_trigger = Clock.create_trigger(self._apply_active_segment, -1)

    def on_kv_post(self, base_widget):
        super().on_kv_post(base_widget)  # pyright: ignore

        self.multiline = False
        self.cursor_width = 0
        self.cursor_blink = False

        self._rebuild_all()

    # ---------------------------------------------------------
    # Segment utilities
    # ---------------------------------------------------------
    def _get_segment_indices(self) -> list[int]:
        indices = list(range(len(self.lengths)))

        if self.segment_direction == "right":
            indices.reverse()

        return indices

    def _segment_editable(self, segment: int) -> bool:
        if self.editable_segments is None:
            return True
        return segment in self.editable_segments

    # ---------------------------------------------------------
    # Navigation ordering
    # ---------------------------------------------------------
    def _rebuild_segment_navigation(self) -> None:
        order = []

        for segment_index in self._get_segment_indices():
            if not self._segment_editable(segment_index):
                continue
            order.append(segment_index)

        self._segment_navigation = order
        self._segment_navigation_lookup = {
            segment: i for i, segment in enumerate(order)
        }

    def _get_adjacent_segment(self, segment: int, direction: int) -> int | None:
        idx = self._segment_navigation_lookup.get(segment)

        if idx is None:
            return None

        idx += direction

        if 0 <= idx < len(self._segment_navigation):
            return self._segment_navigation[idx]

        return None

    def _move_segment(self, direction: int) -> bool:
        nxt = self._get_adjacent_segment(self._active_segment, direction)
        if nxt is None:
            return False

        self._set_active_segment(nxt)
        return True

    # ---------------------------------------------------------
    # Display helpers
    # ---------------------------------------------------------
    def _get_segment_display_text(self, segment_index: int) -> str:
        value = self.segments[segment_index]

        if not self.segment_visuals:
            return value

        return value.ljust(self.lengths[segment_index])

    def _build_render_tokens(self):
        tokens = []
        last_segment = len(self.segments) - 1

        for segment_index, _segment in enumerate(self.segments):
            text = self._get_segment_display_text(segment_index)
            tokens.append((text, segment_index))

            if segment_index != last_segment:
                tokens.append((self.separator, None))

        return tokens

    # ---------------------------------------------------------
    # Rendering
    # ---------------------------------------------------------
    def _render(self):
        tokens = self._build_render_tokens()

        self._editable_positions.clear()

        parts: list[str] = []
        position = 0
        last_index = len(tokens) - 1

        for i, (text, segment_ref) in enumerate(tokens):
            parts.append(text)

            if segment_ref is not None:
                start = position
                end = position + len(text)
                self._editable_positions[segment_ref] = (start, end)

            position += len(text)

            if i == last_index:
                continue

            spacing = " " * self.segment_spacing
            parts.append(spacing)
            position += len(spacing)

        text = "".join(parts)
        if callable(self.formater) and not self.focus:
            formatted = self.formater(text, self.value)
            if isinstance(formatted, str):
                self.text = formatted
            else:
                self.text = text
        else:
            self.text = text

    # ---------------------------------------------------------
    # Rebuild
    # ---------------------------------------------------------
    def _rebuild_all(self):
        if not self.lengths:
            return

        if not self.segments or len(self.segments) != len(self.lengths):
            self.segments = self.default_segments
        else:
            normalized = []
            for index, length in enumerate(self.lengths):
                value = self.segments[index] if index < len(self.segments) else ""
                normalized.append(str(value)[:length])
            self.segments = normalized

        self._rebuild_segment_navigation()

        if self._segment_navigation:
            self._active_segment = self._segment_navigation[0]
            self._segment_cursor = len(self.segments[self._active_segment])

        self._render()

        if self.segment_visuals:
            self._create_segments_graphics()

    # ---------------------------------------------------------
    # Segment activation
    # ---------------------------------------------------------
    def _set_active_segment(self, segment: int):
        if segment not in self._segment_navigation_lookup:
            return

        self._active_segment = segment
        self._segment_cursor = len(self.segments[segment])
        self._active_trigger()

    def _apply_active_segment(self, *_):
        if not self.focus:
            return

        pos = self._editable_positions.get(self._active_segment)
        if pos is None:
            self.cancel_selection()  # pyright: ignore
            return

        start, end = pos
        cursor_pos = start + len(self.segments[self._active_segment])
        cursor_pos = min(cursor_pos, end)

        self.cursor = (cursor_pos, 0)

        # keep your current visual highlight behavior
        if self.segment_highlight and end > start:
            self.select_text(start, end)  # pyright: ignore
        else:
            self.cancel_selection()  # pyright: ignore

        if self.segment_visuals:
            self._update_segment_style()

    # ---------------------------------------------------------
    # Helpers
    # ---------------------------------------------------------
    def transform_char(self, char: str) -> str | None:
        return char

    def _get_nearest_segment_from_column(self, column: int) -> int:
        if not self._editable_positions:
            return self._active_segment

        for segment, (start, end) in self._editable_positions.items():
            if start <= column <= end:
                return segment

        def distance(item):
            _, (start, end) = item
            if column < start:
                return start - column
            if column > end:
                return column - end
            return 0

        segment, _ = min(self._editable_positions.items(), key=distance)
        return segment

    # ---------------------------------------------------------
    # Editing
    # ---------------------------------------------------------
    def insert_text(self, substring, from_undo=False):
        if self.readonly or not substring:  # pyright: ignore
            return

        segment = self._active_segment
        before = self.segments[:]
        updated = self.segments[:]
        accepted = []
        should_unfocus = False

        for ch in substring:
            if ch == self.separator or ch in self.jump_chars:
                next_segment = self._get_adjacent_segment(segment, 1)
                if next_segment is not None:
                    segment = next_segment
                continue

            ch = self.transform_char(ch)
            if not ch:
                continue

            if not self.validate_char(ch):
                continue

            current = updated[segment]
            max_length = self.lengths[segment]

            if len(current) >= max_length:
                if self.auto_jump:
                    next_segment = self._get_adjacent_segment(segment, 1)
                    if next_segment is None:
                        should_unfocus = self.unfocus_on_fill
                        break
                    segment = next_segment
                    current = updated[segment]
                    max_length = self.lengths[segment]
                else:
                    continue

            if len(current) >= max_length:
                should_unfocus = self.unfocus_on_fill
                break

            updated[segment] = current + ch
            accepted.append(ch)

            if self.auto_jump and len(updated[segment]) >= max_length:
                next_segment = self._get_adjacent_segment(segment, 1)
                if next_segment is None:
                    should_unfocus = self.unfocus_on_fill
                else:
                    segment = next_segment

        if not accepted:
            return

        if not self.validate_edit(before, updated, chars="".join(accepted)):
            return

        self.segments = updated
        self._render()
        self._set_active_segment(segment)

        if should_unfocus:
            self.focus = False

    def do_backspace(self, from_undo=False, mode="bkspc"):
        segment = self._active_segment
        before = self.segments[:]
        updated = self.segments[:]

        current = updated[segment]

        if current:
            updated[segment] = current[:-1]
        else:
            prev = self._get_adjacent_segment(segment, -1)
            if prev is None:
                return

            segment = prev
            current = updated[segment]

            if not current:
                self._set_active_segment(segment)
                return

            updated[segment] = current[:-1]

        if not self.validate_edit(before, updated, chars=None):
            return

        self.segments = updated
        self._render()
        self._set_active_segment(segment)

    def do_delete(self):
        # same behavior as backspace for this segment-editor model
        self.do_backspace()

    def delete_selection(self, from_undo=False):
        self.do_delete()

    def cut(self):
        if getattr(self, "selection_text", ""):
            self.copy()  # pyright: ignore
            self.do_delete()

    # ---------------------------------------------------------
    # Keyboard
    # ---------------------------------------------------------
    def _on_enter(self):
        if not self._move_segment(1):
            self.focus = False

    def keyboard_on_key_down(self, window, keycode, text, modifiers):
        if not self.focus:
            return super().keyboard_on_key_down(window, keycode, text, modifiers)  # pyright: ignore

        key = keycode[0]

        if key == 8:
            self.do_backspace()
            return True

        if key == 127:
            self.do_delete()
            return True

        if key == 9:
            direction = -1 if "shift" in modifiers else 1
            self._move_segment(direction)
            return True

        if key in (13, 271):
            self._on_enter()
            return True

        if key == 276:
            self._move_segment(-1)
            return True

        if key == 275:
            self._move_segment(1)
            return True

        return super().keyboard_on_key_down(window, keycode, text, modifiers)  # pyright: ignore

    def keyboard_on_textinput(self, window, text):
        if not self.focus:
            return super().keyboard_on_textinput(window, text)  # pyright: ignore

        if text == self.separator or text in self.jump_chars:
            self._move_segment(1)
            return True

        self.insert_text(text)
        return True

    # ---------------------------------------------------------
    # Focus
    # ---------------------------------------------------------
    def _on_textinput_focused(self, instance, value, *largs):  # pyright: ignore
        super()._on_textinput_focused(instance, value, *largs)

        if value:
            self._render()
            self._set_active_segment(self._active_segment)
        else:
            self._unfocus_segments()

    # ---------------------------------------------------------
    # Mouse
    # ---------------------------------------------------------
    def on_touch_up(self, touch):
        handled = super().on_touch_up(touch)  # pyright: ignore

        if self.collide_point(*touch.pos) and self.focus:  # pyright: ignore
            column, _ = self.get_cursor_from_xy(*touch.pos)  # pyright: ignore
            segment = self._get_nearest_segment_from_column(column)
            self._set_active_segment(segment)
            return True

        return handled

    # ---------------------------------------------------------
    # Segment graphics
    # ---------------------------------------------------------
    def _create_segments_graphics(self):
        for graphics in self._segment_graphics.values():
            self.canvas.after.remove(graphics["bg_color"])  # pyright: ignore
            self.canvas.after.remove(graphics["bg"])  # pyright: ignore
            self.canvas.after.remove(graphics["border_color"])  # pyright: ignore
            self.canvas.after.remove(graphics["border"])  # pyright: ignore

        self._segment_graphics.clear()

        with self.canvas.after:  # pyright: ignore
            for segment in self._editable_positions:
                bg_color = Color(*self.segment_background_color)

                bg = SmoothRoundedRectangle(
                    pos=(0, 0),
                    size=(0, 0),
                    radius=self.segment_radius,
                )

                border_color = Color(*self.segment_border_color)

                border = SmoothLine(
                    width=self.segment_border_width,
                    rounded_rectangle=[0, 0, 0, 0, *self.segment_radius],
                )

                self._segment_graphics[segment] = {
                    "bg_color": bg_color,
                    "bg": bg,
                    "border_color": border_color,
                    "border": border,
                }

        self._segment_graphics_trigger()

    def _update_segments_graphics(self, *_):
        if not self._segment_graphics:
            return

        pl, pt, pr, pb = self.segment_padding

        for segment, graphics in self._segment_graphics.items():
            start, _end = self._editable_positions.get(segment, (None, None))
            if start is None:
                continue

            col, row = self.get_cursor_from_index(start)  # pyright: ignore

            old_cursor = self.cursor
            self.cursor = (col, row)
            x, y = self.cursor_pos  # pyright: ignore
            y -= self.line_height  # pyright: ignore
            self.cursor = old_cursor

            sample = "0" * self.lengths[segment]
            glyph_width = self._get_text_width(  # pyright: ignore
                sample,
                self.tab_width,  # pyright: ignore
                self._label_cached,  # pyright: ignore
            )

            segment_width = glyph_width + pl + pr
            segment_height = self.line_height + pt + pb  # pyright: ignore

            x -= pl
            y -= pb

            graphics["bg"].pos = (x, y)
            graphics["bg"].size = (segment_width, segment_height)

            graphics["border"].rounded_rectangle = [
                x,
                y,
                segment_width,
                segment_height,
                *self.segment_radius,
            ]

    def _update_segment_style(self):
        if not self._segment_graphics:
            return

        active = self._active_segment

        for segment, graphics in self._segment_graphics.items():
            if segment == active:
                graphics["bg_color"].rgba = self.segment_background_focused_color
                graphics["border_color"].rgba = self.segment_border_focused_color
            else:
                graphics["bg_color"].rgba = self.segment_background_color
                graphics["border_color"].rgba = self.segment_border_color

    def _unfocus_segments(self):
        for graphics in self._segment_graphics.values():
            graphics["bg_color"].rgba = self.segment_background_color
            graphics["border_color"].rgba = self.segment_border_color

    # ---------------------------------------------------------
    # Property updates
    # ---------------------------------------------------------
    def on_lengths(self, *_):
        self._rebuild_all()

    def on_separator(self, *_):
        self._rebuild_all()

    def on_segment_spacing(self, *_):
        self._rebuild_all()

    def on_segment_visuals(self, *_):
        self._rebuild_all()

    def on_size(self, *args):
        self._segment_graphics_trigger()

    def on_pos(self, *args):
        self._segment_graphics_trigger()

    def on_segment_background_color(self, *_):
        self._update_segment_style()

    def on_segment_border_color(self, *_):
        self._update_segment_style()

    def on_segment_background_focused_color(self, *_):
        self._update_segment_style()

    def on_segment_border_focused_color(self, *_):
        self._update_segment_style()
