from __future__ import annotations

from kivy.animation import Animation
from kivy.graphics import (
    Color,
    Ellipse,
    StencilPop,
    StencilPush,
    StencilUnUse,
    StencilUse,
)
from kivy.graphics.vertex_instructions import RoundedRectangle
from kivy.properties import (
    BooleanProperty,
    ColorProperty,
    ListProperty,
    NumericProperty,
    OptionProperty,
    StringProperty,
)


class FnRippleBehavior:
    """
    A unified, single-class ripple effect supporting both rectangular and
    circular constraints, built for stability and clean canvas management.
    """

    ripple_enabled = BooleanProperty(True)

    # Easily switch between rectangle and circle masks!
    ripple_mode = OptionProperty("rectangle", options=("rectangle", "circle"))

    ripple_canvas_after = BooleanProperty(True)

    ripple_color = ColorProperty(None, allownone=True)
    ripple_alpha = NumericProperty(0.15)
    ripple_scale = NumericProperty(1.0)

    # Durations from KivyMD
    ripple_duration_in_fast = NumericProperty(0.3)
    ripple_duration_in_slow = NumericProperty(2.0)
    ripple_duration_out = NumericProperty(0.3)

    ripple_func_in = StringProperty("out_quad")
    ripple_func_out = StringProperty("out_quad")

    # Animation properties used internally
    _ripple_rad = NumericProperty(0.0)
    _ripple_color_anim = ListProperty([0, 0, 0, 0])

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._ripple_origin = (0.0, 0.0)

        # State tracking flags
        self._doing_ripple = False
        self._finishing_ripple = False
        self._fading_out = False

        self._ripple_color_instruction = None
        self._ripple_instruction = None

    # =========================================================================
    # Touch Handling
    # =========================================================================

    def on_touch_down(self, touch):
        if getattr(touch, "is_mouse_scrolling", False):
            return super().on_touch_down(touch)

        if not self.collide_point(*touch.pos):
            return super().on_touch_down(touch)

        if self.ripple_enabled and not getattr(self, "disabled", False):
            self.start_ripple(touch.pos)

        return super().on_touch_down(touch)

    def on_touch_move(self, touch):
        if not self.collide_point(*touch.pos):
            if self._doing_ripple and not self._finishing_ripple:
                self.finish_ripple()
        return super().on_touch_move(touch)

    def on_touch_up(self, touch):
        if self.collide_point(*touch.pos) and self._doing_ripple:
            self.finish_ripple()
        return super().on_touch_up(touch)

    # =========================================================================
    # Ripple Lifecycle Methods
    # =========================================================================

    def start_ripple(self, pos: tuple[float, float]) -> None:
        self._cancel_all_ripple_animations()
        self._clear_ripple_canvas()

        self._doing_ripple = True
        self._finishing_ripple = False
        self._fading_out = False

        self._ripple_origin = pos
        self._ripple_rad = 1.0

        self._create_ripple_instructions()
        self._update_ripple_graphics()

        target_size = self._get_target_size()

        # Start the slow "holding down" animation
        anim = Animation(
            _ripple_rad=target_size,
            t="linear",
            duration=self.ripple_duration_in_slow,
        )
        anim.start(self)

    def finish_ripple(self) -> None:
        if not self._doing_ripple or self._finishing_ripple:
            return

        self._finishing_ripple = True
        self._doing_ripple = False

        Animation.cancel_all(self, "_ripple_rad")

        target_size = self._get_target_size()

        # Snap quickly to the target size when user lifts their finger
        anim = Animation(
            _ripple_rad=target_size,
            t=self.ripple_func_in,
            duration=self.ripple_duration_in_fast,
        )
        anim.bind(on_complete=lambda *_: self._fade_out())
        anim.start(self)

    def _fade_out(self) -> None:
        if self._fading_out or self._ripple_color_instruction is None:
            return

        self._fading_out = True
        Animation.cancel_all(self, "_ripple_color_anim")

        r, g, b, _ = self._ripple_color_anim

        anim = Animation(
            _ripple_color_anim=[r, g, b, 0.0],
            t=self.ripple_func_out,
            duration=self.ripple_duration_out,
        )
        anim.bind(on_complete=lambda *_: self._end_ripple())
        anim.start(self)

    def _end_ripple(self) -> None:
        self._cancel_all_ripple_animations()
        self._clear_ripple_canvas()
        self._doing_ripple = False
        self._finishing_ripple = False
        self._fading_out = False

    # =========================================================================
    # Canvas Construction & Stencils
    # =========================================================================

    def _create_ripple_instructions(self) -> None:
        canvas = self.canvas.after if self.ripple_canvas_after else self.canvas.before

        # Determine the color to use
        rgba = self._get_ripple_color()
        self._ripple_color_anim = rgba  # Initialize internal color property

        with canvas:
            StencilPush(group="fn_unified_ripple")

            self._draw_clip_shape()

            StencilUse(group="fn_unified_ripple")

            self._ripple_color_instruction = Color(*rgba, group="fn_unified_ripple")

            # The expanding ripple is ALWAYS a circle
            self._ripple_instruction = Ellipse(
                pos=(0, 0),
                size=(0, 0),
                group="fn_unified_ripple",
            )

            StencilUnUse(group="fn_unified_ripple")

            self._draw_clip_shape()

            StencilPop(group="fn_unified_ripple")

    def _draw_clip_shape(self) -> None:
        """Draws the boundaries that clip the growing circular ripple."""
        if self.ripple_mode == "circle":
            # Creates a circular boundary in the exact center
            diameter = min(self.width, self.height) * self.ripple_scale
            Ellipse(
                pos=(self.center_x - diameter / 2.0, self.center_y - diameter / 2.0),
                size=(diameter, diameter),
                group="fn_unified_ripple",
            )
        else:
            # Creates a rectangular boundary matching the widget's box
            radius = getattr(self, "radius", [0, 0, 0, 0])
            if isinstance(radius, (int, float)):
                radius = [radius] * 4

            RoundedRectangle(
                pos=self.pos,
                size=self.size,
                radius=radius,
                group="fn_unified_ripple",
            )

    def _clear_ripple_canvas(self) -> None:
        canvas = self.canvas.after if self.ripple_canvas_after else self.canvas.before
        canvas.remove_group("fn_unified_ripple")
        self._ripple_color_instruction = None
        self._ripple_instruction = None

    def _cancel_all_ripple_animations(self) -> None:
        Animation.cancel_all(self, "_ripple_rad", "_ripple_color_anim")

    # =========================================================================
    # Property Listeners & Geometry Math
    # =========================================================================

    def on__ripple_rad(self, *_):
        self._update_ripple_graphics()

    def on__ripple_color_anim(self, *_):
        if self._ripple_color_instruction:
            self._ripple_color_instruction.rgba = self._ripple_color_anim

    def _update_ripple_graphics(self) -> None:
        if self._ripple_instruction is None:
            return

        rad = self._ripple_rad
        x, y = self._ripple_origin

        self._ripple_instruction.size = (rad, rad)
        self._ripple_instruction.pos = (x - rad / 2.0, y - rad / 2.0)

    def _get_target_size(self) -> float:
        """Calculates how big the circle needs to grow to cover the whole mask."""
        if self.ripple_mode == "circle":
            return max(self.width, self.height) * self.ripple_scale * 2.0

        # For rectangle, find the distance to the furthest corner to ensure full coverage
        x, y = self._ripple_origin
        corners = (
            (self.x, self.y),
            (self.right, self.y),
            (self.x, self.top),
            (self.right, self.top),
        )
        max_dist_sq = max((cx - x) ** 2 + (cy - y) ** 2 for cx, cy in corners)
        return max_dist_sq**0.5 * 2.0

    def _get_ripple_color(self) -> list[float]:
        """Safely retrieves the intended ripple color, handling 'the theme thing'."""
        if self.ripple_color:
            color = list(self.ripple_color)
            color[3] = self.ripple_alpha
            return color

        # Fallback to a nice generic gray if no theme is found
        return [0.7, 0.7, 0.7, self.ripple_alpha]
