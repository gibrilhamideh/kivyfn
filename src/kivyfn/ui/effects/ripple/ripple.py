from __future__ import annotations

from typing import Any

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


class FnRippleEffect:
    """
    Visual ripple feedback behavior.

    Requires:
        - FnTouchBehavior
        OR
        - a compatible behavior that dispatches:
            on_press(touch)
            on_release(touch)
            on_cancel(touch)

    This behavior does not handle raw touch events directly.
    """

    ripple_rad_default = NumericProperty(1)
    ripple_color = ColorProperty([1, 1, 1, 1])
    ripple_alpha = NumericProperty(0.5)
    ripple_scale = NumericProperty(None)

    ripple_duration_in_fast = NumericProperty(0.3)
    ripple_duration_in_slow = NumericProperty(2)
    ripple_duration_out = NumericProperty(0.3)

    ripple_canvas_after = BooleanProperty(True)
    ripple_func_in = StringProperty("out_quad")
    ripple_func_out = StringProperty("out_quad")
    ripple_effect = BooleanProperty(True)

    ripple_shape = OptionProperty(
        "rectangular",
        options=("rectangular", "circular"),
    )

    _ripple_radius = NumericProperty(0)
    _ripple_running = BooleanProperty(False)
    _ripple_finishing = BooleanProperty(False)
    _ripple_fading_out = BooleanProperty(False)
    _ripple_border_radius = ListProperty([0, 0, 0, 0])

    _ripple_group = "fn_ripple_behavior"

    def __init__(self, **kwargs: Any) -> None:
        super().__init__(**kwargs)

        self._ripple_local_pos: tuple[float, float] = (0, 0)
        self._ripple_finish_radius: float = 0

        self._ripple_color_instruction: Color | None = None
        self._ripple_ellipse: Ellipse | None = None

        self._ripple_stencil_shape: RoundedRectangle | Ellipse | None = None
        self._ripple_stencil_restore_shape: RoundedRectangle | Ellipse | None = None

        self.bind(  # pyright: ignore
            _ripple_radius=self._update_ripple_geometry,
            ripple_color=self._update_ripple_color,
            pos=self._update_ripple_geometry,
            size=self._update_ripple_geometry,
        )

    # ------------------------------------------------------------------
    # FnWidget lifecycle
    # ------------------------------------------------------------------
    def on_detach(self) -> Any:
        self._reset_ripple()
        super().on_detach() # pyright: ignore

    # ------------------------------------------------------------------
    # FnTouchBehavior event hooks
    # ------------------------------------------------------------------

    def on_press(self, touch: Any) -> Any:
        if self.ripple_effect:
            self.start_ripple_from_touch(touch)

        super_on_press = getattr(super(), "on_press", None)
        if super_on_press is not None:
            return super_on_press(touch)

        return None

    def on_release(self, touch: Any) -> Any:
        self.finish_ripple()

        super_on_release = getattr(super(), "on_release", None)
        if super_on_release is not None:
            return super_on_release(touch)

        return None

    def on_cancel(self, touch: Any) -> Any:
        self.finish_ripple()

        super_on_cancel = getattr(super(), "on_cancel", None)
        if super_on_cancel is not None:
            return super_on_cancel(touch)

        return None

    # ------------------------------------------------------------------
    # Public ripple API
    # ------------------------------------------------------------------

    def start_ripple_from_touch(self, touch: Any) -> None:
        if not self.ripple_effect:
            return

        if (
            self._ripple_running
            or self._ripple_finishing
            or self._ripple_fading_out
        ):
            self._reset_ripple()

        self._ripple_local_pos = (
            touch.x - self.x,  # pyright: ignore
            touch.y - self.y,  # pyright: ignore
        )

        self._ripple_radius = self.ripple_rad_default
        self._ripple_finish_radius = self._compute_finish_radius()

        color = list(self.ripple_color)
        self.ripple_color = [
            color[0],
            color[1],
            color[2],
            self.ripple_alpha,
        ]

        self._lay_canvas_instructions()
        self.start_ripple()

    def start_ripple(self) -> None:
        if self._ripple_running:
            return

        self._ripple_running = True

        anim = Animation(
            _ripple_radius=self._ripple_finish_radius,
            t="linear",
            duration=self.ripple_duration_in_slow,
        )
        anim.bind(on_complete=self.fade_out)
        anim.start(self)

    def finish_ripple(self) -> None:
        if not self._ripple_running:
            return

        if self._ripple_finishing:
            return

        self._ripple_finishing = True
        self._ripple_running = False

        self._ripple_finish_radius = self._compute_finish_radius()

        Animation.cancel_all(self, "_ripple_radius")

        anim = Animation(
            _ripple_radius=self._ripple_finish_radius,
            t=self.ripple_func_in,
            duration=self.ripple_duration_in_fast,
        )
        anim.bind(on_complete=self.fade_out)
        anim.start(self)

    def fade_out(self, *args: Any) -> None:
        if self._ripple_fading_out:
            return

        self._ripple_fading_out = True

        Animation.cancel_all(self, "ripple_color")

        color = list(self.ripple_color)

        anim = Animation(
            ripple_color=[
                color[0],
                color[1],
                color[2],
                0.0,
            ],
            t=self.ripple_func_out,
            duration=self.ripple_duration_out,
        )
        anim.bind(on_complete=self.anim_complete)
        anim.start(self)

    def anim_complete(self, *args: Any) -> None:
        self._ripple_running = False
        self._ripple_finishing = False
        self._ripple_fading_out = False

        self._clear_ripple_canvas()

    # ------------------------------------------------------------------
    # Canvas layout
    # ------------------------------------------------------------------

    def _lay_canvas_instructions(self) -> None:
        if not self.ripple_effect:
            return

        self._clear_ripple_canvas()

        if self.ripple_shape == "circular":
            self._lay_circular_canvas_instructions()
        else:
            self._lay_rectangular_canvas_instructions()

    def _lay_rectangular_canvas_instructions(self) -> None:
        canvas = self._get_ripple_canvas()
        self._ripple_border_radius = self._resolve_border_radius()

        center_x, center_y = self._get_ripple_center()

        with canvas:  # pyright: ignore
            StencilPush(group=self._ripple_group)

            self._ripple_stencil_shape = RoundedRectangle(
                pos=self.pos,  # pyright: ignore
                size=self.size,  # pyright: ignore
                radius=self._ripple_border_radius,
                group=self._ripple_group,
            )

            StencilUse(group=self._ripple_group)

            self._ripple_color_instruction = Color(
                rgba=self.ripple_color,
                group=self._ripple_group,
            )

            self._ripple_ellipse = Ellipse(
                size=(self._ripple_radius, self._ripple_radius),
                pos=(
                    center_x - self._ripple_radius / 2.0,
                    center_y - self._ripple_radius / 2.0,
                ),
                group=self._ripple_group,
            )

            StencilUnUse(group=self._ripple_group)

            self._ripple_stencil_restore_shape = RoundedRectangle(
                pos=self.pos,  # pyright: ignore
                size=self.size,  # pyright: ignore
                radius=self._ripple_border_radius,
                group=self._ripple_group,
            )

            StencilPop(group=self._ripple_group)

    def _lay_circular_canvas_instructions(self) -> None:
        canvas = self._get_ripple_canvas()

        stencil_pos, stencil_size = self._get_circular_stencil_geometry()
        center_x, center_y = self._get_ripple_center()

        with canvas:  # pyright: ignore
            StencilPush(group=self._ripple_group)

            self._ripple_stencil_shape = Ellipse(
                pos=stencil_pos,
                size=stencil_size,
                group=self._ripple_group,
            )

            StencilUse(group=self._ripple_group)

            self._ripple_color_instruction = Color(
                rgba=self.ripple_color,
                group=self._ripple_group,
            )

            self._ripple_ellipse = Ellipse(
                size=(self._ripple_radius, self._ripple_radius),
                pos=(
                    center_x - self._ripple_radius / 2.0,
                    center_y - self._ripple_radius / 2.0,
                ),
                group=self._ripple_group,
            )

            StencilUnUse(group=self._ripple_group)

            self._ripple_stencil_restore_shape = Ellipse(
                pos=stencil_pos,
                size=stencil_size,
                group=self._ripple_group,
            )

            StencilPop(group=self._ripple_group)

    # ------------------------------------------------------------------
    # Geometry updates
    # ------------------------------------------------------------------

    def _update_ripple_geometry(self, *args: Any) -> None:
        if self._ripple_ellipse is None:
            return

        self._update_ripple_ellipse_geometry()
        self._update_ripple_stencil_geometry()

    def _update_ripple_ellipse_geometry(self) -> None:
        if self._ripple_ellipse is None:
            return

        center_x, center_y = self._get_ripple_center()

        self._ripple_ellipse.size = (
            self._ripple_radius,
            self._ripple_radius,
        )

        self._ripple_ellipse.pos = (
            center_x - self._ripple_radius / 2.0,
            center_y - self._ripple_radius / 2.0,
        )

        if (
            self.ripple_shape == "circular"
            and self._ripple_radius > self.width * 0.6  # pyright: ignore
            and not self._ripple_fading_out
        ):
            self.fade_out()

    def _update_ripple_stencil_geometry(self) -> None:
        if self.ripple_shape == "circular":
            self._update_circular_stencil_geometry()
            return

        self._update_rectangular_stencil_geometry()

    def _update_rectangular_stencil_geometry(self) -> None:
        radius = self._resolve_border_radius()

        if self._ripple_stencil_shape is not None:
            self._ripple_stencil_shape.pos = self.pos  # pyright: ignore
            self._ripple_stencil_shape.size = self.size  # pyright: ignore
            self._ripple_stencil_shape.radius = radius  # pyright: ignore

        if self._ripple_stencil_restore_shape is not None:
            self._ripple_stencil_restore_shape.pos = self.pos  # pyright: ignore
            self._ripple_stencil_restore_shape.size = self.size  # pyright: ignore
            self._ripple_stencil_restore_shape.radius = radius  # pyright: ignore

    def _update_circular_stencil_geometry(self) -> None:
        stencil_pos, stencil_size = self._get_circular_stencil_geometry()

        if self._ripple_stencil_shape is not None:
            self._ripple_stencil_shape.pos = stencil_pos
            self._ripple_stencil_shape.size = stencil_size

        if self._ripple_stencil_restore_shape is not None:
            self._ripple_stencil_restore_shape.pos = stencil_pos
            self._ripple_stencil_restore_shape.size = stencil_size

    def _update_ripple_color(self, instance: Any, value: list[float]) -> None:
        if self._ripple_color_instruction is None:
            return

        self._ripple_color_instruction.rgba = value # pyright: ignore

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    def _get_ripple_center(self) -> tuple[float, float]:
        if self.ripple_shape == "circular":
            return (
                self.center_x,  # pyright: ignore
                self.center_y,  # pyright: ignore
            )

        return (
            self.x + self._ripple_local_pos[0],  # pyright: ignore
            self.y + self._ripple_local_pos[1],  # pyright: ignore
        )

    def _get_circular_stencil_geometry(
        self,
    ) -> tuple[tuple[float, float], tuple[float, float]]:
        scale = self._get_effective_ripple_scale()

        stencil_width = self.width * scale  # pyright: ignore
        stencil_height = self.height * scale  # pyright: ignore

        stencil_pos = (
            self.center_x - stencil_width / 2.0,  # pyright: ignore
            self.center_y - stencil_height / 2.0,  # pyright: ignore
        )

        return stencil_pos, (stencil_width, stencil_height)

    def _compute_finish_radius(self) -> float:
        scale = self._get_effective_ripple_scale()
        return max(self.width, self.height) * scale  # pyright: ignore

    def _get_effective_ripple_scale(self) -> float:
        if self.ripple_scale is not None:
            return self.ripple_scale

        if self.ripple_shape == "circular":
            return 1.0

        return 2.75

    def _get_ripple_canvas(self) -> Any:
        if self.ripple_canvas_after:
            return self.canvas.after  # pyright: ignore

        return self.canvas.before  # pyright: ignore

    def _clear_ripple_canvas(self) -> None:
        self.canvas.before.remove_group(self._ripple_group)  # pyright: ignore
        self.canvas.after.remove_group(self._ripple_group)  # pyright: ignore

        self._ripple_color_instruction = None
        self._ripple_ellipse = None
        self._ripple_stencil_shape = None
        self._ripple_stencil_restore_shape = None

    def _reset_ripple(self) -> None:
        Animation.cancel_all(
            self,
            "_ripple_radius",
            "ripple_color",
        )

        self._ripple_running = False
        self._ripple_finishing = False
        self._ripple_fading_out = False

        self._clear_ripple_canvas()

    def _resolve_border_radius(self) -> list[Any]:
        radius = getattr(self, "radius", [0, 0, 0, 0])

        if isinstance(radius, (int, float)):
            return [radius]

        return list(radius)
