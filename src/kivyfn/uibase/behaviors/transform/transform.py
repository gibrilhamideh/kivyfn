from kivy.lang import Builder
from kivy.properties import (
    NumericProperty,
    ListProperty,
)

Builder.load_string(
    """
<FnTransformBehavior>
    canvas.before:
        PushMatrix

        Translate:
            x: root.translate_x
            y: root.translate_y
            z: root.translate_z

        Rotate:
            angle: root.rotate_angle
            axis: tuple(root.rotate_axis)
            origin:
                root.center \
                if not root.rotate_center else \
                root.rotate_center

        Scale:
            x: root.scale_x
            y: root.scale_y
            z: root.scale_z
            origin:
                root.center \
                if not root.scale_center else \
                root.scale_center

    canvas.after:
        PopMatrix
"""
)


class FnTransformBehavior:
    """
    Behavior that provides translation, rotation, and scaling
    transformations for a widget.

    All transformations are applied using a single matrix stack
    to ensure proper composition of transforms.
    """

    # ----------------------------------
    # Translation
    # ----------------------------------

    translate_x = NumericProperty(0)
    """
    Horizontal canvas translation.

    :attr:`translate_x` is a :class:`~kivy.properties.NumericProperty`
    and defaults to ``0``.
    """

    translate_y = NumericProperty(0)
    """
    Vertical canvas translation.

    :attr:`translate_y` is a :class:`~kivy.properties.NumericProperty`
    and defaults to ``0``.
    """

    translate_z = NumericProperty(0)
    """
    Z-axis translation.

    :attr:`translate_z` is a :class:`~kivy.properties.NumericProperty`
    and defaults to ``0``.
    """

    # ----------------------------------
    # Rotation
    # ----------------------------------

    rotate_angle = NumericProperty(0)
    """
    Rotation angle in degrees.

    :attr:`rotate_angle` is a :class:`~kivy.properties.NumericProperty`
    and defaults to ``0``.
    """

    rotate_axis = ListProperty((0, 0, 1))
    """
    Rotation axis vector ``(x, y, z)``.

    :attr:`rotate_axis` is a :class:`~kivy.properties.ListProperty`
    and defaults to ``(0, 0, 1)``.
    """

    rotate_center = ListProperty()
    """
    Origin point of the rotation.

    If empty, the widget's center is used.

    :attr:`rotate_center` is a :class:`~kivy.properties.ListProperty`
    and defaults to ``[]``.
    """

    # ----------------------------------
    # Scaling
    # ----------------------------------

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

    scale_center = ListProperty([0, 0, 0])
    """
    Origin point of the scaling transformation.

    If empty, the widget's center is used.

    :attr:`scale_center` is a :class:`~kivy.properties.VariableListProperty`
    and defaults to ``[]``.
    """
