from kivy.properties import NumericProperty


class FnTranslateBehavior:
    """
    Behavior that applies a translation transformation to a widget.
    """

    translate_x = NumericProperty(0)
    """
    Horizontal translation.

    :attr:`translate_x` is a :class:`~kivy.properties.NumericProperty`
    and defaults to ``0``.
    """

    translate_y = NumericProperty(0)
    """
    Vertical translation.

    :attr:`translate_y` is a :class:`~kivy.properties.NumericProperty`
    and defaults to ``0``.
    """

    translate_z = NumericProperty(0)
    """
    Z-axis translation.

    :attr:`translate_z` is a :class:`~kivy.properties.NumericProperty`
    and defaults to ``0``.
    """
