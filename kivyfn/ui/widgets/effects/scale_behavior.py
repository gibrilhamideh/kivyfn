

__all__ = ("ScaleBehavior",)

from kivy.lang import Builder
from kivy.properties import ListProperty, NumericProperty

Builder.load_string(
    """
<ScaleBehavior>
    canvas.before:
        PushMatrix
        Scale:
            x: self.scale_value_x
            y: self.scale_value_y
            z: self.scale_value_z
            origin:
                self.center \
                if not self.scale_value_center else \
                self.scale_value_center
    canvas.after:
        PopMatrix
"""
)


class ScaleBehavior:
    """Base class for controlling the scale of the widget."""

    scale_value_x = NumericProperty(1)
    """
    X-axis value.

    :attr:`scale_value_x` is an :class:`~kivy.properties.NumericProperty`
    and defaults to `1`.
    """

    scale_value_y = NumericProperty(1)
    """
    Y-axis value.

    :attr:`scale_value_y` is an :class:`~kivy.properties.NumericProperty`
    and defaults to `1`.
    """

    scale_value_z = NumericProperty(1)
    """
    Z-axis value.

    :attr:`scale_value_z` is an :class:`~kivy.properties.NumericProperty`
    and defaults to `1`.
    """

    scale_value_center = ListProperty()
    """
    Origin of the scale.

    .. versionadded:: 1.2.0

    The format of the origin can be either (x, y) or (x, y, z).

    :attr:`scale_value_center` is an :class:`~kivy.properties.NumericProperty`
    and defaults to `[]`.
    """
