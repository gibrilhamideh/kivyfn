from __future__ import annotations
from typing import Any
from kivy.properties import AliasProperty, BooleanProperty, ObjectProperty


class FnFieldBaseBehavior:
    """
    Base behavior for all input fields.

    IMPORTANT:
    Developers should interact with `value`, not `text`.

    Subclasses must implement:

        _get_value()
        _set_value(value)
    """

    # ---------------------------------------------------------
    # Public Properties
    # ---------------------------------------------------------

    valid = BooleanProperty(False)

    revert_on_invalid = BooleanProperty(True)

    default: Any = ObjectProperty(None, allownone=True)

    # ---------------------------------------------------------
    # Internal Properties
    # ---------------------------------------------------------
    _value: Any = None
    _cached_value = ObjectProperty(None, allownone=True)

    # ---------------------------------------------------------
    # Value API (must be implemented by subclasses)
    # ---------------------------------------------------------
    #
    def _get_value(self):
        return self._value

    def _set_value(self, value):
        self._value = value

    def _alias_get(self):
        return self._get_value()

    def _alias_set(self, value):
        self._set_value(value)

    value = AliasProperty(
        _alias_get,
        _alias_set,
    )

    __events__ = ("on_commit",)

    # ---------------------------------------------------------
    # Validation Hooks
    # ---------------------------------------------------------
    def validate_char(self, char: str) -> bool:
        """
        Character-level validation.

        Used during typing.

        Default: allow everything.
        """
        return True

    def validate_segment(self, index: int, chars: list[str]) -> bool:
        """
        Segment-level validation.

        Used by segmented fields.

        Default: allow everything.
        """
        return True

    def validate_partial(self, value: Any) -> bool:
        """
        Validation during editing.

        Allows temporary states while typing.

        Default: allow everything.
        """
        return True

    def validate_value(self, value: Any) -> bool:
        """
        Final validation.

        Called when editing finishes (blur or submit).

        Default: valid.
        """
        return True

    # ---------------------------------------------------------
    # Focus Handling
    # ---------------------------------------------------------

    def on_focus(self, instance, focused):
        if focused:
            self._cached_value = self.value
            self.valid = True
            return

        value = self.value
        valid = self.validate_value(value)

        if not valid and self.revert_on_invalid:
            self.value = self._cached_value
            self.valid = True
        else:
            self.valid = valid
            self.dispatch("on_commit", value)

    def on_commit(self, value):
        pass
