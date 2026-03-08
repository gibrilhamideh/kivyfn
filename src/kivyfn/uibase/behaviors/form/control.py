from kivy.properties import (
    ObjectProperty,
    BooleanProperty,
    StringProperty,
)


class FnControlBehavior:
    """
    Base abstraction for all form-capable widgets.

    A control:
    - Holds a value
    - Can be disabled
    - Can be required
    - Can report validation state
    """

    name = StringProperty("")
    """
    Optional identifier used by forms to map values.
    """

    value = ObjectProperty(None)
    """
    Current value of the control.
    """

    disabled = BooleanProperty(False)
    """
    Whether the control is interactive.
    """

    required = BooleanProperty(False)
    """
    Whether the control must have a value.
    """

    error = StringProperty("")
    """
    Validation error message.
    """

    valid = BooleanProperty(True)
    """
    Indicates whether the control passes validation.
    """

    # -------------------------
    # Validation
    # -------------------------

    def validate(self) -> bool:
        """
        Validate the control.

        Override in subclasses for custom logic.
        """
        if self.required and not self.value:
            self.error = "This field is required."
            self.valid = False
            return False

        self.error = ""
        self.valid = True
        return True

    # -------------------------
    # Reset
    # -------------------------

    def reset(self) -> None:
        """
        Reset control to default state.
        """
        self.value = None
        self.error = ""
        self.valid = True
