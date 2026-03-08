from kivy.lang import Builder
from kivy.properties import ColorProperty, NumericProperty, VariableListProperty

Builder.load_string(
    """
<FnBorderBehavior>
    canvas.before:
        Color:
            rgba: (0, 0, 0, 0) if root.border_color is None else root.border_color

        SmoothLine:
            width: root.border_width
            rounded_rectangle:
                [ \
                0, \
                0, \
                root.width, \
                root.height, \
                *root.radius \
                ] \
                if isinstance(root, RelativeLayout) else \
                [ \
                root.x, \
                root.y, \
                root.width, \
                root.height, \
                *root.radius \
                ]
"""
)


class FnBorderBehavior:
    """
    Behavior that adds a rounded border to a widget.

    The border automatically follows the widget's position and size.
    The radius can be shared with other behaviors (such as
    :class:`FnBackgroundBehavior`) to ensure consistent rounding.

    Example::

        FnWidget:
            border_color: 1, 1, 1, 1
            border_width: 2
            radius: 10, 10, 10, 10
    """

    border_color = ColorProperty(None, allownone=True)
    """
    Color of the border.

    If ``None`` (default), the border will not be rendered.

    :attr:`border_color` is a :class:`~kivy.properties.ColorProperty`
    and defaults to ``None``.
    """

    border_width = NumericProperty(1)
    """
    Width of the border line in pixels.

    :attr:`border_width` is a :class:`~kivy.properties.NumericProperty`
    and defaults to ``1``.
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
