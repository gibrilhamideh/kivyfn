from kivy.properties import VariableListProperty


class FnClipBehavior:
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
