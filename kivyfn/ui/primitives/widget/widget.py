"""
Behaviors/Background Color
==========================

.. note:: The following classes are intended for in-house use of the library.
"""

from __future__ import annotations

from kivy.lang import Builder
from kivy.metrics import dp
from kivy.uix.widget import Widget
from kivy.properties import (
    ColorProperty,
    ListProperty,
    NumericProperty,
    ReferenceListProperty,
    StringProperty,
    VariableListProperty,
    BoundedNumericProperty,
    DictProperty,
)

from ...behaviors.binder import FnBinder

Builder.load_string(
    """
#:import RelativeLayout kivy.uix.relativelayout.RelativeLayout


<FnWidget>:
    canvas.before:
        # =============================
        # Clear all Previous Instructions
        # =============================
        Clear

        # =============================
        # Transform Layer
        # =============================
        PushMatrix

        # -------- Rotation --------
        Rotate:
            angle: self.angle
            origin: self._background_origin

        # -------- Scale --------
        Scale:
            x: self.scale_value_x
            y: self.scale_value_y
            z: self.scale_value_z
            origin:
                self.center \
                if not self.scale_value_center else \
                self.scale_value_center


        # =============================
        # Shadow / Elevation Layer
        # =============================
        Color:
            rgba: root.shadow_color

        BoxShadow:
            pos: self.pos if not isinstance(self, RelativeLayout) else (0, 0)
            size: self.size
            offset: root.shadow_offset
            spread_radius: -(root.shadow_softness[0]), -(root.shadow_softness[1])
            blur_radius: root.elevation_levels[root.elevation]
            border_radius: root.radius


        # =============================
        # Background Layer
        # =============================
        Color:
            group: "backgroundcolor-behavior-bg-color"
            rgba: self.background_color

        SmoothRoundedRectangle:
            size: self.size
            pos: self.pos if not isinstance(self, RelativeLayout) else (0, 0)
            radius: root.radius
            source: root.background


        # =============================
        # Border Layer
        # =============================
        Color:
            rgba: (0, 0, 0, 0) if self.border_color is None else self.border_color

        SmoothLine:
            width: root.border_width
            rounded_rectangle:
                [ \
                0,
                0, \
                self.width, \
                self.height, \
                *self.radius, \
                ] \
                if isinstance(self, RelativeLayout) else \
                [ \
                self.x,
                self.y, \
                self.width, \
                self.height, \
                *self.radius, \
                ]
    # =============================
    # End Transform
    # =============================
    canvas.after:
        PopMatrix
"""
)


class FnWidget(Widget):
    shadow_color = ColorProperty([0, 0, 0, 0])
    """
    Shadow color.

    :attr:`shadow_color` is a :class:`~kivy.properties.ColorProperty`
    and defaults to `[0, 0, 0, 0]`.
    """

    shadow_softness = VariableListProperty([0, 0], length=2)
    """
    Shadow softness.

    :attr:`shadow_softness` is a :class:`~kivy.properties.NumericProperty`
    and defaults to `0.0`.
    """

    shadow_offset = ListProperty((0, 0))
    """
    shadow offset.
    
    :attr:`shadow_offset` is a :class:`~kivy.properties.ListProperty`
    and defaults to `(0, 0)`."""

    elevation = BoundedNumericProperty(0, min=0, errorvalue=0)
    """
    Elevation level.

    :attr:`elevation` is a :class:`~kivy.properties.BoundedNumericProperty`
    and defaults to `0`.
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

    :attr:`elevation_levels` is a :class:`~kivy.properties.DictProperty`
    and defaults to `{0: 0, 1: dp(8), 2: dp(12), 3: dp(16), 4: dp(20), 5: dp(24)}`.
    """

    background = StringProperty()
    """
    Background image path.

    :attr:`background` is a :class:`~kivy.properties.StringProperty`
    and defaults to `''`.
    """

    background_color = ColorProperty([0, 0, 0, 0])
    """
    Background color.

    :attr:`background_color` is a :class:`~kivy.properties.ColorProperty`
    and defaults to `[0, 0, 0, 0]`.
    """

    border_color = ColorProperty(None, allownone=True)
    """
    If a custom value is specified for the `border_color` parameter, the border
    of the specified color will be used to border the widget:

    :attr:`border_color` is an :class:`~kivy.properties.ColorProperty`
    """

    border_width = NumericProperty(1)
    """
    Border of the specified width will be used to border the widget.

    :attr:`border_width` is an :class:`~kivy.properties.NumericProperty`
    and defaults to `1`.
    """

    radius = VariableListProperty([0], length=4)
    """
    Canvas radius.

    :attr:`radius` is an :class:`~kivy.properties.VariableListProperty`
    and defaults to `[0, 0, 0, 0]`.
    """

    angle = NumericProperty(0)
    """
    Angle of rotation of the widget.

    :attr:`angle` is a :class:`~kivy.properties.NumericProperty`
    and defaults to `0`.
    """

    scale_value_x = NumericProperty(1)
    """
    X-axis scale factor of the widget.

    :attr:`scale_value_x` is a :class:`~kivy.properties.NumericProperty`
    and defaults to `1`.
    """

    scale_value_y = NumericProperty(1)
    """
    Y-axis scale factor of the widget.

    :attr:`scale_value_y` is a :class:`~kivy.properties.NumericProperty`
    and defaults to `1`.
    """

    scale_value_z = NumericProperty(1)
    """
    Z-axis scale factor of the widget.

    :attr:`scale_value_z` is a :class:`~kivy.properties.NumericProperty`
    and defaults to `1`.
    """

    scale_value_center = ListProperty()
    """
    Origin point used for scaling transformations.

    If not specified, the widget's center will be used.

    The format can be either `(x, y)` or `(x, y, z)`.

    :attr:`scale_value_center` is a :class:`~kivy.properties.ListProperty`
    and defaults to `[]`.
    """

    binders: dict[str, FnBinder] = DictProperty()
    """
    Dictionary of binders attached to this widget.

    Binders are reactive helpers declared in kv that subscribe to a store
    address and update the widget when the state changes.

    Each binder may optionally define a ``name``. If a name is provided,
    the binder will be stored in this dictionary and can later be accessed
    or disposed programmatically.

    Example::

        FnLabel:
            FnBinder:
                name: "email"
                field: "text"
                address: "user.email"

    Accessing a binder::

        widget.binders["email"].dispose()

    If a binder does not define a ``name``, it will not be stored in
    :attr:`binders`.

    :attr:`binders` is a :class:`~kivy.properties.DictProperty`
    and defaults to ``{}``.
    """

    background_origin = ListProperty(None)

    _background_x = NumericProperty(0)
    _background_y = NumericProperty(0)
    _background_origin = ReferenceListProperty(_background_x, _background_y)

    def __init__(self, **kwarg):
        super().__init__(**kwarg)
        self.bind(pos=self.update_background_origin)

    def update_background_origin(self, instance, pos: list) -> None:
        """Fired when the values of :attr:`pos` change."""

        if self.background_origin:
            self._background_origin = self.background_origin
        else:
            self._background_origin = self.center

    def add_widget(self, widget, index=0, canvas=None):
        if isinstance(widget, FnBinder):
            widget.owner = self
            return

        return super().add_widget(widget, index, canvas)

    def _register_binder(self, name: str | None, binder: FnBinder):
        if name is None:
            return

        if name in self.binders:
            raise ValueError(f"Binder '{name}' already exists in {self}")

        self.binders[name] = binder
