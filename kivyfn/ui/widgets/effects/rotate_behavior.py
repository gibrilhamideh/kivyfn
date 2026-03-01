
__all__ = ("RotateBehavior",)

from kivy.lang import Builder
from kivy.properties import ListProperty, NumericProperty

Builder.load_string(
    """
<RotateBehavior>
    canvas.before:
        PushMatrix
        Rotate:
            angle: self.rotate_value_angle
            axis: tuple(self.rotate_value_axis)
            origin: self.center
    canvas.after:
        PopMatrix
"""
)


class RotateBehavior:
    """Base class for controlling the rotate of the widget."""

    rotate_value_angle = NumericProperty(0)
    """
    Property for getting/setting the angle of the rotation.

    :attr:`rotate_value_angle` is an :class:`~kivy.properties.NumericProperty`
    and defaults to `0`.
    """

    rotate_value_axis = ListProperty((0, 0, 1))
    """
    Property for getting/setting the axis of the rotation.

    :attr:`rotate_value_axis` is an :class:`~kivy.properties.ListProperty`
    and defaults to `(0, 0, 1)`.
    """
