from kivy.properties import ListProperty, NumericProperty


class FnRotateBehavior:
    """
    Behavior that applies a rotation transformation to a widget.
    """

    rotate_angle = NumericProperty(0)
    """
    Rotation angle in degrees.

    :attr:`rotate_angle` is a :class:`~kivy.properties.NumericProperty`
    and defaults to ``0``.
    """

    rotate_axis = ListProperty((0, 0, 1))
    """
    Rotation axis.

    The axis is defined as a vector ``(x, y, z)``.

    :attr:`rotate_axis` is a :class:`~kivy.properties.ListProperty`
    and defaults to ``(0, 0, 1)``.
    """

    rotate_center = ListProperty()
    """
    Origin point of the rotation.

    If empty, the widget's center is used.

    The format can be either::

        (x, y)
        (x, y, z)

    :attr:`rotate_center` is a :class:`~kivy.properties.ListProperty`
    and defaults to ``[]``.
    """
