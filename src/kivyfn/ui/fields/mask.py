# kivyfn/ui/fields/mask.py
from __future__ import annotations

from typing import Any
from kivy.clock import Clock
from kivy.properties import BooleanProperty, OptionProperty, StringProperty

from kivyfn.ui.behaviors.field import FnFieldCursorBehavior
from kivyfn.ui.fields.base import FnBaseField
from kivyfn.ui.fields.event import InputEvent, InputKind


class FnMaskField(FnFieldCursorBehavior, FnBaseField):
    pattern = StringProperty("(###) ####-####")
    pattern_char = StringProperty("#")
    allowed_chars = StringProperty("")

    show_literals = BooleanProperty(False)
    show_placeholders = BooleanProperty(False)
    placeholder_char = StringProperty("_")

    unfocus_on_fill = BooleanProperty(False)
    edit_mode = OptionProperty("overwrite", options=["append", "overwrite"])
    value_mode = OptionProperty("raw", options=["raw", "formatted"])

    def __init__(self, **kwargs: Any) -> None:
        self._display_to_slot_positions: list[int] = [0]
        self._slot_to_display_positions: dict[int, int] = {}
        self._slot_values: list[str] = []
        self._cursor_width_before_placeholders = 2
        self._internal_cursor_move = False
        self._last_valid_cursor_idx = 0

        super().__init__(**kwargs)
        self.multiline = False
        self.write_tab = False
        self.valign = "center"

        self._cursor_width_before_placeholders = self.cursor_width or 2
        if not self.cursor_width:
            self.cursor_width = 2

        self._slot_values = self._slots_from_raw(self._value or "")
        self._sync_cursor_width()
        self._refresh_display()

    # ---------------------------------------------------------
    # intercept _set_value to update slot values
    # ---------------------------------------------------------
    def _set_value(self, value: Any) -> bool:
        """
        Overrides the internal API setter. 
        Runs ONLY on programmatic updates (e.g., field.value = "00:15:30").
        """
        # 1. Let the base class handle validation, assigning self._value, 
        #    and converting/setting self.text
        success = super()._set_value(value)
        
        # If validation fails in the base class chain, halt immediately
        if not success:
            return False

        # 2. Since the value is valid and committed, sync your mask's internal slots
        raw_data = self._value_to_raw(value)
        self._slot_values = self._slots_from_raw(raw_data)

        return True

    def _clear_on_focus(self) -> None:
        if not self.clear_on_focus:
            return

        self._slot_values = self._empty_slots()
        self._value = ""
        self._refresh_display()

    # ---------------------------------------------------------
    # Value conversion (Intercepting the Base Class Hooks)
    # ---------------------------------------------------------
    def text_to_value(self) -> str:
        """
        Converts the visual UI text back into the value property.
        If mode is raw, strips out mask symbols. If formatted, keeps them.
        """
        if self.value_mode == "formatted":
            return self.text
        return self._slots_to_raw(self._slot_values)

    def value_to_text(self, value: Any) -> str:
        """
        Takes whatever value the developer assigns programmatically 
        and updates the display layout cleanly.
        """
        slots = self._slots_from_raw(self._value_to_raw(value))
        return self._format_slots(slots, update_maps=False)

    # ---------------------------------------------------------
    # Validation
    # ---------------------------------------------------------
    def validate_value(self, value: Any) -> bool:
        return self._validate_slots(self._slots_from_raw(self._value_to_raw(value)))

    def validate_beforeinput(self, event: InputEvent) -> bool:
        return isinstance(event.after, str) and self._validate_slots(self._slots_from_raw(event.after))

    def validate_mask_char(self, char: str) -> bool:
        return len(char) == 1 and (not self.allowed_chars or char in self.allowed_chars)

    def validate_section(self, index: int, value: str) -> bool:
        return True

    def _validate_slots(self, slots: list[str]) -> bool:
        if len(slots) != self._slot_count():
            return False
        if any(c and not self.validate_mask_char(c) for c in slots):
            return False

        for idx, (start, end) in enumerate(self._section_ranges()):
            section_slots = slots[start:end]
            if section_slots and all(section_slots):
                if not self.validate_section(idx, "".join(section_slots)):
                    return False
        return True

    # ---------------------------------------------------------
    # Pattern & Slot Helpers
    # ---------------------------------------------------------
    def _get_pattern_char(self) -> str:
        return self.pattern_char[0] if self.pattern_char else "#"

    def _get_placeholder_char(self) -> str:
        return self.placeholder_char[0] if self.placeholder_char else " "

    def _slot_count(self) -> int:
        return self.pattern.count(self._get_pattern_char())

    def _mask_literals(self) -> set[str]:
        p_char = self._get_pattern_char()
        return {c for c in self.pattern if c != p_char}

    def _section_ranges(self) -> list[tuple[int, int]]:
        sections: list[tuple[int, int]] = []
        p_char = self._get_pattern_char()
        start, in_sec = 0, False

        for i, char in enumerate(self.pattern):
            if char == p_char:
                if not in_sec:
                    start = self.pattern[:i].count(p_char)
                    in_sec = True
            elif in_sec:
                sections.append((start, self.pattern[:i].count(p_char)))
                in_sec = False
        if in_sec:
            sections.append((start, self._slot_count()))
        return sections

    def _empty_slots(self) -> list[str]:
        return [""] * self._slot_count()

    def _normalize_slots(self, slots: list[str]) -> list[str]:
        count = self._slot_count()
        return [slots[i][0] if (i < len(slots) and slots[i]) else "" for i in range(count)]

    def _slots_from_raw(self, raw: Any) -> list[str]:
        if isinstance(raw, bytes):
            raw = raw.decode("utf8")
        extracted = self._extract_raw(str(raw or ""))
        slots = self._empty_slots()
        for i, char in enumerate(extracted[:len(slots)]):
            slots[i] = char
        return slots

    def _slots_to_raw(self, slots: list[str]) -> str:
        return "".join(c for c in slots if c)

    def _compact_slots(self, slots: list[str] | None = None) -> list[str]:
        return self._slots_from_raw(self._slots_to_raw(slots or self._slot_values))

    def _all_slots_filled(self, slots: list[str] | None = None) -> bool:
        slots = slots or self._slot_values
        return bool(slots) and all(bool(c) for c in slots)

    def _next_append_slot_index(self, slots: list[str] | None = None) -> int:
        return min(len(self._slots_to_raw(slots or self._slot_values)), self._slot_count())

    def _has_filled_at_or_after(self, slots: list[str], slot_index: int) -> bool:
        return any(bool(c) for c in slots[slot_index:])

    def _set_slots(self, slots: list[str], *, cursor_slot: int) -> None:
        self._slot_values = self._normalize_slots(slots)
        self._value = self._slots_to_raw(self._slot_values)
        self.text = self._format_slots(self._slot_values)
        self._set_real_cursor_from_slot(cursor_slot)
        self._sync_cursor_box_visibility()

    # ---------------------------------------------------------
    # Parsing / Raw Extraction
    # ---------------------------------------------------------
    def _value_to_raw(self, value: Any) -> str:
        if isinstance(value, bytes):
            value = value.decode("utf8")
        return self._extract_raw(str(value or ""))[:self._slot_count()]

    def _looks_like_formatted_text(self, text: str) -> bool:
        if len(text) != len(self.pattern):
            return False
        p_char = self._get_pattern_char()
        return all(p == t for p, t in zip(self.pattern, text) if p != p_char)

    def _extract_raw_from_formatted_text(self, text: str) -> str:
        p_char = self._get_pattern_char()
        ph = self._get_placeholder_char()
        return "".join(t for p, t in zip(self.pattern, text) if p == p_char and t != ph and self.validate_mask_char(t))

    def _extract_raw(self, text: str) -> str:
        if isinstance(text, bytes):
            text = text.decode("utf8")
        if self._looks_like_formatted_text(text):
            return self._extract_raw_from_formatted_text(text)

        ph = self._get_placeholder_char()
        skip_chars = (self._mask_literals() if not self.allowed_chars else set()) | {"\r", "\n", ph}
        return "".join(c for c in text if c not in skip_chars and (not self.allowed_chars or self.validate_mask_char(c)))

    # ---------------------------------------------------------
    # Layout and Formatting Engine
    # ---------------------------------------------------------
    def _format_slots(self, slots: list[str], *, update_maps: bool = True) -> str:
        slots = self._normalize_slots(slots)
        text_parts: list[str] = []
        display_to_slot: list[int] = [0]
        slot_to_display: dict[int, int] = {}

        slot_idx = 0
        slot_count = self._slot_count()
        p_char = self._get_pattern_char()
        ph = self._get_placeholder_char()
        show_all = self.show_literals or self.show_placeholders

        for char in self.pattern:
            disp_idx = len(text_parts)
            if char == p_char:
                slot_to_display.setdefault(slot_idx, disp_idx)
                val = slots[slot_idx] if slot_idx < slot_count else ""

                if val or self.show_placeholders:
                    text_parts.append(val or ph)
                    display_to_slot.append(min(slot_idx + 1, slot_count))
                slot_idx += 1
            elif show_all or self._has_filled_at_or_after(slots, slot_idx):
                text_parts.append(char)
                display_to_slot.append(min(slot_idx, slot_count))

        slot_to_display.setdefault(slot_count, len(text_parts))
        if update_maps:
            self._display_to_slot_positions = display_to_slot
            self._slot_to_display_positions = slot_to_display

        return "".join(text_parts)

    def _refresh_display(self) -> None:
        self._slot_values = self._normalize_slots(self._slot_values)
        self._value = self._slots_to_raw(self._slot_values)
        self.text = self._format_slots(self._slot_values)
        cursor_slot = self._next_append_slot_index() if self.edit_mode == "append" else self._display_to_slot_index(self.cursor_index())
        self._set_real_cursor_from_slot(cursor_slot)
        self._sync_cursor_box_visibility()

    # ---------------------------------------------------------
    # Cursor Alignment & Translation
    # ---------------------------------------------------------
    def _display_to_slot_index(self, display_index: int) -> int:
        if not self._display_to_slot_positions:
            return 0
        idx = max(0, min(display_index, len(self._display_to_slot_positions) - 1))
        return max(0, min(self._display_to_slot_positions[idx], self._slot_count()))

    def _slot_to_display_index(self, slot_index: int) -> int:
        slot_index = max(0, min(slot_index, self._slot_count()))
        return self._slot_to_display_positions.get(slot_index, len(self.text))

    def _set_real_cursor_from_slot(self, slot_index: int) -> None:
        disp_idx = self._slot_to_display_index(slot_index)
        def _set_cursor(*_: Any) -> None:
            self.cancel_selection()
            self._internal_cursor_move = True
            self.cursor = self.get_cursor_from_index(disp_idx)
            self._last_valid_cursor_idx = disp_idx
            self._internal_cursor_move = False
            self._sync_cursor_box_visibility()
        Clock.schedule_once(_set_cursor, 0)

    def _sync_cursor_width(self) -> None:
        if self.show_placeholders:
            if self.cursor_width != 0:
                self._cursor_width_before_placeholders = self.cursor_width or 2
            self.cursor_width = 0
        elif self.cursor_width == 0:
            self.cursor_width = self._cursor_width_before_placeholders or 2

    def _sync_cursor_box_visibility(self) -> None:
        self.cursor_box_visible = bool(self.show_placeholders and self.focus)

    def on_cursor(self, instance: Any, value: Any) -> None:
        self._sync_cursor_box_visibility()
        if self._internal_cursor_move or not self.text:
            return

        current_idx = self.cursor_index()
        valid_indices = sorted(list(self._slot_to_display_positions.values()))
        
        if current_idx not in valid_indices and valid_indices:
            # Determine direction of cursor movement
            moving_forward = current_idx > self._last_valid_cursor_idx
            
            if moving_forward:
                # Find the next available editable index ahead of us
                allowed = [i for i in valid_indices if i >= current_idx]
                target_idx = allowed[0] if allowed else valid_indices[-1]
            else:
                # Find the previous editable index behind us
                allowed = [i for i in valid_indices if i <= current_idx]
                target_idx = allowed[-1] if allowed else valid_indices[0]
                
            self._internal_cursor_move = True
            self.cursor = self.get_cursor_from_index(target_idx)
            self._last_valid_cursor_idx = target_idx
            self._internal_cursor_move = False
        else:
            self._last_valid_cursor_idx = current_idx

    # ---------------------------------------------------------
    # Selection Bounds
    # ---------------------------------------------------------
    def _get_selection_display_range(self) -> tuple[int, int]:
        start = getattr(self, "_selection_from", None)
        end = getattr(self, "_selection_to", None)
        if start is not None and end is not None and start != end:
            return min(start, end), max(start, end)
        idx = self.cursor_index()
        return idx, idx

    def _get_selection_slot_range(self) -> tuple[int, int]:
        start, end = self._get_selection_display_range()
        s_slot, e_slot = self._display_to_slot_index(start), self._display_to_slot_index(end)
        return min(s_slot, e_slot), max(s_slot, e_slot)

    def _has_selection(self) -> bool:
        start, end = self._get_selection_display_range()
        return start != end

    def _clear_slot_range(self, slots: list[str], start_slot: int, end_slot: int) -> list[str]:
        slots = slots.copy()
        for idx in range(max(0, start_slot), min(end_slot, self._slot_count())):
            slots[idx] = ""
        return slots

    # ---------------------------------------------------------
    # Mutation Pipelines
    # ---------------------------------------------------------
    def _input_is_allowed(self, *, kind: InputKind, before: str, after_slots: list[str], text: str) -> bool:
        event = InputEvent(field=self, kind=kind, before=before, after=self._slots_to_raw(after_slots), text=text)
        return self._validate_slots(after_slots) and self.validate_beforeinput(event)

    def _unfocus_on_fill(self, cursor_slot: int) -> None:
        if not self.unfocus_on_fill or cursor_slot < self._slot_count() or not self._all_slots_filled():
            return

        def _unfocus(*_: Any) -> None:
            if self.unfocus_on_fill and self._all_slots_filled() and self._display_to_slot_index(self.cursor_index()) >= self._slot_count():
                self.focus = False
        Clock.schedule_once(_unfocus, 0)

    def insert_text(self, substring: str, from_undo: bool = False) -> None:
        if self.readonly or not substring:
            return
        raw_insert = "".join(c for c in self._extract_raw(substring) if self.validate_mask_char(c))
        if not raw_insert:
            return

        before = self._slots_to_raw(self._slot_values)
        slots = self._slot_values.copy()

        if self._has_selection():
            start, end = self._get_selection_slot_range()
            slots = self._clear_slot_range(slots, start, end)
            if self.edit_mode == "append":
                slots = self._compact_slots(slots)
            slot_idx = start if self.edit_mode == "overwrite" else self._next_append_slot_index(slots)
        else:
            slot_idx = self._next_append_slot_index(slots) if self.edit_mode == "append" else self._display_to_slot_index(self.cursor_index())

        inserted: list[str] = []
        for char in raw_insert:
            if slot_idx >= self._slot_count():
                break
            slots[slot_idx] = char
            inserted.append(char)
            slot_idx += 1

        if inserted and self._input_is_allowed(kind= "replace" if self.selection_text else ("paste" if len(raw_insert) > 1 else "insert"), before=before, after_slots=slots, text="".join(inserted)):
            self.cancel_selection()
            self._set_slots(slots, cursor_slot=slot_idx)
            self._unfocus_on_fill(slot_idx)

    def do_backspace(self, from_undo: bool = False, mode: str = "bkspc") -> None:
        if self.readonly:
            return
        before = self._slots_to_raw(self._slot_values)
        slots = self._slot_values.copy()

        if self._has_selection():
            start, end = self._get_selection_slot_range()
            removed = "".join(slots[start:end])
            slots = self._clear_slot_range(slots, start, end)
            if not removed:
                self.cancel_selection()
                self._set_real_cursor_from_slot(start)
                return
            if self._input_is_allowed(kind="backspace", before=before, after_slots=slots, text=removed):
                self.cancel_selection()
                self._set_slots(slots if self.edit_mode == "overwrite" else self._compact_slots(slots), cursor_slot=start)
            return

        slot_idx = (self._next_append_slot_index(slots) if self.edit_mode == "append" else self._display_to_slot_index(self.cursor_index())) - 1
        if slot_idx < 0:
            return

        removed = slots[slot_idx]
        if not removed:
            self._set_real_cursor_from_slot(slot_idx)
            return

        slots[slot_idx] = ""
        if self._input_is_allowed(kind="backspace", before=before, after_slots=slots, text=removed):
            self.cancel_selection()
            self._set_slots(slots, cursor_slot=slot_idx)

    def delete_selection(self, from_undo: bool = False) -> None:
        if self.readonly or not self._has_selection():
            return
        before = self._slots_to_raw(self._slot_values)
        slots = self._slot_values.copy()
        start, end = self._get_selection_slot_range()

        removed = "".join(slots[start:end])
        slots = self._clear_slot_range(slots, start, end)
        if not removed:
            self.cancel_selection()
            self._set_real_cursor_from_slot(start)
            return

        if self._input_is_allowed(kind="delete", before=before, after_slots=slots, text=removed):
            self.cancel_selection()
            if self.edit_mode == "append":
                slots = self._compact_slots(slots)
            self._set_slots(slots, cursor_slot=self._next_append_slot_index(slots) if self.edit_mode == "append" else start)

    def do_delete(self) -> None:
        if self.readonly:
            return
        if self._has_selection():
            self.delete_selection()
            return
        if self.edit_mode == "append":
            self.do_backspace()
            return

        before = self._slots_to_raw(self._slot_values)
        slots = self._slot_values.copy()
        slot_idx = self._display_to_slot_index(self.cursor_index())

        if slot_idx >= self._slot_count() or not slots[slot_idx]:
            return

        removed = slots[slot_idx]
        slots[slot_idx] = ""
        if self._input_is_allowed(kind="delete", before=before, after_slots=slots, text=removed):
            self.cancel_selection()
            self._set_slots(slots, cursor_slot=slot_idx)

    def cut(self) -> None:
        if getattr(self, "selection_text", ""):
            self.copy()
            self.delete_selection()

    # ---------------------------------------------------------
    # Event Handlers & Hooks
    # ---------------------------------------------------------
    def keyboard_on_key_down(self, window: Any, keycode: Any, text: str, modifiers: Any):
        if keycode[0] == 127:
            self.do_delete()
            return True
        res = super().keyboard_on_key_down(window, keycode, text, modifiers)
        self._sync_cursor_box_visibility()
        return res

    def _on_textinput_focused(self, instance: Any, value: bool, *largs: Any) -> None:
        super()._on_textinput_focused(instance, value, *largs)
        self._sync_cursor_box_visibility()
        if value and self.edit_mode == "append":
            self._set_real_cursor_from_slot(self._next_append_slot_index())
        if not value:
            self.cancel_selection()

    def on_touch_up(self, touch: Any):
        handled = super().on_touch_up(touch)
        if self.collide_point(*touch.pos) and self.focus:
            self._sync_cursor_box_visibility()
            if self.edit_mode == "append":
                self._set_real_cursor_from_slot(self._next_append_slot_index())
        return handled

    # ---------------------------------------------------------
    # Property Observer Dispatches
    # ---------------------------------------------------------
    def on_pattern(self, instance: Any, value: str) -> None:
        self._refresh_display()

    def on_pattern_char(self, instance: Any, value: str) -> None:
        self._refresh_display()

    def on_show_literals(self, instance: Any, value: bool) -> None:
        self._refresh_display()

    def on_show_placeholders(self, instance: Any, value: bool) -> None:
        self._sync_cursor_width()
        self._refresh_display()
        self._sync_cursor_box_visibility()

    def on_placeholder_char(self, instance: Any, value: str) -> None:
        self._refresh_display()

    def on_edit_mode(self, instance: Any, value: str) -> None:
        if value == "append":
            self._slot_values = self._compact_slots()
        self._refresh_display()
