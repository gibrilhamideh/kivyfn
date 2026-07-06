from kivy.properties import (
    ColorProperty,
    StringProperty,
    VariableListProperty,
)


class FnBackgroundBehavior:
    """
    Behavior that adds a background color to a widget.

    The background automatically follows the widget's
    position and size.

    Example::

        FnWidget:
            background_color: 0.2, 0.2, 0.2, 1
    """

    bg_color = ColorProperty((0, 0, 0, 0))
    """
    Background color of the widget.

    :attr:`background_color` is a :class:`~kivy.properties.ColorProperty`
    and defaults to `(0, 0, 0, 0)` (transparent).
    """

    bg = StringProperty("")
    """
    Background texture source of the widget.

    The value should be a path to an image file that will be used as the
    background texture.

    Example::

        FnWidget:
            bg: "images/background.png"

    If the value is an empty string (default), no background image will be
    used and only the background color will be rendered.

    :attr:`background` is a :class:`~kivy.properties.StringProperty`
    and defaults to ``""``.
    """

    radius = VariableListProperty([0], length=4)
    """
    Radius of the widget's corners.

    The value should contain four numbers representing the radius
    of each corner in the following order::

        (top_left, top_right, bottom_right, bottom_left)

    These values are used by canvas instructions that support
    rounded rectangles such as ``SmoothRoundedRectangle`` and
    ``SmoothLine``.

    Example::

        FnWidget:
            radius: 12, 12, 12, 12

    :attr:`radius` is a :class:`~kivy.properties.ListProperty`
    and defaults to ``(0, 0, 0, 0)``.
    """
