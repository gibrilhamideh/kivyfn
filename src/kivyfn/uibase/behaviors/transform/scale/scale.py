from kivy.properties import ListProperty, NumericProperty


class FnScaleBehavior:
    """
    Behavior that allows scaling a widget along the X, Y, and Z axes.
    """

    scale_x = NumericProperty(1)
    """
    Scale factor along the X-axis.

    :attr:`scale_x` is a :class:`~kivy.properties.NumericProperty`
    and defaults to ``1``.
    """

    scale_y = NumericProperty(1)
    """
    Scale factor along the Y-axis.

    :attr:`scale_y` is a :class:`~kivy.properties.NumericProperty`
    and defaults to ``1``.
    """

    scale_z = NumericProperty(1)
    """
    Scale factor along the Z-axis.

    :attr:`scale_z` is a :class:`~kivy.properties.NumericProperty`
    and defaults to ``1``.
    """

    scale_center = ListProperty()
    """
    Origin point of the scaling transformation.

    If empty, the widget's center is used.

    The format can be either::

        (x, y)
        (x, y, z)

    :attr:`scale_center` is a :class:`~kivy.properties.ListProperty`
    and defaults to ``[]``.
    """
