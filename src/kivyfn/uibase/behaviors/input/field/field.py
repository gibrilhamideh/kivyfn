from __future__ import annotations
from typing import Any, Callable
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

    formater: Callable = ObjectProperty(None, allownone=True)

    # ---------------------------------------------------------
    # Internal Properties
    # ---------------------------------------------------------
    _cached_value = ObjectProperty(None, allownone=True)

    # ---------------------------------------------------------
    # Value API (must be implemented by subclasses)
    # ---------------------------------------------------------
    def _get_value(self):
        raise NotImplementedError(
            f"{self.__class__.__name__} must implement _get_value()"
        )

    def _set_value(self, value, from_cache=False):
        raise NotImplementedError(
            f"{self.__class__.__name__} must implement _set_value()"
        )

    def _alias_get(self):
        return self._get_value()

    def _alias_set(self, value):
        return self._set_value(value)

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
    def _on_textinput_focused(self, instance, focused, *largs):
        super()._on_textinput_focused(instance, focused, *largs)  # pyright: ignore

        if focused:
            self.valid = True
            return

        new_value = self._get_value()
        valid = self.validate_value(new_value)

        if not valid:
            if self.revert_on_invalid:
                self._set_value(self._cached_value, from_cache=True)
                self.valid = True
            else:
                self.valid = False

            return

        self.valid = True

        # Only commit if value actually changed
        if new_value != self._cached_value:
            self.value = new_value
            self.dispatch("on_commit", new_value)  # pyright: ignore

    def on_commit(self, value):
        pass
