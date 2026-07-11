# kivyfn/ui/fields/numeric.py
from __future__ import annotations

from typing import Any

from kivy.properties import NumericProperty, OptionProperty

from kivyfn.ui.fields.base import FnBaseField
from kivyfn.ui.fields.event import InputEvent


class FnNumericField(FnBaseField):
    """
    Numeric input field.

    Rules
    -----
    text:
        Live editing text.

    value:
        Committed numeric value.

    Supports:
        - int / float
        - min_value / max_value
        - intermediate editing states like "-", ".", "-."
    """

    number_type = OptionProperty("float", options=["int", "float"])

    min_value = NumericProperty(None, allownone=True)
    max_value = NumericProperty(None, allownone=True)
    max_decimals = NumericProperty(None, allownone=True)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.multiline = False
        self.write_tab = False

    # ---------------------------------------------------------
    # Property Event
    # ---------------------------------------------------------
    def on_number_type(self, *_: Any) -> None:
        value = self._coerce_value(self.value)

        if value is None:
            return

        self.value = value

    # ---------------------------------------------------------
    # Value conversion
    # ---------------------------------------------------------
    def text_to_value(self) -> int | float | None:
        return self._parse_text(self.text)

    def value_to_text(self, value: Any) -> str:
        return self._format_value(value)

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

    def _format_value(self, value: Any) -> str:
        value = self._coerce_value(value)

        if value is None:
            return ""

        if self.number_type == "int":
            text = str(int(value))
        else:
            text = str(float(value))

        if callable(self.formatter):
            formatted = self.formatter(text, value)
            if isinstance(formatted, str):
                return formatted

        return text

    # ---------------------------------------------------------
    # Validation
    # ---------------------------------------------------------
    def validate_value(self, value: Any) -> bool:
        value = self._coerce_value(value)

        if value is None:
            return self.default is None

        return self._value_in_range(value)

    def validate_beforeinput(self, event: InputEvent) -> bool:
        after = event.after

        if not isinstance(after, str):
            return False

        # Block impossible numeric text.
        if not self._is_text_allowed(after):
            return False

        # Empty/intermediate text is allowed while editing.
        # Do not mark invalid here; final commit handles it.
        text = after.strip()
        if self._is_intermediate_text(text):
            self.invalid = False
            return True

        value = self._parse_text(text)

        # If it is syntactically allowed but not parseable,
        # let final validation handle it.
        if value is None:
            self.invalid = False
            return True

        # This is the only live invalid state we really need:
        # numeric value exists, but violates min/max.
        self.invalid = not self._value_in_range(value)

        return True

    # ---------------------------------------------------------
    # Numeric rules
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

    def _decimal_count(self, text: str) -> int:
        if "." not in text:
            return 0

        return len(text.split(".", 1)[1])

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
            return all(ch in "0123456789-" for ch in text)

        if text.count(".") > 1:
            return False

        if self.max_decimals is not None:
            if "." in text:
                decimals = text.split(".", 1)[1]

                if len(decimals) > self.max_decimals:
                    return False

        return all(ch in "0123456789-." for ch in text)

    def _value_in_range(self, value: int | float) -> bool:
        if self.min_value is not None and value < self.min_value:
            return False

        if self.max_value is not None and value > self.max_value:
            return False

        return True

    # ---------------------------------------------------------
    # Proposed text helpers
    # ---------------------------------------------------------
    def _get_proposed_text_after_insert(self, substring: str) -> str:
        text = self.text

        if self.selection_text:
            start = min(self.selection_from, self.selection_to)
            end = max(self.selection_from, self.selection_to)
            return text[:start] + substring + text[end:]

        col, _ = self.cursor
        return text[:col] + substring + text[col:]

    def _get_proposed_text_after_backspace(self) -> tuple[str, str] | None:
        text = self.text

        if self.selection_text:
            start = min(self.selection_from, self.selection_to)
            end = max(self.selection_from, self.selection_to)
            removed = text[start:end]
            return text[:start] + text[end:], removed

        col, _ = self.cursor

        if col <= 0:
            return None

        removed = text[col - 1]
        return text[: col - 1] + text[col:], removed

    # ---------------------------------------------------------
    # Editing
    # ---------------------------------------------------------
    def insert_text(self, substring: str, from_undo: bool = False) -> None:
        if self.readonly or not substring:  # pyright: ignore
            return

        filtered = "".join(
            ch for ch in substring if self._is_char_allowed(ch)
        )

        if not filtered:
            return

        before = self.text
        after = self._get_proposed_text_after_insert(filtered)

        event = InputEvent(
            field=self,
            kind="paste" if len(filtered) > 1 else "insert",
            before=before,
            after=after,
            text=filtered,
        )

        if not self.validate_beforeinput(event):
            return

        super().insert_text(filtered, from_undo=from_undo)

    def do_backspace(
        self,
        from_undo: bool = False,
        mode: str = "bkspc",
    ) -> None:
        if self.readonly:  # pyright: ignore
            return

        proposed = self._get_proposed_text_after_backspace()

        if proposed is None:
            return

        after, removed = proposed
        before = self.text

        event = InputEvent(
            field=self,
            kind="backspace",
            before=before,
            after=after,
            text=removed,
        )

        if not self.validate_beforeinput(event):
            return

        super().do_backspace(from_undo=from_undo, mode=mode)

    def _is_char_allowed(self, char: str) -> bool:
        if self.number_type == "int":
            return char in "0123456789-"

        return char in "0123456789-."
