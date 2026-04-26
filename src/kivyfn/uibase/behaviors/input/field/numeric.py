from __future__ import annotations

from typing import Any

from kivy.properties import ObjectProperty, OptionProperty

from .field import FnFieldBaseBehavior


class FnNumericInputBehavior(FnFieldBaseBehavior):
    """
    Simple numeric input behavior.

    Supports:
    - int / float
    - min_value / max_value

    Notes
    -----
    - Developers should use `value`, not `text`.
    - While editing, temporary states like "-", ".", "-." are allowed
      so typing feels natural.
    - Final validation happens on blur/commit.
    """

    number_type = OptionProperty("float", options=["int", "float"])

    min_value = ObjectProperty(None, allownone=True)
    max_value = ObjectProperty(None, allownone=True)

    # ---------------------------------------------------------
    # Value API
    # ---------------------------------------------------------
    def _get_value(self) -> int | float | None:
        return self._parse_text(self.text)

    def _set_value(self, value, from_cache=False):
        text = self._format_value(value)
        self.text = text

        if not from_cache:
            self._cached_value = self._coerce_value(value)

    # ---------------------------------------------------------
    # Parsing / formatting
    # ---------------------------------------------------------
    def _coerce_value(self, value: Any) -> int | float | None:
        if value is None:
            return None

        try:
            if self.number_type == "int":
                return int(value)

            return float(value)

        except (TypeError, ValueError):
            return None

    def _parse_text(self, text: str) -> int | float | None:
        text = text.strip()

        if text == "":
            return None

        # valid during typing, but not final values
        if text in {"-", ".", "-."}:
            return None

        try:
            if self.number_type == "int":
                if "." in text:
                    return None
                return int(text)

            return float(text)

        except (TypeError, ValueError):
            return None

    def _format_value(self, value: int | float | None) -> str:
        if value is None:
            return ""

        if self.number_type == "int":
            text = str(int(value))
        else:
            text = str(float(value))

        if callable(self.formater):
            formatted = self.formater(text, value)
            if isinstance(formatted, str):
                return formatted

        return text

    # ---------------------------------------------------------
    # Text validation helpers
    # ---------------------------------------------------------
    def _allows_negative(self) -> bool:
        return self.min_value is None or self.min_value < 0

    def _is_intermediate_text(self, text: str) -> bool:
        if text == "":
            return True

        if text == "-":
            return self._allows_negative()

        if self.number_type == "float":
            if text == ".":
                return True
            if text == "-.":
                return self._allows_negative()

        return False

    def _is_text_allowed(self, text: str) -> bool:
        text = text.strip()

        if self._is_intermediate_text(text):
            return True

        if text.count("-") > 1:
            return False

        if "-" in text:
            if not self._allows_negative():
                return False
            if not text.startswith("-"):
                return False

        if self.number_type == "int":
            for ch in text:
                if ch not in "0123456789-":
                    return False
            return True

        if text.count(".") > 1:
            return False

        for ch in text:
            if ch not in "0123456789-.":
                return False

        return True

    def _value_in_range(self, value: int | float | None) -> bool:
        if value is None:
            return False

        if self.min_value is not None and value < self.min_value:
            return False

        if self.max_value is not None and value > self.max_value:
            return False

        return True

    def _get_proposed_text_after_insert(self, substring: str) -> str:
        text = self.text

        if self.selection_text:
            start = min(self.selection_from, self.selection_to)
            end = max(self.selection_from, self.selection_to)
            return text[:start] + substring + text[end:]

        col, _row = self.cursor
        return text[:col] + substring + text[col:]

    def _get_proposed_text_after_backspace(self) -> str | None:
        text = self.text

        if self.selection_text:
            start = min(self.selection_from, self.selection_to)
            end = max(self.selection_from, self.selection_to)
            return text[:start] + text[end:]

        col, _row = self.cursor

        if col <= 0:
            return None

        return text[: col - 1] + text[col:]

    # ---------------------------------------------------------
    # Validation hooks
    # ---------------------------------------------------------
    def validate_char(self, char: str) -> bool:
        if self.number_type == "int":
            return char in "0123456789-"
        return char in "0123456789-."

    def validate_value(self, value: Any) -> bool:
        text = self.text.strip()

        if text == "":
            return self.default is None

        if self._is_intermediate_text(text):
            return False

        if value is None:
            return False

        return self._value_in_range(value)

    # ---------------------------------------------------------
    # Editing
    # ---------------------------------------------------------
    def insert_text(self, substring, from_undo=False):
        filtered = "".join(ch for ch in substring if self.validate_char(ch))

        if not filtered:
            return

        proposed = self._get_proposed_text_after_insert(filtered)

        if not self._is_text_allowed(proposed):
            return

        super().insert_text(filtered, from_undo=from_undo)  # pyright: ignore

    def do_backspace(self, from_undo=False, mode="bkspc"):
        proposed = self._get_proposed_text_after_backspace()

        if proposed is None:
            return

        if not self._is_text_allowed(proposed):
            return

        super().do_backspace(from_undo=from_undo, mode=mode)  # pyright: ignore

    # ---------------------------------------------------------
    # Focus / commit
    # ---------------------------------------------------------
    def _on_textinput_focused(self, instance, focused, *largs):
        super()._on_textinput_focused(instance, focused, *largs)  # pyright: ignore

        if focused:
            self._cached_value = self._parse_text(self.text)
            self.valid = True
            return

        value = self._parse_text(self.text)

        if not self.validate_value(value):
            if self.revert_on_invalid:
                self._set_value(self._cached_value, from_cache=True)
                self.valid = True
            else:
                self.valid = False
            return

        self.valid = True

        # normalize text even if the numeric value did not change
        self.text = self._format_value(value)

        if value != self._cached_value:
            self._cached_value = value
            self.dispatch("on_commit", value)  # pyright: ignore
