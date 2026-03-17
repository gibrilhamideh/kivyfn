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
    placeholder = StringProperty("_")

    segments = ListProperty([])

    segment_spacing = NumericProperty(0)
    segment_direction = OptionProperty("left", options=["left", "right"])
    segment_fill_direction = OptionProperty("left", options=["left", "right"])
    editable_segments = ListProperty(None, allownone=True)
    sequential = BooleanProperty(False)

    unfocus_on_fill = BooleanProperty(False)

    slot_highlight = BooleanProperty(True)
    slot_visuals = BooleanProperty(False)
    slot_background_color = ColorProperty((1, 0, 0, 0.2))
    slot_border_color = ColorProperty((0, 0, 0, 0))
    slot_background_focused_color = ColorProperty((0, 0, 0, 0))
    slot_border_focused_color = ColorProperty((0, 1, 0, 0.2))
    slot_border_width = NumericProperty(1)
    slot_radius = VariableListProperty([0], length=4)
    slot_padding = NumericProperty(5)
    slot_spacing = NumericProperty(0)

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
        bind=("segments",),
    )

    def _get_default_segments(self):
        return [[None] * length for length in self.lengths]

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
        """
        Index of the currently active segment.
        """

        self._active_slot = 0
        """
        Index of the active slot within the current segment.
        """

        self._editable_positions = {}
        """
        Mapping of slot → text index.

        Keys are (segment_index, slot_index) tuples and values are the
        corresponding character index in the rendered text. This allows
        the widget to translate between the segmented structure and the
        TextInput cursor position.
        """

        self._slot_navigation = []
        """
        Ordered list of editable slots used for navigation.

        Each entry is a (segment_index, slot_index) tuple representing a
        slot in the segmented field. The order of this list defines how
        the cursor moves when navigating between slots.
        """

        self._slot_navigation_lookup = {}
        """
        Mapping of slot → navigation index.

        Keys are (segment_index, slot_index) tuples and values are the
        corresponding position of that slot in `_slot_navigation`. This
        allows fast lookup of a slot's position in the navigation order.
        """

        self._slot_graphics_trigger = Clock.create_trigger(
            self._update_slots_graphics, 0
        )
        """
        Deferred trigger that updates slot graphics positions.

        This batches multiple layout updates (size, position, text changes)
        into a single update on the next frame, avoiding redundant layout work.
        """

        self._active_trigger = Clock.create_trigger(self._apply_active_slot, -1)
        """
        Deferred trigger that applies the active slot highlight.

        Scheduled with `-1` so it runs after Kivy finishes its internal
        TextInput cursor/selection updates, preventing highlight flicker.
        """

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
        """
        Return the order in which segments should be processed.

        Segments are the top-level parts of the field (e.g. HH, MM, SS).
        The order depends on `segment_direction`.

        Returns
        -------
        list[int]
            Segment indices in traversal order.
        """

        indices = list(range(len(self.lengths)))

        if self.segment_direction == "right":
            indices.reverse()

        return indices

    def _get_slot_indices(self, seg) -> list[int]:
        """
        Return the order of slots inside a segment.

        A slot is a single editable position within a segment.
        The order depends on `segment_fill_direction`.

        Parameters
        ----------
        seg : int
            The segment index.

        Returns
        -------
        list[int]
            Slot indices in traversal order.
        """
        order = list(range(self.lengths[seg]))

        if self.segment_fill_direction == "right":
            order.reverse()

        return order

    # ---------------------------------------------------------
    # Slot ordering
    # ---------------------------------------------------------

    def _rebuild_slot_navigation(self) -> None:
        """
        Build the ordered navigation list of all editable slots.

        Each slot is stored as (segment_index, slot_index). A lookup map
        is also created so the position of any slot in the navigation
        order can be found quickly.
        """
        order = []

        for segment_index in self._get_segment_indices():
            if not self._segment_editable(segment_index):
                continue
            for slot_index in self._get_slot_indices(segment_index):
                order.append((segment_index, slot_index))

        self._slot_navigation = order
        self._slot_navigation_lookup = {slot: i for i, slot in enumerate(order)}

    def _segment_editable(self, segment: int) -> bool:
        if self.editable_segments is None:
            return True
        return segment in self.editable_segments

    # ---------------------------------------------------------
    # Rendering
    # ---------------------------------------------------------
    def _build_render_tokens(self):
        """
        Build the list of tokens used to render the field text.

        Each token is a tuple of:

            (display_text, slot_reference)

        display_text
            The character that should appear in the input.

        slot_reference
            A tuple (segment_index, slot_index) for editable slots,
            or None for separators.

        Example
        -------
        segments = [
            ['1', '2'],
            ['3', '4'],
            ['5', None]
        ]

        separator = ":"
        placeholder = "_"

        Result:

        [
            ('1', (0, 0)),
            ('2', (0, 1)),
            (':', None),
            ('3', (1, 0)),
            ('4', (1, 1)),
            (':', None),
            ('5', (2, 0)),
            ('_', (2, 1))
        ]

        Empty slots use the placeholder character.
        """
        tokens = []
        last_segment = len(self.segments) - 1

        for segment_index, segment in enumerate(self.segments):
            for slot_index, slot in enumerate(segment):
                # determine character to display
                char = slot if slot is not None else self.placeholder

                # token = (display_character, slot_reference)
                tokens.append((char, (segment_index, slot_index)))

            # add separator between segments
            if segment_index != last_segment:
                tokens.append((self.separator, None))

        return tokens

    def _render(self):
        """
        Render segments into the TextInput string and record slot positions.

        Spacing between slots and segments is expressed in units of spaces,
        controlled by `slot_spacing` and `segment_spacing`.

        Example
        -------
        segments = [['1','2'], ['3','4']]
        slot_spacing = 1
        segment_spacing = 2
        separator = ":"

        text → "1 2  :  3 4"
        """

        tokens = self._build_render_tokens()

        self._editable_positions.clear()

        parts: list[str] = []
        position = 0

        last_index = len(tokens) - 1

        for i, (text, slot_ref) in enumerate(tokens):
            parts.append(text)

            if slot_ref is not None:
                self._editable_positions[slot_ref] = position

            position += len(text)

            if i == last_index:
                continue

            _, next_slot_ref = tokens[i + 1]

            # determine spacing
            if slot_ref is not None and next_slot_ref is not None:
                spacing = " " * self.slot_spacing
            else:
                spacing = " " * self.segment_spacing

            parts.append(spacing)
            position += len(spacing)

        text = "".join(parts)
        if callable(self.formater) and not self.focus:
            formatted = self.formater(text, self.value, self.completed)
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

        self._rebuild_slot_navigation()

        if self._slot_navigation:
            self._active_segment, self._active_slot = self._slot_navigation[0]

        self._render()

        if self.slot_visuals:
            self._create_slots_graphics()

    # ---------------------------------------------------------
    # Slot navigation
    # ---------------------------------------------------------
    def _move_slot(self, direction):
        nxt = self._get_adjacent_slot(
            self._active_segment, self._active_slot, direction
        )
        if nxt:
            self._set_active_slot(*nxt)

    def _get_adjacent_slot(self, segment: int, slot: int, direction) -> tuple | None:
        """
        Return the adjacent slot in the slot navigation order.

        Parameters
        ----------
        segment : int
            The segment index of the current slot.
        slot : int
            The slot index within the segment.
        direction : int
            +1 to get the next slot, -1 to get the previous slot.

        Returns
        -------
        tuple[int, int] | None
            The (segment_index, slot_index) of the adjacent slot, or None
            if no slot exists in that direction.
        """
        idx = self._slot_navigation_lookup.get((segment, slot))

        if idx is None:
            return None

        idx += direction

        if 0 <= idx < len(self._slot_navigation):
            return self._slot_navigation[idx]

        return None

    def _get_first_empty_slot(self) -> tuple | None:
        """
        Return the first empty slot in navigation order.

        An empty slot is one whose value in `self.segments` is None.

        Example
        -------
        segments = [['1', '2'], ['3', None]]

        Result:
            (1, 1)

        If all slots are filled, the last slot is returned.
        If the field has no slots, None is returned.
        """
        for segment, slot in self._slot_navigation:
            if self.segments[segment][slot] is None:
                return segment, slot

        # if all slots are filled
        if self._slot_navigation:
            return self._slot_navigation[-1]

        return None

    def _get_nearest_slot_from_column(self, column: int) -> tuple[int, int]:
        """Return the editable slot closest to the given text column."""

        def distance(item):
            _, position = item
            return abs(column - position)

        slot, _ = min(self._editable_positions.items(), key=distance)
        return slot

    # ---------------------------------------------------------
    # Active slot
    # ---------------------------------------------------------
    def _set_active_slot(self, seg, char):
        """
        Set the active slot.

        Updates the active segment and slot, then schedules
        `_apply_active_slot()` to update the cursor highlight
        and slot visuals.
        """
        idx = self._slot_navigation_lookup.get((seg, char))

        if idx is None:
            return

        if self.sequential:
            first_empty = self._get_first_empty_slot()
            if first_empty:
                first_empty_idx = self._slot_navigation_lookup.get(first_empty, -1)
                if idx > first_empty_idx:
                    return

        self._active_segment = seg
        self._active_slot = char

        self._active_trigger()

    def _apply_active_slot(self, *_):
        """
        Apply the active slot visually.

        Moves the cursor to the active slot and optionally selects the
        corresponding character in the text. Updates slot visuals if enabled.
        """
        if not self.focus:
            return

        pos = self._editable_positions.get((self._active_segment, self._active_slot))

        if pos is None:
            self.cancel_selection()  # pyright: ignore
            return

        self.cursor = (pos, 0)

        if self.slot_highlight:
            self.select_text(pos, pos + 1)  # pyright: ignore
        else:
            self.cancel_selection()  # pyright: ignore

        if self.slot_visuals:
            self._update_slot_style()

    # ---------------------------------------------------------
    # Editing
    # ---------------------------------------------------------
    def insert_text(self, substring, from_undo=False):
        seg = self._active_segment
        slot = self._active_slot

        updated = [s.copy() for s in self.segments]

        for ch in substring:
            if not self.validate_char(ch):
                continue

            updated[seg][slot] = ch

            nxt = self._get_adjacent_slot(seg, slot, 1)

            if not nxt:
                if self.unfocus_on_fill:
                    self.focus = False
                break

            seg, slot = nxt

        for i, s in enumerate(updated):
            if not self.validate_segment(i, s):
                return

        if not self.validate_partial(updated):
            return

        self.segments = updated

        self._render()
        self._set_active_slot(seg, slot)

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
            self._move_slot(direction)
            return True

        # ---------------------------------------------------------
        # Space → move forward
        # ---------------------------------------------------------
        if key == 32:
            self._move_slot(1)
            return True

        # ---------------------------------------------------------
        # Arrow Left
        # ---------------------------------------------------------
        if key == 276:
            self._move_slot(-1)
            return True

        # ---------------------------------------------------------
        # Arrow Right
        # ---------------------------------------------------------
        if key == 275:
            self._move_slot(1)
            return True

        return super().keyboard_on_key_down(window, keycode, text, modifiers)  # pyright: ignore

    def keyboard_on_textinput(self, window, text):
        if not self.focus:
            return super().keyboard_on_textinput(window, text)  # pyright: ignore

        # consume navigation characters
        if text == " " or text == "\t":
            return True

        self.insert_text(text)
        return True

    def do_backspace(self, from_undo=False, mode="bkspc"):
        seg = self._active_segment
        slot = self._active_slot

        if self.segments[seg][slot] is not None:
            self.segments[seg][slot] = None
        else:
            prev = self._get_adjacent_slot(seg, slot, -1)
            if not prev:
                return
            seg, slot = prev
            self.segments[seg][slot] = None

        self._render()
        self._set_active_slot(seg, slot)

    # ---------------------------------------------------------
    # Focus
    # ---------------------------------------------------------
    def _on_textinput_focused(self, instance, value, *largs):  # pyright: ignore
        super()._on_textinput_focused(instance, value, *largs)

        if value:
            self._render()

            if self.sequential:
                slot = self._get_first_empty_slot()
                if slot:
                    self._set_active_slot(*slot)

        else:
            self._unfocus_slots()

    # ---------------------------------------------------------
    # Mouse
    # ---------------------------------------------------------
    def on_touch_up(self, touch):
        handled = super().on_touch_up(touch)  # pyright: ignore

        if self.collide_point(*touch.pos) and self.focus:  # pyright: ignore
            # sequential mode → always jump to first empty slot
            if self.sequential:
                slot = self._get_first_empty_slot()
                if slot:
                    self._set_active_slot(*slot)
                return True

            # normal mode → activate slot closest to click
            column, _ = self.get_cursor_from_xy(*touch.pos)  # pyright: ignore
            slot = self._get_nearest_slot_from_column(column)

            self._set_active_slot(*slot)
            return True

        return handled

    # ---------------------------------------------------------
    # Slot graphics
    # ---------------------------------------------------------
    def _create_slots_graphics(self):
        """
        Rebuild the canvas graphics used to draw slot backgrounds and borders
        for all editable slots.
        """
        # remove existing slot graphics
        for graphics in self._slot_graphics.values():
            self.canvas.after.remove(graphics["bg_color"])  # pyright: ignore
            self.canvas.after.remove(graphics["bg"])  # pyright: ignore
            self.canvas.after.remove(graphics["border_color"])  # pyright: ignore
            self.canvas.after.remove(graphics["border"])  # pyright: ignore

        self._slot_graphics.clear()

        with self.canvas.after:  # pyright: ignore
            for slot in self._editable_positions:
                bg_color = Color(*self.slot_background_color)

                bg = SmoothRoundedRectangle(
                    pos=(0, 0),
                    size=(0, 0),
                    radius=self.slot_radius,
                )

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

        self._slot_graphics_trigger()

    def _update_slots_graphics(self, *_):
        """
        Update the position and size of all slot graphics.

        Each slot rectangle is positioned to surround the character
        it represents in the rendered TextInput text. This method
        recalculates the geometry based on the current text layout.
        """

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
        """
        Update visual styling of slot graphics.

        The active slot uses the focused background and border colors,
        while all other slots use the default slot colors.
        """
        if not self._slot_graphics:
            return

        active = (self._active_segment, self._active_slot)

        for slot, graphics in self._slot_graphics.items():
            if slot == active:
                graphics["bg_color"].rgba = self.slot_background_focused_color
                graphics["border_color"].rgba = self.slot_border_focused_color
            else:
                graphics["bg_color"].rgba = self.slot_background_color
                graphics["border_color"].rgba = self.slot_border_color

    def _unfocus_slots(self):
        """
        Reset all slot graphics to their unfocused visual state.
        """
        for graphics in self._slot_graphics.values():
            graphics["bg_color"].rgba = self.slot_background_color
            graphics["border_color"].rgba = self.slot_border_color

    # ---------------------------------------------------------
    # Property updates
    # ---------------------------------------------------------
    def on_lengths(self, *_):
        self._rebuild_all()

    def on_separator(self, *_):
        self._rebuild_all()

    def on_slot_spacing(self, *_):
        self._rebuild_all()

    def on_segment_spacing(self, *_):
        self._rebuild_all()

    def on_placeholder(self, *_):
        self._rebuild_all()

    def on_size(self, *args):
        self._slot_graphics_trigger()

    def on_pos(self, *args):
        self._slot_graphics_trigger()

    def on_slot_background_color(self, *_):
        self._update_slot_style()

    def on_slot_border_color(self, *_):
        self._update_slot_style()

    def on_slot_background_focused_color(self, *_):
        self._update_slot_style()

    def on_slot_border_focused_color(self, *_):
        self._update_slot_style()
