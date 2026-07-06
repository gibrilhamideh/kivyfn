# kivyfn/ui/fields/slot.py
from __future__ import annotations

from typing import Any

from kivy.clock import Clock
from kivy.properties import (
    AliasProperty,
    BooleanProperty,
    ListProperty,
    NumericProperty,
    OptionProperty,
    StringProperty,
)

from kivyfn.ui.fields.base import FnBaseField
from kivyfn.ui.fields.event import InputEvent
from kivyfn.ui.behaviors.field import FnFieldSlotBehavior


class FnSlotField(FnFieldSlotBehavior, FnBaseField):
    slots = ListProperty([])
    length = NumericProperty(6)
    allowed_chars = StringProperty("")
    slot_spacing = NumericProperty(3)
    slot_direction = OptionProperty("left", options=["left", "right"])

    unfocus_on_fill = BooleanProperty(False)
    transform_uppercase = BooleanProperty(False)

    slot_font_name = StringProperty("NotoSansMono")

    def _get_is_complete(self) -> bool:
        if not self.slots:
            return False

        for char in self.slots:
            if char is None:
                return False

        return True

    completed = AliasProperty(
        _get_is_complete,
        None,
        bind=("slots",),
    )

    def _get_default_slots(self) -> list[str | None]:
        return [None] * max(0, int(self.length))

    default_slots = AliasProperty(
        _get_default_slots,
        None,
        bind=("length",),
    )

    def __init__(self, **kwargs: Any) -> None:
        self._setting_slots = False

        super().__init__(**kwargs)

        self._active_slot = 0
        self._editable_positions: dict[int, int] = {}
        self._slot_navigation: list[int] = []
        self._slot_navigation_lookup: dict[int, int] = {}

        self._active_trigger = Clock.create_trigger(
            self._apply_active_slot,
            -1,
        )

    def on_kv_post(self, base_widget: Any) -> None:
        self.selection_color = 0, 0, 0, 0
        self.size_hint = None, None
        self.multiline = False
        self.cursor_width = 0
        self.cursor_blink = False
        self.write_tab = False
        self.font_name = self.slot_font_name

        self._rebuild_all()
        super().on_kv_post(base_widget)

    # ---------------------------------------------------------
    # Value conversion
    # ---------------------------------------------------------
    def text_to_value(self) -> str:
        return self._slots_to_value(self.slots)

    def value_to_text(self, value: Any) -> str:
        self._set_slots(self._normalize_value(value))
        self._rebuild_slot_navigation()

        if self._slot_navigation:
            self._active_slot = self._get_first_empty_slot()

        return self._build_text()

    # ---------------------------------------------------------
    # Validation
    # ---------------------------------------------------------
    def validate_value(self, value: Any) -> bool:
        try:
            slots = self._normalize_value(value)
        except Exception:
            return False

        for char in slots:
            if char is not None and not self.validate_slot_char(char):
                return False

        return True

    def validate_beforeinput(self, event: InputEvent) -> bool:
        after = event.after

        if not isinstance(after, list):
            return False

        for char in after:
            if char is not None and not self.validate_slot_char(char):
                return False

        return True

    def validate_slot_char(self, char: str) -> bool:
        if not char:
            return False

        if len(char) != 1:
            return False

        if not self.allowed_chars:
            return True

        return char in self.allowed_chars

    # ---------------------------------------------------------
    # Slots
    # ---------------------------------------------------------
    def _copy_slots(self, slots: list[str | None]) -> list[str | None]:
        return [char for char in slots]

    def _slots_to_value(self, slots: list[str | None]) -> str:
        return "".join(char for char in slots if char is not None)

    def _set_slots(self, slots: list[str | None]) -> None:
        self._setting_slots = True
        self.slots = self._copy_slots(slots)
        self._value = self._slots_to_value(self.slots)
        self._setting_slots = False

    def _normalize_value(self, value: Any) -> list[str | None]:
        length = max(0, int(self.length))

        if value is None:
            return [None] * length

        if isinstance(value, list):
            source = value
        else:
            source = list(str(value))

        slots: list[str | None] = []

        for index in range(length):
            char = source[index] if index < len(source) else None

            if char == "":
                char = None
            elif char is not None:
                char = str(char)[0]

            slots.append(char)

        return slots

    # ---------------------------------------------------------
    # Navigation
    # ---------------------------------------------------------
    def _get_slot_indices(self) -> list[int]:
        indices = list(range(max(0, int(self.length))))

        if self.slot_direction == "right":
            indices.reverse()

        return indices

    def _rebuild_slot_navigation(self) -> None:
        order = self._get_slot_indices()

        self._slot_navigation = order
        self._slot_navigation_lookup = {
            slot: index for index, slot in enumerate(order)
        }

    def _move_slot(self, direction: int) -> None:
        next_slot = self._get_adjacent_slot(self._active_slot, direction)

        if next_slot is not None:
            self._set_active_slot(next_slot)

    def _get_adjacent_slot(self, slot: int, direction: int) -> int | None:
        index = self._slot_navigation_lookup.get(slot)

        if index is None:
            return None

        index += direction

        if 0 <= index < len(self._slot_navigation):
            return self._slot_navigation[index]

        return None

    def _get_first_empty_slot(self) -> int:
        for slot in self._slot_navigation:
            if self.slots[slot] is None:
                return slot

        if self._slot_navigation:
            return self._slot_navigation[-1]

        return 0

    def _get_nearest_slot_from_column(self, column: int) -> int | None:
        if not self._editable_positions:
            return None

        def distance(item: tuple[int, int]) -> int:
            _, position = item
            return abs(column - position)

        slot, _ = min(self._editable_positions.items(), key=distance)
        return slot

    # ---------------------------------------------------------
    # Rendering
    # ---------------------------------------------------------
    def _display_char(self, char: str | None) -> str:
        return char if char is not None else " "

    def _build_render_tokens(self) -> list[tuple[str, int]]:
        tokens: list[tuple[str, int]] = []

        for slot_index, char in enumerate(self.slots):
            tokens.append((self._display_char(char), slot_index))

        return tokens

    def _build_text(self) -> str:
        tokens = self._build_render_tokens()

        self._editable_positions.clear()

        parts: list[str] = []
        position = 0
        last_index = len(tokens) - 1

        for index, (text, slot_index) in enumerate(tokens):
            parts.append(text)
            self._editable_positions[slot_index] = position

            position += len(text)

            if index == last_index:
                continue

            spacing = " " * max(0, int(self.slot_spacing))
            parts.append(spacing)
            position += len(spacing)

        text = "".join(parts)

        if callable(self.formatter) and not self.focus:
            formatted = self.formatter(text, self.value)

            if isinstance(formatted, str):
                return formatted

        return text

    def _render(self) -> None:
        self.text = self._build_text()

        if self.slot_visuals:
            self._slot_graphics_trigger()

    def _rebuild_all(self) -> None:
        length = max(0, int(self.length))

        if length <= 0:
            self._set_slots([])
            self._editable_positions.clear()
            self._slot_navigation.clear()
            self._slot_navigation_lookup.clear()
            self.text = ""
            self._clear_slots_graphics()
            return

        if not self.slots or len(self.slots) != length:
            self._set_slots(self.default_slots)
        else:
            self._set_slots(self._normalize_value(self.slots))

        self._rebuild_slot_navigation()

        if self._slot_navigation:
            self._active_slot = self._get_first_empty_slot()

        self._render()

        if self.slot_visuals:
            self._create_slots_graphics()

    # ---------------------------------------------------------
    # Active slot
    # ---------------------------------------------------------
    def _set_active_slot(self, slot: int) -> None:
        index = self._slot_navigation_lookup.get(slot)

        if index is None:
            return

        first_empty = self._get_first_empty_slot()
        first_empty_index = self._slot_navigation_lookup.get(first_empty, -1)

        if index > first_empty_index:
            return

        self._active_slot = slot
        self._active_trigger()

    def _apply_active_slot(self, *_: Any) -> None:
        if not self.focus:
            return

        position = self._editable_positions.get(self._active_slot)

        if position is None:
            self.cancel_selection()
            return

        self.cursor = (position, 0)

        if self.slot_highlight:
            self.select_text(position, position + 1)
        else:
            self.cancel_selection()

        if self.slot_visuals:
            self._update_slot_style()

    # ---------------------------------------------------------
    # Editing
    # ---------------------------------------------------------
    def transform_char(self, char: str) -> str | None:
        if self.transform_uppercase:
            return char.upper()

        return char

    def insert_text(self, substring: str, from_undo: bool = False) -> None:
        if self.readonly or not substring:
            return

        if not self._slot_navigation:
            return

        slot = self._active_slot

        before = self._copy_slots(self.slots)
        updated = self._copy_slots(self.slots)

        accepted: list[str] = []

        for char in substring:
            char = self.transform_char(char)

            if not char:
                continue

            if char in "\r\n\t":
                continue

            if char == " ":
                continue

            if not self.validate_slot_char(char):
                continue

            updated[slot] = char
            accepted.append(char)

            next_slot = self._get_adjacent_slot(slot, 1)

            if next_slot is None:
                break

            slot = next_slot

        if not accepted:
            return

        after = self._copy_slots(updated)

        event = InputEvent(
            field=self,
            kind="paste" if len(accepted) > 1 else "insert",
            before=before,
            after=after,
            text="".join(accepted),
        )

        if not self.validate_beforeinput(event):
            return

        self._set_slots(updated)
        self._render()
        self._set_active_slot(slot)

        if self.completed and self.unfocus_on_fill:
            self.focus = False

    def do_backspace(
        self,
        from_undo: bool = False,
        mode: str = "bkspc",
    ) -> None:
        if self.readonly:
            return

        if not self._slot_navigation:
            return

        slot = self._active_slot

        before = self._copy_slots(self.slots)
        updated = self._copy_slots(self.slots)

        removed = updated[slot]

        if updated[slot] is not None:
            updated[slot] = None
        else:
            previous_slot = self._get_adjacent_slot(slot, -1)

            if previous_slot is None:
                return

            slot = previous_slot
            removed = updated[slot]
            updated[slot] = None

        after = self._copy_slots(updated)

        event = InputEvent(
            field=self,
            kind="backspace",
            before=before,
            after=after,
            text="" if removed is None else removed,
        )

        if not self.validate_beforeinput(event):
            return

        self._set_slots(updated)
        self._render()
        self._set_active_slot(slot)

    # ---------------------------------------------------------
    # Keyboard
    # ---------------------------------------------------------
    def keyboard_on_key_down(
        self,
        window: Any,
        keycode: Any,
        text: str,
        modifiers: Any,
    ):
        if not self.focus:
            return super().keyboard_on_key_down(
                window,
                keycode,
                text,
                modifiers,
            )

        key = keycode[0]

        if key == 8:
            self.do_backspace()
            return True

        if key == 9:
            direction = -1 if "shift" in modifiers else 1
            self._move_slot(direction)
            return True

        if key == 32:
            self._move_slot(1)
            return True

        if key == 276:
            self._move_slot(-1)
            return True

        if key == 275:
            self._move_slot(1)
            return True

        return super().keyboard_on_key_down(
            window,
            keycode,
            text,
            modifiers,
        )

    def keyboard_on_textinput(self, window: Any, text: str):
        if not self.focus:
            return super().keyboard_on_textinput(window, text)

        if text == " " or text == "\t":
            return

        self.insert_text(text)
        return

    # ---------------------------------------------------------
    # Focus / touch
    # ---------------------------------------------------------
    def _on_textinput_focused(
        self,
        instance: Any,
        value: bool,
        *largs: Any,
    ):
        super()._on_textinput_focused(instance, value, *largs)

        if value:
            self._render()

            slot = self._get_first_empty_slot()
            self._set_active_slot(slot)

            return

        self._unfocus_slots()

    def on_touch_up(self, touch: Any):
        handled = super().on_touch_up(touch)

        if self.collide_point(*touch.pos) and self.focus:
            slot = self._get_first_empty_slot()
            self._set_active_slot(slot)
            return True

        return handled

    def _clear_on_focus(self) -> None:
        if not self.clear_on_focus:
            return

        self._set_slots(self.default_slots)
        self._render()

        if self._slot_navigation:
            self._active_slot = self._get_first_empty_slot()
            self._set_active_slot(self._active_slot)

    # ---------------------------------------------------------
    # Property updates
    # ---------------------------------------------------------
    def on_length(self, *_: Any) -> None:
        self._rebuild_all()

    def on_slots(self, *_: Any) -> None:
        if self._setting_slots:
            return

        self._rebuild_all()

    def on_slot_spacing(self, *_: Any) -> None:
        self._rebuild_all()

    def on_slot_direction(self, *_: Any) -> None:
        self._rebuild_all()
