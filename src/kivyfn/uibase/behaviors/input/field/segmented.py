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
)
from kivy.graphics import Color
from kivy.graphics.vertex_instructions import SmoothRoundedRectangle
from kivy.graphics.vertex_instructions import SmoothLine

from .field import FnFieldBaseBehavior
# editable_segments
# sequential
# focus_first_empty
# format_partial
# unfocus_on_fill


# _format, edtibale_segemnts, sequential segments
class FnSegmentedFieldBehavior(FnFieldBaseBehavior):
    lengths = ListProperty([])
    separator = StringProperty(":")
    spacing = StringProperty("")
    placeholder = StringProperty("_")

    segment_direction = OptionProperty("left", options=["left", "right"])
    segment_fill_direction = OptionProperty("left", options=["left", "right"])

    unfocus_on_fill = BooleanProperty(False)

    segments = ListProperty([])

    slot_visuals = BooleanProperty(True)
    slot_background_color = ColorProperty((1, 0, 0, 0.2))
    slot_border_color = ColorProperty((0, 0, 0, 0))
    slot_background_focused_color = ColorProperty((0, 0, 0, 0))
    slot_border_focused_color = ColorProperty((0, 1, 0, 0.2))
    slot_border_width = NumericProperty(1)
    slot_radius = VariableListProperty([0], length=4)
    slot_padding = NumericProperty(5)

    _slot_graphics = DictProperty({})

    _active_segment = 0
    _active_char = 0

    _editable_positions = {}
    _slot_order = []
    _slot_order_index = {}

    _highlight_ev = None

    # ---------------------------------------------------------
    # Initialization
    # ---------------------------------------------------------

    def on_kv_post(self, base_widget):
        super().on_kv_post(base_widget)

        self.multiline = False
        self.cursor_width = 0
        self.cursor_blink = False

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
            for ch in self._char_indices(seg):
                order.append((seg, ch))

        self._slot_order = order
        self._slot_order_index = {slot: i for i, slot in enumerate(order)}

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

    def _format(self):
        pass

    # ---------------------------------------------------------
    # Highlight
    # ---------------------------------------------------------

    def _highlight(self):
        if not self.focus:
            self.cancel_selection()
            return

        pos = self._editable_positions.get((self._active_segment, self._active_char))

        if pos is None:
            self.cancel_selection()
            return

        self.cursor = (pos, 0)
        self.select_text(pos, pos + 1)

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
        with self.canvas.after:
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
            col, row = self.get_cursor_from_index(index)

            # temporarily move cursor to compute pixel position
            old_cursor = self.cursor
            self.cursor = (col, row)
            x, y = self.cursor_pos
            y -= self.line_height
            self.cursor = old_cursor

            # slot size based on glyph metrics
            glyph_width = self._get_text_width("0", self.tab_width, self._label_cached)

            slot_width = glyph_width + (self.slot_padding * 2)
            slot_height = self.line_height + (self.slot_padding * 2)

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

    # ---------------------------------------------------------
    # Active slot
    # ---------------------------------------------------------

    def _set_active(self, seg, char, defer=False):
        seg = max(0, min(seg, len(self.lengths) - 1))
        char = max(0, min(char, self.lengths[seg] - 1))

        self._active_segment = seg
        self._active_char = char

        if defer:
            self._schedule_highlight()
        else:
            self._highlight()

        if self.slot_visuals:
            self._update_slot_style()

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
            return super().keyboard_on_key_down(window, keycode, text, modifiers)

        key = keycode[0]

        if key == 8:
            self.do_backspace()
            return True

        if key == 276:
            prev = self._visual_prev(self._active_segment, self._active_char)
            if prev:
                self._set_active(*prev)
            return True

        if key == 275:
            nxt = self._visual_next(self._active_segment, self._active_char)
            if nxt:
                self._set_active(*nxt)
            return True

        return super().keyboard_on_key_down(window, keycode, text, modifiers)

    def keyboard_on_textinput(self, window, text):
        if self.focus:
            self.insert_text(text)
            return True

        super().keyboard_on_textinput(window, text)

    # ---------------------------------------------------------
    # Mouse
    # ---------------------------------------------------------
    def _on_textinput_focused(self, instance, value, *largs):
        super()._on_textinput_focused(instance, value, *largs)

        if value:
            self._render()
        else:
            self._unfocus_slots()
            self._format()

    def on_touch_up(self, touch):
        handled = super().on_touch_up(touch)

        if self.collide_point(*touch.pos) and self.focus:
            col, _ = self.get_cursor_from_xy(*touch.pos)

            best = min(
                self._editable_positions.items(),
                key=lambda x: abs(col - x[1]),
            )[0]

            self._set_active(*best, defer=True)

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
