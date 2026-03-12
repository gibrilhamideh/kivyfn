from __future__ import annotations

from typing import Optional

from kivy.clock import Clock
from kivy.properties import (
    BooleanProperty,
    ListProperty,
    OptionProperty,
    StringProperty,
)
from kivy.uix.textinput import TextInput


class FnSegmentedFieldBehavior:
    """
    Segmented field behavior with one-character highlight editing.

    Use this BEFORE TextInput in inheritance order:

        class TimeField(FnSegmentedFieldBehavior, TextInput):
            pass
    """

    lengths = ListProperty([])
    separator = StringProperty(":")
    spacing = StringProperty("")
    placeholder = StringProperty("_")

    # Order of segments when auto-advancing:
    # "left"  -> segment 0, 1, 2, ...
    # "right" -> last, ..., 2, 1, 0
    segment_direction = OptionProperty("left", options=["left", "right"])

    # Order of chars INSIDE each segment when auto-advancing:
    # "left"  -> index 0, 1, 2, ...
    # "right" -> last, ..., 2, 1, 0
    segment_fill_direction = OptionProperty("left", options=["left", "right"])

    unfocus_on_fill = BooleanProperty(False)

    # Internal editable slots, e.g. [["1", "2"], ["3", "_"], ["_", "_"]]
    segments = ListProperty([])

    _active_segment = 0
    _active_char = 0
    _highlight_ev = None

    # Maps (segment_index, char_index) -> absolute text position in self.text
    _editable_positions: dict[tuple[int, int], int] = {}

    # Logical write order of slots
    _slot_order: list[tuple[int, int]] = []
    _slot_order_index: dict[tuple[int, int], int] = {}

    # ---------------------------------------------------------
    # Initialization
    # ---------------------------------------------------------

    def on_kv_post(self, base_widget):
        super_on_kv_post = getattr(super(), "on_kv_post", None)
        if callable(super_on_kv_post):
            super_on_kv_post(base_widget)

        self.multiline = False
        self.cursor_width = 0
        self.cursor_blink = False

        if not self.lengths:
            return

        if not self.segments:
            self.segments = [[self.placeholder] * length for length in self.lengths]
        else:
            self._normalize_segments()

        self._rebuild_slot_order()

        if self._slot_order:
            self._active_segment, self._active_char = self._slot_order[0]

        self._render()

        if self.focus:
            self._schedule_highlight()

    # ---------------------------------------------------------
    # Internal shape helpers
    # ---------------------------------------------------------

    def _normalize_segments(self) -> None:
        normalized: list[list[str]] = []

        for i, length in enumerate(self.lengths):
            value = self.segments[i] if i < len(self.segments) else None
            chars = [self.placeholder] * length

            if value is None:
                normalized.append(chars)
                continue

            if isinstance(value, list):
                raw = [str(ch)[:1] for ch in value]
            else:
                raw = [ch for ch in str(value)]

            for j, ch in enumerate(raw[:length]):
                chars[j] = ch

            normalized.append(chars)

        self.segments = normalized

    def _segment_indices_in_order(self) -> list[int]:
        if self.segment_direction == "left":
            return list(range(len(self.lengths)))
        return list(range(len(self.lengths) - 1, -1, -1))

    def _char_indices_in_segment(self, seg_index: int) -> list[int]:
        length = self.lengths[seg_index]
        if self.segment_fill_direction == "left":
            return list(range(length))
        return list(range(length - 1, -1, -1))

    def _rebuild_slot_order(self) -> None:
        slot_order: list[tuple[int, int]] = []

        for seg_index in self._segment_indices_in_order():
            for char_index in self._char_indices_in_segment(seg_index):
                slot_order.append((seg_index, char_index))

        self._slot_order = slot_order
        self._slot_order_index = {slot: i for i, slot in enumerate(slot_order)}

    # ---------------------------------------------------------
    # Display helpers
    # ---------------------------------------------------------

    def _build_tokens(self) -> list[tuple[str, Optional[tuple[int, int]]]]:
        """
        Returns a flat list of visible tokens.

        Each item is:
            (token_text, editable_ref)

        editable_ref is:
            (segment_index, char_index) for editable chars
            None for separators
        """
        tokens: list[tuple[str, Optional[tuple[int, int]]]] = []

        for seg_index, seg in enumerate(self.segments):
            for char_index, ch in enumerate(seg):
                tokens.append((ch, (seg_index, char_index)))

            if seg_index < len(self.segments) - 1:
                tokens.append((self.separator, None))

        return tokens

    def _render(self) -> None:
        tokens = self._build_tokens()

        self._editable_positions = {}
        rendered_parts: list[str] = []
        pos = 0

        for i, (token_text, editable_ref) in enumerate(tokens):
            rendered_parts.append(token_text)

            if editable_ref is not None:
                self._editable_positions[editable_ref] = pos

            pos += len(token_text)

            if i < len(tokens) - 1:
                rendered_parts.append(self.spacing)
                pos += len(self.spacing)

        self.text = "".join(rendered_parts)

    # ---------------------------------------------------------
    # Highlight helpers
    # ---------------------------------------------------------

    def _schedule_highlight(self) -> None:
        if self._highlight_ev is not None:
            self._highlight_ev.cancel()
        self._highlight_ev = Clock.schedule_once(self._do_scheduled_highlight, 0)

    def _do_scheduled_highlight(self, _dt) -> None:
        self._highlight_ev = None
        self._highlight_current()

    def _highlight_current(self) -> None:
        if not self.focus:
            self.cancel_selection()
            return

        pos = self._editable_positions.get((self._active_segment, self._active_char))
        if pos is None:
            self.cancel_selection()
            return

        self.cursor = (pos, 0)
        self.select_text(pos, pos + 1)

    # ---------------------------------------------------------
    # Active slot helpers
    # ---------------------------------------------------------

    def _set_active(self, seg: int, char: int, defer_highlight: bool = False) -> None:
        seg = max(0, min(seg, len(self.lengths) - 1))
        char = max(0, min(char, self.lengths[seg] - 1))

        self._active_segment = seg
        self._active_char = char

        if defer_highlight:
            self._schedule_highlight()
        else:
            self._highlight_current()

    def _logical_previous_slot(self, seg: int, char: int) -> Optional[tuple[int, int]]:
        idx = self._slot_order_index.get((seg, char))
        if idx is None or idx <= 0:
            return None
        return self._slot_order[idx - 1]

    def _logical_next_slot(self, seg: int, char: int) -> Optional[tuple[int, int]]:
        idx = self._slot_order_index.get((seg, char))
        if idx is None or idx >= len(self._slot_order) - 1:
            return None
        return self._slot_order[idx + 1]

    def _visual_previous_slot(self, seg: int, char: int) -> Optional[tuple[int, int]]:
        if char > 0:
            return seg, char - 1

        if seg > 0:
            prev_seg = seg - 1
            return prev_seg, self.lengths[prev_seg] - 1

        return None

    def _visual_next_slot(self, seg: int, char: int) -> Optional[tuple[int, int]]:
        if char + 1 < self.lengths[seg]:
            return seg, char + 1

        if seg + 1 < len(self.lengths):
            return seg + 1, 0

        return None

    def _next_segment_start_slot(self, seg: int) -> Optional[tuple[int, int]]:
        if self.segment_direction == "left":
            next_seg = seg + 1
            if next_seg >= len(self.lengths):
                return None
        else:
            next_seg = seg - 1
            if next_seg < 0:
                return None

        if self.segment_fill_direction == "left":
            return next_seg, 0
        return next_seg, self.lengths[next_seg] - 1

    def _snap_to_closest_editable(self, col: int) -> tuple[int, int]:
        best_distance: Optional[int] = None
        best_seg = 0
        best_char = 0

        for (seg, char), pos in self._editable_positions.items():
            distance = abs(col - pos)

            if best_distance is None or distance < best_distance:
                best_distance = distance
                best_seg = seg
                best_char = char

        return best_seg, best_char

    # ---------------------------------------------------------
    # Focus handling
    # ---------------------------------------------------------

    def _on_textinput_focused(self, instance, value, *largs):
        """
        Override TextInput's internal focus handler so our highlight wins
        after TextInput finishes its own cleanup.
        """
        super()._on_textinput_focused(instance, value, *largs)

        self._render()

        if value:
            self._schedule_highlight()
        else:
            if self._highlight_ev is not None:
                self._highlight_ev.cancel()
                self._highlight_ev = None
            self.cancel_selection()

    # ---------------------------------------------------------
    # Mouse handling
    # ---------------------------------------------------------

    def on_touch_down(self, touch):
        return super().on_touch_down(touch)

    def on_touch_up(self, touch):
        handled = super().on_touch_up(touch)

        if self.collide_point(*touch.pos) and self.focus:
            col, _row = self.get_cursor_from_xy(*touch.pos)
            seg, char = self._snap_to_closest_editable(col)
            self._set_active(seg, char, defer_highlight=True)
            return True

        return handled

    # ---------------------------------------------------------
    # Validation hook
    # ---------------------------------------------------------

    def validate_segment(self, index: int, chars: list[str]) -> bool:
        """
        Override in subclasses if needed.

        chars is the full segment after the proposed edit.
        """
        return True

    # ---------------------------------------------------------
    # Editing
    # ---------------------------------------------------------

    def insert_text(self, substring, from_undo=False):
        if not substring:
            return

        seg = self._active_segment
        char = self._active_char

        for new_char in substring:
            candidate = [*self.segments[seg]]
            candidate[char] = new_char

            if not self.validate_segment(seg, candidate):
                continue

            self.segments[seg][char] = new_char

            nxt = self._logical_next_slot(seg, char)
            if nxt is not None:
                seg, char = nxt
            else:
                if self.unfocus_on_fill:
                    self.focus = False

        self._active_segment = seg
        self._active_char = char

        self._render()

        if self.focus:
            self._highlight_current()

    def do_backspace(self, from_undo=False, mode="bkspc"):
        seg = self._active_segment
        char = self._active_char

        # If current slot has a real char -> clear THIS slot and stay on it.
        # If current slot is already placeholder -> move back in LOGICAL fill order,
        # clear that slot, stay there.
        if self.segments[seg][char] != self.placeholder:
            self.segments[seg][char] = self.placeholder
        else:
            prev = self._logical_previous_slot(seg, char)
            if prev is None:
                return

            seg, char = prev
            self.segments[seg][char] = self.placeholder

        self._active_segment = seg
        self._active_char = char

        self._render()
        self._highlight_current()

    # ---------------------------------------------------------
    # Keyboard interception
    # ---------------------------------------------------------

    def keyboard_on_key_down(self, window, keycode, text, modifiers):
        if not self.focus:
            return super().keyboard_on_key_down(window, keycode, text, modifiers)

        key = keycode[0]
        mods = set(modifiers) - {"capslock", "numlock"}

        if mods:
            return super().keyboard_on_key_down(window, keycode, text, modifiers)

        # backspace
        if key == 8:
            self.do_backspace()
            return True

        # left arrow = visual movement
        if key == 276:
            prev = self._visual_previous_slot(self._active_segment, self._active_char)
            if prev is not None:
                self._set_active(*prev)
            return True

        # right arrow = visual movement
        if key == 275:
            nxt = self._visual_next_slot(self._active_segment, self._active_char)
            if nxt is not None:
                self._set_active(*nxt)
            return True

        # tab -> jump to next segment start in segment_direction
        if key == 9:
            nxt = self._next_segment_start_slot(self._active_segment)
            if nxt is not None:
                self._set_active(*nxt)
            return True

        return super().keyboard_on_key_down(window, keycode, text, modifiers)

    def keyboard_on_textinput(self, window, text):
        if self.focus and text:
            self.insert_text(text)
            return

        return super().keyboard_on_textinput(window, text)

    # ---------------------------------------------------------
    # Recompute when structure changes
    # ---------------------------------------------------------

    def _rebuild_all(self) -> None:
        if not self.lengths:
            self._editable_positions = {}
            self._slot_order = []
            self._slot_order_index = {}
            return

        if not self.segments or len(self.segments) != len(self.lengths):
            self.segments = [[self.placeholder] * length for length in self.lengths]
        else:
            self._normalize_segments()

        self._rebuild_slot_order()

        if self._slot_order:
            current = (self._active_segment, self._active_char)
            if current not in self._slot_order_index:
                self._active_segment, self._active_char = self._slot_order[0]
            else:
                self._active_segment = min(self._active_segment, len(self.lengths) - 1)
                self._active_char = min(
                    self._active_char,
                    self.lengths[self._active_segment] - 1,
                )

        self._render()

        if self.focus:
            self._schedule_highlight()

    def on_lengths(self, *_args):
        self._rebuild_all()

    def on_separator(self, *_args):
        self._rebuild_all()

    def on_spacing(self, *_args):
        self._rebuild_all()

    def on_placeholder(self, *_args):
        self._rebuild_all()

    def on_segment_direction(self, *_args):
        self._rebuild_all()

    def on_segment_fill_direction(self, *_args):
        self._rebuild_all()

    # ---------------------------------------------------------
    # Public helper
    # ---------------------------------------------------------

    def get_value(self):
        """
        Returns tuple[str | None, ...]
        """
        result = []

        for seg in self.segments:
            raw = "".join(ch for ch in seg if ch != self.placeholder)
            result.append(raw if raw else None)

        return tuple(result)
