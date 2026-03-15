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


# _format, edtibale_segemnts, sequential segments
class FnSegmentedFieldBehavior(FnFieldBaseBehavior):
    lengths = ListProperty([])
    separator = StringProperty(":")
    spacing = StringProperty("")
    placeholder = StringProperty("_")

    segments = ListProperty([])

    segment_direction = OptionProperty("left", options=["left", "right"])
    segment_fill_direction = OptionProperty("left", options=["left", "right"])
    editable_segments = ListProperty(None, allownone=True)
    sequential = BooleanProperty(False)

    unfocus_on_fill = BooleanProperty(False)

    slot_visuals = BooleanProperty(False)
    slot_background_color = ColorProperty((1, 0, 0, 0.2))
    slot_border_color = ColorProperty((0, 0, 0, 0))
    slot_background_focused_color = ColorProperty((0, 0, 0, 0))
    slot_border_focused_color = ColorProperty((0, 1, 0, 0.2))
    slot_border_width = NumericProperty(1)
    slot_radius = VariableListProperty([0], length=4)
    slot_padding = NumericProperty(5)

    _slot_graphics = DictProperty({})

    def _get_is_complete(self):
        if not self.segments:
            return False

        for seg in self.segments:
            for ch in seg:
                if ch is None:
                    return False

        return True

    completed = AliasProperty(
        _get_is_complete,
        None,
        bind=("value",),
    )

    # ---------------------------------------------------------
    # Initialization
    # ---------------------------------------------------------
    def __init__(self, **kwargs) -> None:
        self._active_ev = None
        self._active_segment = 0
        self._active_char = 0

        self._editable_positions = {}
        self._slot_order = []
        self._slot_order_index = {}

        self._highlight_ev = None
        super().__init__(**kwargs)

    def on_kv_post(self, base_widget):
        super().on_kv_post(base_widget)  # pyright: ignore

        self.multiline = False
        self.cursor_width = 0
        self.cursor_blink = False

        if self.default is not None and self.value is None:
            self.value = self.default

        self._rebuild_all()

        if self.slot_visuals:
            self._create_slots_graphics()
            self._schedule_slots_update()

    # ---------------------------------------------------------
    # Segment utilities
    # ---------------------------------------------------------

    def _normalize_segments(self):
        normalized = []

        for i, length in enumerate(self.lengths):
            value = self.segments[i] if i < len(self.segments) else None
            chars = [None] * length

            if value:
                raw = value if isinstance(value, list) else list(str(value))
                for j, ch in enumerate(raw[:length]):
                    chars[j] = None if ch is None else str(ch)[:1]

            normalized.append(chars)

        self.segments = normalized

    def _segment_indices(self):
        if self.segment_direction == "left":
            return range(len(self.lengths))
        return range(len(self.lengths) - 1, -1, -1)

    def _char_indices(self, seg):
        length = self.lengths[seg]
        if self.segment_fill_direction == "left":
            return range(length)
        return range(length - 1, -1, -1)

    # ---------------------------------------------------------
    # Slot ordering
    # ---------------------------------------------------------

    def _rebuild_slot_order(self):
        order = []

        for seg in self._segment_indices():
            if not self._segment_editable(seg):
                continue
            for ch in self._char_indices(seg):
                order.append((seg, ch))

        self._slot_order = order
        self._slot_order_index = {slot: i for i, slot in enumerate(order)}

    def _segment_editable(self, seg):
        if self.editable_segments is None:
            return True
        return seg in self.editable_segments

    # ---------------------------------------------------------
    # Rendering
    # ---------------------------------------------------------

    def _build_tokens(self):
        tokens = []

        for seg_i, seg in enumerate(self.segments):
            for ch_i, ch in enumerate(seg):
                tokens.append((ch if ch else self.placeholder, (seg_i, ch_i)))

            if seg_i < len(self.segments) - 1:
                tokens.append((self.separator, None))

        return tokens

    def _render(self):
        tokens = self._build_tokens()

        self._editable_positions.clear()

        parts = []
        pos = 0

        for i, (text, ref) in enumerate(tokens):
            parts.append(text)

            if ref:
                self._editable_positions[ref] = pos

            pos += len(text)

            if i < len(tokens) - 1:
                parts.append(self.spacing)
                pos += len(self.spacing)

        self.text = "".join(parts)

    # ---------------------------------------------------------
    # Highlight
    # ---------------------------------------------------------

    def _highlight(self):
        if not self.focus:
            self.cancel_selection()  # pyright: ignore
            return

        pos = self._editable_positions.get((self._active_segment, self._active_char))

        if pos is None:
            self.cancel_selection()  # pyright: ignore
            return

        self.cursor = (pos, 0)
        self.select_text(pos, pos + 1)  # pyright: ignore

    def _schedule_highlight(self):
        if self._highlight_ev:
            self._highlight_ev.cancel()

        self._highlight_ev = Clock.schedule_once(lambda *_: self._highlight(), 0)

    # ---------------------------------------------------------
    # Slot graphics
    # ---------------------------------------------------------
    def _create_slots_graphics(self):
        # avoid recreating graphics
        if self._slot_graphics:
            return
        with self.canvas.after:  # pyright: ignore
            for slot in self._editable_positions.keys():
                # background
                bg_color = Color(*self.slot_background_color)

                bg = SmoothRoundedRectangle(
                    pos=(0, 0),
                    size=(0, 0),
                    radius=self.slot_radius,
                )

                # border
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

    def _schedule_slots_update(self):
        Clock.schedule_once(self._update_slots_graphics, 0)

    def _update_slots_graphics(self, *_):
        # nothing to update
        if not self._slot_graphics:
            return

        for slot, graphics in self._slot_graphics.items():
            index = self._editable_positions.get(slot)

            if index is None:
                continue

            # index -> cursor location
            col, row = self.get_cursor_from_index(index)  # pyright: ignore

            # temporarily move cursor to compute pixel position
            old_cursor = self.cursor
            self.cursor = (col, row)
            x, y = self.cursor_pos  # pyright: ignore
            y -= self.line_height  # pyright: ignore
            self.cursor = old_cursor

            # slot size based on glyph metrics
            glyph_width = self._get_text_width("0", self.tab_width, self._label_cached)  # pyright: ignore

            slot_width = glyph_width + (self.slot_padding * 2)
            slot_height = self.line_height + (self.slot_padding * 2)  # pyright: ignore

            # offset so slot surrounds glyph
            x -= self.slot_padding
            y -= self.slot_padding

            # update background rectangle
            graphics["bg"].pos = (x, y)
            graphics["bg"].size = (slot_width, slot_height)

            # update border
            graphics["border"].rounded_rectangle = [
                x,
                y,
                slot_width,
                slot_height,
                *self.slot_radius,
            ]

    def _update_slot_style(self):
        if not self._slot_graphics:
            return

        active = (self._active_segment, self._active_char)

        for slot, graphics in self._slot_graphics.items():
            if slot == active:
                graphics["bg_color"].rgba = self.slot_background_focused_color
                graphics["border_color"].rgba = self.slot_border_focused_color
            else:
                graphics["bg_color"].rgba = self.slot_background_color
                graphics["border_color"].rgba = self.slot_border_color

    def _unfocus_slots(self):
        for graphics in self._slot_graphics.values():
            graphics["bg_color"].rgba = self.slot_background_color
            graphics["border_color"].rgba = self.slot_border_color

    # ---------------------------------------------------------
    # Slot navigation
    # ---------------------------------------------------------
    def _slot_move(self, seg, char, direction):
        idx = self._slot_order_index.get((seg, char))

        if idx is None:
            return None

        idx += direction

        if 0 <= idx < len(self._slot_order):
            return self._slot_order[idx]

        return None

    def _visual_prev(self, seg, char):
        if char > 0:
            return seg, char - 1

        if seg > 0:
            return seg - 1, self.lengths[seg - 1] - 1

        return None

    def _visual_next(self, seg, char):
        if char + 1 < self.lengths[seg]:
            return seg, char + 1

        if seg + 1 < len(self.lengths):
            return seg + 1, 0

        return None

    def _first_empty_slot(self):
        for seg, char in self._slot_order:
            if self.segments[seg][char] is None:
                return seg, char

        # if all slots are filled
        if self._slot_order:
            return self._slot_order[-1]

        return None

    def _slot_index(self, seg, char):
        return self._slot_order_index.get((seg, char), -1)

    # ---------------------------------------------------------
    # Active slot
    # ---------------------------------------------------------

    def _set_active(self, seg, char, defer=False):
        idx = self._slot_order_index.get((seg, char))

        if idx is None:
            return

        if self.sequential:
            first_empty = self._first_empty_slot()

            if first_empty:
                first_empty_idx = self._slot_order_index.get(first_empty, -1)

                # block moving past first empty slot
                if idx > first_empty_idx:
                    return

        def apply():
            if not self.focus:
                return

            self._active_segment = seg
            self._active_char = char

            self._highlight()

            if self.slot_visuals:
                self._update_slot_style()

        if self._active_ev:
            self._active_ev.cancel()

        self._active_ev = Clock.schedule_once(lambda *_: apply(), 0)

    # ---------------------------------------------------------
    # Editing
    # ---------------------------------------------------------
    def insert_text(self, substring, from_undo=False):
        seg = self._active_segment
        char = self._active_char

        dummy = [s.copy() for s in self.segments]

        for ch in substring:
            if not self.validate_char(ch):
                continue

            dummy[seg][char] = ch

            nxt = self._slot_move(seg, char, 1)

            if not nxt:
                if self.unfocus_on_fill:
                    self.focus = False
                break

            seg, char = nxt

        for i, s in enumerate(dummy):
            if not self.validate_segment(i, s):
                return

        if not self.validate_partial(dummy):
            return

        self.segments = dummy

        self._set_active(seg, char)
        self._render()
        self._highlight()

    # ---------------------------------------------------------
    # Backspace
    # ---------------------------------------------------------

    def do_backspace(self, from_undo=False, mode="bkspc"):
        seg = self._active_segment
        char = self._active_char

        if self.segments[seg][char] is not None:
            self.segments[seg][char] = None
        else:
            prev = self._slot_move(seg, char, -1)
            if not prev:
                return
            seg, char = prev
            self.segments[seg][char] = None

        self._set_active(seg, char)
        self._render()
        self._highlight()

    # ---------------------------------------------------------
    # Keyboard
    # ---------------------------------------------------------
    def keyboard_on_key_down(self, window, keycode, text, modifiers):
        if not self.focus:
            return super().keyboard_on_key_down(window, keycode, text, modifiers)  # pyright: ignore

        key = keycode[0]

        # ---------------------------------------------------------
        # Backspace
        # ---------------------------------------------------------
        if key == 8:
            self.do_backspace()
            return True

        # ---------------------------------------------------------
        # Tab / Shift+Tab navigation
        # ---------------------------------------------------------
        if key == 9:
            direction = -1 if "shift" in modifiers else 1
            nxt = self._slot_move(self._active_segment, self._active_char, direction)
            if nxt:
                self._set_active(*nxt)
            return True

        # ---------------------------------------------------------
        # Space → move forward
        # ---------------------------------------------------------
        if key == 32:
            nxt = self._slot_move(self._active_segment, self._active_char, 1)
            if nxt:
                self._set_active(*nxt)
            return True

        # ---------------------------------------------------------
        # Arrow Left
        # ---------------------------------------------------------
        if key == 276:
            prev = self._slot_move(self._active_segment, self._active_char, -1)
            if prev:
                self._set_active(*prev)
            return True

        # ---------------------------------------------------------
        # Arrow Right
        # ---------------------------------------------------------
        if key == 275:
            nxt = self._slot_move(self._active_segment, self._active_char, 1)
            if nxt:
                self._set_active(*nxt)
            return True

        return super().keyboard_on_key_down(window, keycode, text, modifiers)  # pyright: ignore

    def keyboard_on_textinput(self, window, text):
        if not self.focus:
            return super().keyboard_on_textinput(window, text)

        # consume navigation characters
        if text == " " or text == "\t":
            return True

        self.insert_text(text)
        return True

    # ---------------------------------------------------------
    # Mouse
    # ---------------------------------------------------------
    def _on_textinput_focused(self, instance, value, *largs):  # pyright: ignore
        super()._on_textinput_focused(instance, value, *largs)

        if value:
            self._render()

            if self.sequential:
                slot = self._first_empty_slot()
                if slot:
                    self._set_active(*slot, defer=True)

        else:
            self._unfocus_slots()
            if callable(self.formater):
                self.text = self.formater(self)

    def on_touch_up(self, touch):
        handled = super().on_touch_up(touch)  # pyright: ignore

        if self.collide_point(*touch.pos) and self.focus:  # pyright: ignore
            if self.sequential:
                slot = self._first_empty_slot()
                if slot:
                    self._set_active(*slot)
                return True

            # normal non-sequential behavior
            col, _ = self.get_cursor_from_xy(*touch.pos)  # pyright: ignore

            best = min(
                self._editable_positions.items(),
                key=lambda x: abs(col - x[1]),
            )[0]

            self._set_active(*best)

            return True

        return handled

    # ---------------------------------------------------------
    # Rebuild
    # ---------------------------------------------------------

    def _rebuild_all(self):
        if not self.lengths:
            return

        if not self.segments or len(self.segments) != len(self.lengths):
            self.segments = [[None] * length for length in self.lengths]
        else:
            self._normalize_segments()

        self._rebuild_slot_order()

        if self._slot_order:
            self._active_segment, self._active_char = self._slot_order[0]

        self._render()

        if self.focus:
            self._schedule_highlight()

    # ---------------------------------------------------------
    # Property updates
    # ---------------------------------------------------------
    def on_lengths(self, *_):
        self._rebuild_all()

    def on_separator(self, *_):
        self._rebuild_all()

    def on_spacing(self, *_):
        self._rebuild_all()

    def on_placeholder(self, *_):
        self._rebuild_all()

    def on_size(self, *args):
        self._schedule_slots_update()

    def on_pos(self, *args):
        self._schedule_slots_update()

    def on_text(self, *args):
        self._schedule_slots_update()

    def on_slot_background_color(self, *_):
        self._update_slot_style()

    def on_slot_border_color(self, *_):
        self._update_slot_style()

    def on_slot_background_focused_color(self, *_):
        self._update_slot_style()

    def on_slot_border_focused_color(self, *_):
        self._update_slot_style()
