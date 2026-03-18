from __future__ import annotations

from kivy.clock import Clock
from kivy.properties import StringProperty

from .field import FnFieldBaseBehavior


class FnMaskFieldBehavior(FnFieldBaseBehavior):
    pattern = StringProperty("(###) #### ####")
    pattern_char = StringProperty("#")

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._raw_value = ""
        self._updating_mask_text = False
        self.multiline = False

    # ---------------------------------------------------------
    # Validation / Transform Hooks
    # ---------------------------------------------------------
    def transform_char(self, char: str) -> str | None:
        """
        Transform a character before validation.

        Return:
        - transformed character
        - None to discard it
        """
        return char

    # ---------------------------------------------------------
    # Helpers
    # ---------------------------------------------------------
    def _slot_count(self) -> int:
        return self.pattern.count(self.pattern_char)

    def _mask_literals(self) -> set[str]:
        return {ch for ch in self.pattern if ch != self.pattern_char}

    def _extract_raw(self, text: str) -> str:
        if isinstance(text, bytes):
            text = text.decode("utf8")

        literals = self._mask_literals()
        return "".join(ch for ch in text if ch not in literals and ch not in "\r\n")

    def _apply_pattern(self, raw: str) -> str:
        result = []
        raw_index = 0

        for ch in self.pattern:
            if raw_index >= len(raw):
                break

            if ch == self.pattern_char:
                result.append(raw[raw_index])
                raw_index += 1
            else:
                result.append(ch)

        return "".join(result)

    def _display_to_raw_index(self, display_index: int) -> int:
        raw_index = 0

        for i, ch in enumerate(self.pattern):
            if i >= display_index:
                break
            if ch == self.pattern_char:
                raw_index += 1

        return min(raw_index, len(self._raw_value))

    def _raw_to_display_index(self, raw_index: int) -> int:
        if raw_index <= 0:
            return 0

        slots_seen = 0
        for i, ch in enumerate(self.pattern):
            if ch == self.pattern_char:
                slots_seen += 1
                if slots_seen == raw_index:
                    return i + 1

        return len(self.text)

    def _get_selection_display_range(self) -> tuple[int, int]:
        a = getattr(self, "_selection_from", None)
        b = getattr(self, "_selection_to", None)

        if a is not None and b is not None and a != b:
            return min(a, b), max(a, b)

        i = self.cursor_index()  # pyright: ignore
        return i, i

    def _set_mask_text(self, raw: str, raw_cursor: int) -> None:
        self._raw_value = raw[: self._slot_count()]
        formatted = self._apply_pattern(self._raw_value)

        self._updating_mask_text = True
        self.text = formatted
        self._updating_mask_text = False

        display_index = self._raw_to_display_index(
            min(raw_cursor, len(self._raw_value))
        )

        def _set_cursor(_dt):
            self.cursor = self.get_cursor_from_index(display_index)  # pyright: ignore

        Clock.schedule_once(_set_cursor, 0)

    def _sync_raw_from_text(self) -> None:
        self._raw_value = self._extract_raw(self.text)[: self._slot_count()]

    def _filter_input_chars(self, text: str) -> str:
        result = []

        for ch in text:
            ch = self.transform_char(ch)

            if ch is None or ch == "":
                continue

            if not self.validate_char(ch):
                continue

            result.append(ch)

        return "".join(result)

    # ---------------------------------------------------------
    # Keep raw synced if text changes externally
    # ---------------------------------------------------------
    def on_text(self, instance, value):
        if not self._updating_mask_text:
            self._sync_raw_from_text()

        if hasattr(super(), "on_text"):
            return super().on_text(instance, value)  # pyright: ignore

    # ---------------------------------------------------------
    # Insert
    # ---------------------------------------------------------
    def insert_text(self, substring, from_undo=False):
        if self.readonly or not substring:  # pyright: ignore
            return

        raw_insert = self._extract_raw(substring)
        raw_insert = self._filter_input_chars(raw_insert)

        if not raw_insert:
            return

        start_display, end_display = self._get_selection_display_range()
        start_raw = self._display_to_raw_index(start_display)
        end_raw = self._display_to_raw_index(end_display)

        before = self._raw_value
        after = self._raw_value[:start_raw] + raw_insert + self._raw_value[end_raw:]
        after = after[: self._slot_count()]

        if not self.validate_edit(before, after, chars=raw_insert):
            return

        self.cancel_selection()  # pyright: ignore
        self._set_mask_text(after, start_raw + len(raw_insert))

    # ---------------------------------------------------------
    # Backspace
    # ---------------------------------------------------------
    def do_backspace(self, from_undo=False, mode="bkspc"):
        if self.readonly:  # pyright: ignore
            return

        start_display, end_display = self._get_selection_display_range()
        start_raw = self._display_to_raw_index(start_display)
        end_raw = self._display_to_raw_index(end_display)

        before = self._raw_value

        # selection delete
        if start_display != end_display:
            after = self._raw_value[:start_raw] + self._raw_value[end_raw:]

            if not self.validate_edit(before, after, chars=None):
                return

            self.cancel_selection()  # pyright: ignore
            self._set_mask_text(after, start_raw)
            return

        # normal backspace
        if start_raw <= 0:
            return

        after = self._raw_value[: start_raw - 1] + self._raw_value[start_raw:]

        if not self.validate_edit(before, after, chars=None):
            return

        self._set_mask_text(after, start_raw - 1)

    # ---------------------------------------------------------
    # Delete selection / Ctrl+X path
    # ---------------------------------------------------------
    def delete_selection(self, from_undo=False):
        start_display, end_display = self._get_selection_display_range()
        if start_display == end_display:
            return

        start_raw = self._display_to_raw_index(start_display)
        end_raw = self._display_to_raw_index(end_display)

        before = self._raw_value
        after = self._raw_value[:start_raw] + self._raw_value[end_raw:]

        if not self.validate_edit(before, after, chars=None):
            return

        self.cancel_selection()  # pyright: ignore
        self._set_mask_text(after, start_raw)

    def cut(self):
        if getattr(self, "selection_text", ""):
            self.copy()  # pyright: ignore
            self.delete_selection()

    # ---------------------------------------------------------
    # Delete key
    # ---------------------------------------------------------
    def do_delete(self):
        if self.readonly:  # pyright: ignore
            return

        start_display, end_display = self._get_selection_display_range()
        start_raw = self._display_to_raw_index(start_display)
        end_raw = self._display_to_raw_index(end_display)

        before = self._raw_value

        if start_display != end_display:
            after = self._raw_value[:start_raw] + self._raw_value[end_raw:]

            if not self.validate_edit(before, after, chars=None):
                return

            self.cancel_selection()  # pyright: ignore
            self._set_mask_text(after, start_raw)
            return

        if start_raw >= len(self._raw_value):
            return

        after = self._raw_value[:start_raw] + self._raw_value[start_raw + 1 :]

        if not self.validate_edit(before, after, chars=None):
            return

        self._set_mask_text(after, start_raw)

    def keyboard_on_key_down(self, window, keycode, text, modifiers):
        if keycode[0] == 127:
            self.do_delete()
            return True

        return super().keyboard_on_key_down(window, keycode, text, modifiers)  # pyright: ignore
