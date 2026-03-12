from __future__ import annotations

from typing import Optional

from kivy.clock import Clock
from kivy.properties import BooleanProperty, ListProperty, StringProperty
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

    pad = BooleanProperty(False)
    pad_char = StringProperty("0")

    # internal editable slots, e.g. [["1", "2"], ["3", "_"], ["_", "_"]]
    segments = ListProperty([])

    _active_segment = 0
    _active_char = 0
    _highlight_ev = None
    _suppress_next_textinput: Optional[str] = None

    # Maps (segment_index, char_index) -> absolute text position in self.text
    _editable_positions: dict[tuple[int, int], int] = {}

    # ---------------------------------------------------------
    # Initialization
    # ---------------------------------------------------------

    def on_kv_post(self, base_widget):
        super_on_kv_post = getattr(super(), "on_kv_post", None)
        if callable(super_on_kv_post):
            super_on_kv_post(base_widget)

        # Segmented fields should behave like single-line structured inputs.
        self.multiline = False
        self.cursor_width = 0
        self.cursor_blink = False

        if not self.lengths:
            return

        if not self.segments:
            self.segments = [[self.placeholder] * length for length in self.lengths]
        else:
            self._normalize_segments()

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

    # ---------------------------------------------------------
    # Token / rendering helpers
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

        # Keep TextInput's logical cursor aligned, but invisible.
        self.cursor = (pos, 0)

        # One-character visual highlight.
        self.select_text(pos, pos + 1)

    # ---------------------------------------------------------
    # Navigation helpers
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

    def _previous_slot(self, seg: int, char: int) -> Optional[tuple[int, int]]:
        if char > 0:
            return seg, char - 1

        if seg > 0:
            prev_seg = seg - 1
            return prev_seg, self.lengths[prev_seg] - 1

        return None

    def _next_slot(self, seg: int, char: int) -> Optional[tuple[int, int]]:
        if char + 1 < self.lengths[seg]:
            return seg, char + 1

        if seg + 1 < len(self.lengths):
            return seg + 1, 0

        return None

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
        after TextInput finishes its own selection cleanup.
        """
        super()._on_textinput_focused(instance, value, *largs)

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

            nxt = self._next_slot(seg, char)
            if nxt is not None:
                seg, char = nxt

        self._active_segment = seg
        self._active_char = char

        self._render()
        self._highlight_current()

    def do_backspace(self, from_undo=False, mode="bkspc"):
        seg = self._active_segment
        char = self._active_char

        # Rule:
        # - if current slot has a real char -> clear THIS slot and stay on it
        # - if current slot is already placeholder -> move left, clear that slot, stay there

        if self.segments[seg][char] != self.placeholder:
            self.segments[seg][char] = self.placeholder
        else:
            prev = self._previous_slot(seg, char)
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

        # let ctrl/cmd shortcuts still go through
        if mods:
            return super().keyboard_on_key_down(window, keycode, text, modifiers)

        # backspace
        if key == 8:
            self.do_backspace()
            return True

        # left
        if key == 276:
            prev = self._previous_slot(self._active_segment, self._active_char)
            if prev is not None:
                self._set_active(*prev)
            return True

        # right
        if key == 275:
            nxt = self._next_slot(self._active_segment, self._active_char)
            if nxt is not None:
                self._set_active(*nxt)
            return True

        # tab -> jump to next segment start
        if key == 9:
            if self._active_segment + 1 < len(self.lengths):
                self._set_active(self._active_segment + 1, 0)
            return True

        return super().keyboard_on_key_down(window, keycode, text, modifiers)

    def keyboard_on_textinput(self, window, text):
        if self._suppress_next_textinput == text:
            self._suppress_next_textinput = None
            return

        if self.focus and text:
            self.insert_text(text)
            return

        return super().keyboard_on_textinput(window, text)

    # ---------------------------------------------------------
    # Recompute when structure changes
    # ---------------------------------------------------------

    def on_lengths(self, *_args):
        if not self.lengths:
            self._editable_positions = {}
            return

        if not self.segments or len(self.segments) != len(self.lengths):
            self.segments = [[self.placeholder] * length for length in self.lengths]
        else:
            self._normalize_segments()

        self._active_segment = min(self._active_segment, len(self.lengths) - 1)
        self._active_char = min(
            self._active_char,
            self.lengths[self._active_segment] - 1,
        )

        self._render()

        if self.focus:
            self._schedule_highlight()

    def on_separator(self, *_args):
        if not self.lengths:
            return
        self._render()
        if self.focus:
            self._schedule_highlight()

    def on_spacing(self, *_args):
        if not self.lengths:
            return
        self._render()
        if self.focus:
            self._schedule_highlight()

    def on_placeholder(self, *_args):
        if not self.lengths:
            return

        for seg_index, seg in enumerate(self.segments):
            for char_index, ch in enumerate(seg):
                if len(ch) != 1:
                    self.segments[seg_index][char_index] = self.placeholder

        self._render()
        if self.focus:
            self._schedule_highlight()

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

