from kivy.lang import Builder
from kivy.metrics import dp
from kivy.properties import (
    ColorProperty,
    StringProperty,
    VariableListProperty,
    DictProperty,
    ListProperty,
    BoundedNumericProperty,
)

Builder.load_string(
    """
<FnBackgroundBehavior>
    canvas.before:

        Color:
            rgba: root.shadow_color

        BoxShadow:
            pos: root.pos if not isinstance(root, RelativeLayout) else (0, 0)
            size: root.size
            offset: root.shadow_offset
            spread_radius: -(root.shadow_softness[0]), -(root.shadow_softness[1])
            blur_radius: root.elevation_levels[root.elevation]
            border_radius: root.radius

        Color:
            rgba: root.background_color

        SmoothRoundedRectangle:
            size: root.size
            pos: root.pos if not isinstance(root, RelativeLayout) else (0, 0)
            radius: root.radius
            source: root.background
"""
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

    background_color = ColorProperty((0, 0, 0, 0))
    """
    Background color of the widget.

    :attr:`background_color` is a :class:`~kivy.properties.ColorProperty`
    and defaults to `(0, 0, 0, 0)` (transparent).
    """

    background = StringProperty("")
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

    shadow_color = ColorProperty([0, 0, 0, 0])
    """
    Shadow color.

    Controls the color and opacity of the widget's shadow.

    :attr:`shadow_color` is a :class:`~kivy.properties.ColorProperty`
    and defaults to ``[0, 0, 0, 0]``.
    """

    shadow_softness = VariableListProperty([0, 0], length=2)
    """
    Shadow softness.

    Controls how much the shadow spreads horizontally and vertically.
    These values are typically used to soften the shadow edges.

    :attr:`shadow_softness` is a :class:`~kivy.properties.VariableListProperty`
    with a length of ``2`` and defaults to ``[0, 0]``.
    """

    shadow_offset = ListProperty((0, 0))
    """
    Shadow offset.

    Defines the horizontal and vertical displacement of the shadow
    relative to the widget.

    :attr:`shadow_offset` is a :class:`~kivy.properties.ListProperty`
    and defaults to ``(0, 0)``.
    """

    elevation = BoundedNumericProperty(0, min=0, errorvalue=0)
    """
    Elevation level.

    Represents the visual elevation of the widget. Higher elevation
    values typically produce larger and softer shadows.

    :attr:`elevation` is a :class:`~kivy.properties.BoundedNumericProperty`
    with a minimum value of ``0`` and defaults to ``0``.
    """

    elevation_levels = DictProperty(
        {
            0: 0,
            1: dp(4),
            2: dp(8),
            3: dp(12),
            4: dp(16),
            5: dp(20),
            6: dp(24),
        }
    )
    """
    Elevation levels.

    Maps elevation values to the blur radius used for the shadow.

    :attr:`elevation_levels` is a :class:`~kivy.properties.DictProperty`
    and defaults to::

        {
            0: 0,
            1: dp(4),
            2: dp(8),
            3: dp(12),
            4: dp(16),
            5: dp(20),
            6: dp(24),
        }
    """
