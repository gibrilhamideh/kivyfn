from __future__ import annotations

from collections.abc import Iterable, Iterator
from contextlib import contextmanager
from math import hypot
from typing import Any

from kivy.clock import Clock
from kivy.core.text import Label as CoreLabel
from kivy.graphics import (
    Color,
    Ellipse,
    InstructionGroup,
    Line,
    Rectangle,
)
from kivy.properties import (
    BooleanProperty,
    ColorProperty,
    NumericProperty,
    ObjectProperty,
    StringProperty,
    VariableListProperty,
)

from kivyfn.factory import load_kv
from kivyfn.ui.layouts.relativelayout import FnRelativeLayout

from .axis import ChartAxis, LinearAxis
from .axis.range import resolve_domain
from .axis.tick import locate_ticks
from .data import NormalizedData
from .errors import (
    ChartAxisError,
    ChartConfigurationError,
    ChartError,
    ChartRenderError,
    ChartSeriesError,
)
from .geometry import ChartBounds
from .interaction import (
    ChartInteraction,
    ChartInteractionController,
    ChartSelection,
    SelectedPoint,
)
from .interaction.hit import nearest_x
from .legend import ChartLegend
from .renderer import LineRenderer, RenderContext, SeriesRenderer
from .renderer.layer import ChartLayers
from .series import ChartSeries
from .tooltip import ChartTooltip
from .types import ChartValue, RenderQuality
from .viewport import ChartViewport


load_kv(__file__)


_SERIES_PALETTE = (
    (0.30, 0.63, 1.00, 1.0),
    (0.73, 0.60, 1.00, 1.0),
    (0.35, 0.80, 0.58, 1.0),
    (1.00, 0.61, 0.38, 1.0),
    (0.97, 0.42, 0.55, 1.0),
    (0.33, 0.82, 0.86, 1.0),
    (0.88, 0.73, 0.46, 1.0),
    (0.66, 0.72, 0.86, 1.0),
)


class FnChart(FnRelativeLayout):
    """Interactive Cartesian chart supporting independently timed series."""

    background_color = ColorProperty((0.09, 0.11, 0.18, 1))
    plot_background_color = ColorProperty((0.04, 0.06, 0.12, 1))
    grid_color = ColorProperty((0.55, 0.60, 0.65, 0.18))
    axis_color = ColorProperty((0.55, 0.60, 0.65, 0.55))
    text_color = ColorProperty((0.90, 0.93, 1.00, 1))
    crosshair_color = ColorProperty((0.90, 0.93, 1.00, 0.65))
    selection_color = ColorProperty((1, 1, 1, 1))

    padding = VariableListProperty([58, 18, 28, 42], length=4)
    legend_enabled = BooleanProperty(True)
    tooltip_enabled = BooleanProperty(True)
    max_render_points = NumericProperty(4000)
    empty_text = StringProperty("No data")

    interaction = ObjectProperty(None, allownone=True)
    viewport = ObjectProperty(None, allownone=True)
    selection = ObjectProperty(None, allownone=True)

    __events__ = (
        "on_selection",
        "on_viewport",
        "on_chart_error",
        "on_render",
    )

    def __init__(
        self,
        *,
        axes: Iterable[ChartAxis] | None = None,
        series: Iterable[ChartSeries] | None = None,
        interaction: ChartInteraction | None = None,
        viewport: ChartViewport | None = None,
        **kwargs: Any,
    ) -> None:
        self._axes: dict[str, ChartAxis] = {}
        self._series: list[ChartSeries] = []
        self._normalized: dict[str, NormalizedData] = {}
        self._renderers: dict[str, SeriesRenderer] = {
            "line": LineRenderer(),
        }
        self._quality: RenderQuality = "final"
        self._update_depth = 0
        self._update_dirty = False
        self._rendering = False
        self._plot_bounds = ChartBounds(0, 0, 0, 0)

        super().__init__(**kwargs)

        self.interaction = interaction or ChartInteraction()
        self.viewport = viewport or ChartViewport()
        self._layers = ChartLayers(self.canvas)
        self._interaction_controller = ChartInteractionController(self)
        self._render_trigger = Clock.create_trigger(self._render, -1)

        self._tooltip = ChartTooltip()
        self._legend = ChartLegend(self)
        self.add_widget(self._tooltip)
        self.add_widget(self._legend)

        configured_axes = axes or (
            LinearAxis(id="x", side="bottom"),
            LinearAxis(id="y", side="left"),
        )

        with self.update():
            for axis in configured_axes:
                self.add_axis(axis)

            for item in series or ():
                self.add_series(item)

        properties = (
            "size",
            "background_color",
            "plot_background_color",
            "grid_color",
            "axis_color",
            "text_color",
            "crosshair_color",
            "selection_color",
            "padding",
            "legend_enabled",
            "tooltip_enabled",
            "max_render_points",
            "empty_text",
        )
        for name in properties:
            self.fbind(name, self._on_visual_change)

        self.request_render()

    @property
    def axes(self) -> tuple[ChartAxis, ...]:
        return tuple(self._axes.values())

    @property
    def series(self) -> tuple[ChartSeries, ...]:
        return tuple(self._series)

    @property
    def plot_bounds(self) -> ChartBounds:
        return self._plot_bounds

    def add_axis(self, axis: ChartAxis) -> None:
        if not isinstance(axis, ChartAxis):
            raise TypeError(
                "FnChart.add_axis requires a ChartAxis instance"
            )

        if axis.id in self._axes:
            raise ChartAxisError(f"Axis {axis.id!r} already exists")

        horizontal = axis.side in {"bottom", "top"}
        if axis.kind == "datetime" and not horizontal:
            raise ChartAxisError(
                "Datetime axes are currently supported only on the "
                "horizontal dimension"
            )

        if horizontal and self._horizontal_axes():
            raise ChartAxisError(
                "FnChart currently supports one horizontal axis"
            )

        for existing in self._axes.values():
            if existing.side == axis.side:
                raise ChartAxisError(
                    f"Axis side {axis.side!r} is already used by "
                    f"{existing.id!r}"
                )

        self._axes[axis.id] = axis
        self.request_render()

    def get_axis(self, axis_id: str) -> ChartAxis:
        try:
            return self._axes[axis_id]
        except KeyError as error:
            raise ChartAxisError(
                f"Chart axis {axis_id!r} does not exist"
            ) from error

    def remove_axis(self, axis_id: str) -> ChartAxis:
        for item in self._series:
            if axis_id in {item.x_axis, item.y_axis}:
                raise ChartAxisError(
                    f"Cannot remove axis {axis_id!r}; series "
                    f"{item.id!r} still uses it"
                )

        try:
            axis = self._axes.pop(axis_id)
        except KeyError as error:
            raise ChartAxisError(
                f"Chart axis {axis_id!r} does not exist"
            ) from error

        self.request_render()
        return axis

    def add_series(self, series: ChartSeries) -> None:
        if not isinstance(series, ChartSeries):
            raise TypeError(
                "FnChart.add_series requires a ChartSeries instance"
            )

        if any(item.id == series.id for item in self._series):
            raise ChartSeriesError(
                f"Series {series.id!r} already exists"
            )

        self.get_axis(series.x_axis)
        self.get_axis(series.y_axis)

        if series.kind not in self._renderers:
            raise ChartSeriesError(
                f"No renderer is registered for series kind "
                f"{series.kind!r}"
            )

        series.subscribe(self._on_series_change)
        self._series.append(series)
        self.request_render()

    def get_series(self, series_id: str) -> ChartSeries:
        for item in self._series:
            if item.id == series_id:
                return item

        raise ChartSeriesError(
            f"Chart series {series_id!r} does not exist"
        )

    def remove_series(self, series_id: str) -> ChartSeries:
        series = self.get_series(series_id)
        series.unsubscribe(self._on_series_change)
        self._series.remove(series)
        self._normalized.pop(series.id, None)

        if self.selection is not None:
            self.clear_selection()

        self.request_render()
        return series

    def clear_series(self) -> None:
        if not self._series:
            return

        with self.update():
            for series in tuple(self._series):
                self.remove_series(series.id)

    def show_series(self, series_id: str) -> None:
        series = self.get_series(series_id)
        if not series.visible:
            series.visible = True
            series.notify_changed()

    def hide_series(self, series_id: str) -> None:
        series = self.get_series(series_id)
        if series.visible:
            series.visible = False
            series.notify_changed()

    def toggle_series(self, series_id: str) -> None:
        series = self.get_series(series_id)
        series.visible = not series.visible
        series.notify_changed()

    def color_for_series(
        self,
        series: ChartSeries,
    ) -> tuple[float, float, float, float]:
        if series.color is not None:
            return series.color

        index = self._series.index(series)
        return _SERIES_PALETTE[index % len(_SERIES_PALETTE)]

    @contextmanager
    def update(self) -> Iterator[FnChart]:
        self._update_depth += 1

        try:
            yield self
        finally:
            self._update_depth -= 1

            if self._update_depth == 0 and self._update_dirty:
                self._update_dirty = False
                self.request_render()

    def request_render(self, *_: Any) -> None:
        if self._update_depth:
            self._update_dirty = True
            return

        if hasattr(self, "_render_trigger"):
            self._render_trigger()

    def render_now(self) -> None:
        self._render_trigger.cancel()
        self._render(0)

    def fit(self) -> None:
        self.reset_viewport()

    def reset_viewport(self) -> None:
        self.viewport.reset()
        self._quality = "final"
        self.dispatch("on_viewport", self.viewport)
        self.request_render()

    def pan_pixels(self, delta_x: float, delta_y: float) -> None:
        mode = self.interaction.pan
        bounds = self.plot_bounds

        if mode in {"x", "both"} and bounds.width > 0:
            for axis in self._horizontal_axes():
                lower, upper = axis.scale.scalar_domain
                shift = -delta_x / bounds.width * (upper - lower)
                self.viewport.set_x(
                    axis.scale.from_scalar(lower + shift),
                    axis.scale.from_scalar(upper + shift),
                )

        if mode in {"y", "both"} and bounds.height > 0:
            for axis in self._vertical_axes():
                lower, upper = axis.scale.scalar_domain
                shift = -delta_y / bounds.height * (upper - lower)
                self.viewport.set_y(
                    axis.id,
                    lower + shift,
                    upper + shift,
                )

        self._quality = "interactive"
        self.dispatch("on_viewport", self.viewport)
        self.request_render()

    def zoom_at(
        self,
        x: float,
        y: float,
        factor: float,
    ) -> None:
        if factor <= 0:
            return

        local_x, local_y = self.to_local(x, y)
        bounds = self.plot_bounds
        mode = self.interaction.zoom

        if mode in {"x", "both"} and bounds.width > 0:
            ratio = (local_x - bounds.left) / bounds.width

            for axis in self._horizontal_axes():
                lower, upper = axis.scale.scalar_domain
                new_lower, new_upper = _zoom_domain(
                    lower,
                    upper,
                    ratio,
                    factor,
                )
                self.viewport.set_x(
                    axis.scale.from_scalar(new_lower),
                    axis.scale.from_scalar(new_upper),
                )

        if mode in {"y", "both"} and bounds.height > 0:
            ratio = (local_y - bounds.bottom) / bounds.height

            for axis in self._vertical_axes():
                lower, upper = axis.scale.scalar_domain
                new_lower, new_upper = _zoom_domain(
                    lower,
                    upper,
                    ratio,
                    factor,
                )
                self.viewport.set_y(axis.id, new_lower, new_upper)

        self._quality = "interactive"
        self.dispatch("on_viewport", self.viewport)
        self.request_render()

    def finish_interaction(self) -> None:
        self._quality = "final"
        self.request_render()

    def is_plot_point(self, x: float, y: float) -> bool:
        local = self.to_local(x, y)
        return self.plot_bounds.contains(*local)

    def activate_at(self, x: float, y: float) -> None:
        if self.interaction.selection != "none":
            self.select_at(x, y)

    def select_at(self, x: float, y: float) -> ChartSelection | None:
        if self.interaction.selection == "none":
            return None

        local_x, local_y = self.to_local(x, y)
        bounds = self.plot_bounds
        if not bounds.contains(local_x, local_y):
            self.clear_selection()
            return None

        primary = self._primary_x_axis()
        selection_x = primary.scale.invert(
            local_x,
            bounds.left,
            bounds.width,
        )
        selected: list[SelectedPoint] = []

        for series in self._series:
            if not series.visible:
                continue

            normalized = series.normalize()
            x_axis = self.get_axis(series.x_axis)
            y_axis = self.get_axis(series.y_axis)
            target = x_axis.scale.to_scalar(
                x_axis.scale.invert(
                    local_x,
                    bounds.left,
                    bounds.width,
                )
            )
            point = nearest_x(normalized.points, target)
            if point is None:
                continue

            pixel_x = x_axis.scale.transform(
                point.x,
                bounds.left,
                bounds.width,
            )
            pixel_y = local_y
            if point.y is not None:
                pixel_y = y_axis.scale.transform(
                    point.y,
                    bounds.bottom,
                    bounds.height,
                )

            selected.append(
                SelectedPoint(
                    series_id=series.id,
                    point=point,
                    pixel=(pixel_x, pixel_y),
                    distance=hypot(
                        pixel_x - local_x,
                        pixel_y - local_y,
                    ),
                )
            )

        if self.interaction.selection == "nearest_point" and selected:
            selected = [min(selected, key=lambda item: item.distance)]

        selection = ChartSelection(
            mode=self.interaction.selection,
            x=selection_x,
            pixel=(local_x, local_y),
            points=tuple(selected),
        )
        self.selection = selection
        self._draw_overlay()
        self.dispatch("on_selection", selection)
        return selection

    def clear_selection(self) -> None:
        if self.selection is None:
            return

        self.selection = None
        self._tooltip.dismiss()
        ChartLayers.clear(self._layers.overlay)
        self.dispatch("on_selection", None)

    def on_touch_down(self, touch: Any) -> bool:
        if super().on_touch_down(touch):
            return True

        return self._interaction_controller.on_touch_down(touch)

    def on_touch_move(self, touch: Any) -> bool | None:
        if touch.grab_current is self:
            return self._interaction_controller.on_touch_move(touch)

        return super().on_touch_move(touch)

    def on_touch_up(self, touch: Any) -> bool | None:
        if touch.grab_current is self:
            return self._interaction_controller.on_touch_up(touch)

        return super().on_touch_up(touch)

    def on_selection(self, selection: ChartSelection | None) -> None:
        pass

    def on_viewport(self, viewport: ChartViewport) -> None:
        pass

    def on_chart_error(self, error: ChartError) -> None:
        pass

    def on_render(self) -> None:
        pass

    def _on_visual_change(self, *_: Any) -> None:
        self.request_render()

    def _on_series_change(self, series: ChartSeries) -> None:
        self._normalized.pop(series.id, None)

        if self.selection is not None:
            self.clear_selection()

        self.request_render()

    def _render(self, _: float) -> None:
        if self._rendering:
            return

        self._rendering = True

        try:
            self._render_chart()
        except ChartError as error:
            self.dispatch("on_chart_error", error)
            raise
        except Exception as error:
            wrapped = ChartRenderError(
                f"Unexpected {type(error).__name__} while rendering chart"
            )
            self.dispatch("on_chart_error", wrapped)
            raise wrapped from error
        finally:
            self._rendering = False

    def _render_chart(self) -> None:
        self._update_plot_bounds()
        self._validate_and_normalize()
        self._resolve_domains()

        background = InstructionGroup()
        grid = InstructionGroup()
        series_group = InstructionGroup()

        self._stage_background(background)
        self._stage_axes(grid)
        self._stage_series(series_group)

        if not self._has_visible_points():
            self._stage_empty(grid)

        ChartLayers.replace(self._layers.background, background)
        ChartLayers.replace(self._layers.grid, grid)
        ChartLayers.replace(self._layers.series, series_group)

        self._layout_overlays()
        self._legend.rebuild()
        self._draw_overlay()
        self.dispatch("on_render")

    def _update_plot_bounds(self) -> None:
        left, top, right, bottom = self.padding
        legend_height = self._legend.height if self.legend_enabled else 0
        plot_left = float(left)
        plot_bottom = float(bottom)
        plot_right = max(plot_left, self.width - float(right))
        plot_top = max(
            plot_bottom,
            self.height - float(top) - legend_height,
        )
        self._plot_bounds = ChartBounds(
            plot_left,
            plot_bottom,
            plot_right,
            plot_top,
        )

    def _validate_and_normalize(self) -> None:
        normalized: dict[str, NormalizedData] = {}

        for series in self._series:
            self.get_axis(series.x_axis)
            self.get_axis(series.y_axis)
            normalized[series.id] = series.normalize()

        self._normalized = normalized

    def _resolve_domains(self) -> None:
        for axis in self._axes.values():
            if axis.side in {"bottom", "top"}:
                values: list[ChartValue] = [
                    point.x
                    for series in self._series
                    if series.visible and series.x_axis == axis.id
                    for point in self._normalized[series.id].points
                ]

                if self.viewport.has_x_range:
                    minimum = self.viewport.x_min
                    maximum = self.viewport.x_max
                    assert minimum is not None and maximum is not None
                else:
                    minimum, maximum = resolve_domain(axis, values)
            else:
                y_values = [
                    point.y
                    for series in self._series
                    if series.visible and series.y_axis == axis.id
                    for point in self._normalized[series.id].points
                    if point.y is not None
                ]
                fixed = self.viewport.y_ranges.get(axis.id)
                if fixed is not None:
                    minimum, maximum = fixed
                else:
                    minimum, maximum = resolve_domain(axis, y_values)

            axis.scale.set_domain(minimum, maximum)

    def _stage_background(self, group: InstructionGroup) -> None:
        group.add(Color(*self.background_color))
        group.add(Rectangle(pos=(0, 0), size=self.size))
        group.add(Color(*self.plot_background_color))
        group.add(
            Rectangle(
                pos=self.plot_bounds.pos,
                size=self.plot_bounds.size,
            )
        )

    def _stage_axes(self, group: InstructionGroup) -> None:
        bounds = self.plot_bounds

        for axis in self._axes.values():
            if not axis.visible:
                continue

            ticks = locate_ticks(axis)
            horizontal = axis.side in {"bottom", "top"}
            last_label_edge = float("-inf")

            for tick in ticks:
                if horizontal:
                    pixel = axis.scale.transform(
                        tick.value,
                        bounds.left,
                        bounds.width,
                    )
                    if axis.grid:
                        group.add(Color(*self.grid_color))
                        group.add(
                            Line(
                                points=(
                                    pixel,
                                    bounds.bottom,
                                    pixel,
                                    bounds.top,
                                ),
                                width=1,
                            )
                        )

                    label_y = (
                        bounds.bottom - 22
                        if axis.side == "bottom"
                        else bounds.top + 5
                    )
                    texture = self._text_texture(tick.label)
                    label_x = pixel - texture.size[0] / 2
                    if label_x >= last_label_edge + 4:
                        self._add_texture(
                            group,
                            texture,
                            label_x,
                            label_y,
                        )
                        last_label_edge = label_x + texture.size[0]
                else:
                    pixel = axis.scale.transform(
                        tick.value,
                        bounds.bottom,
                        bounds.height,
                    )
                    if axis.grid:
                        group.add(Color(*self.grid_color))
                        group.add(
                            Line(
                                points=(
                                    bounds.left,
                                    pixel,
                                    bounds.right,
                                    pixel,
                                ),
                                width=1,
                            )
                        )

                    texture = self._text_texture(tick.label)
                    label_x = (
                        bounds.left - texture.size[0] - 8
                        if axis.side == "left"
                        else bounds.right + 8
                    )
                    self._add_texture(
                        group,
                        texture,
                        label_x,
                        pixel - texture.size[1] / 2,
                    )

            group.add(Color(*self.axis_color))
            group.add(Line(points=self._axis_line(axis), width=1))

    def _stage_series(self, group: InstructionGroup) -> None:
        bounds = self.plot_bounds
        configured_limit = int(self.max_render_points)
        if configured_limit <= 0:
            raise ChartConfigurationError(
                "max_render_points must be greater than zero"
            )

        point_limit = min(
            configured_limit,
            max(int(bounds.width * 2), 100),
        )

        for series in self._series:
            if not series.visible:
                continue

            renderer = self._renderers[series.kind]
            context = RenderContext(
                bounds=bounds,
                x_axis=self.get_axis(series.x_axis),
                y_axis=self.get_axis(series.y_axis),
                quality=self._quality,
                max_points=point_limit,
            )
            renderer.render(
                group,
                series,
                context,
                self.color_for_series(series),
            )

    def _stage_empty(self, group: InstructionGroup) -> None:
        texture = self._text_texture(self.empty_text, font_size=14)
        bounds = self.plot_bounds
        self._add_texture(
            group,
            texture,
            bounds.left + (bounds.width - texture.size[0]) / 2,
            bounds.bottom + (bounds.height - texture.size[1]) / 2,
        )

    def _layout_overlays(self) -> None:
        self._legend.display = self.legend_enabled
        self._legend.pos = (
            self.plot_bounds.left,
            self.height - self.padding[1] - self._legend.height,
        )
        self._tooltip.display = self.tooltip_enabled

        if not self.tooltip_enabled:
            self._tooltip.dismiss()

    def _draw_overlay(self) -> None:
        ChartLayers.clear(self._layers.overlay)
        selection = self.selection

        if selection is None:
            self._tooltip.dismiss()
            return

        bounds = self.plot_bounds
        x, y = selection.pixel
        self._layers.overlay.add(Color(*self.crosshair_color))
        self._layers.overlay.add(
            Line(
                points=(x, bounds.bottom, x, bounds.top),
                width=1,
            )
        )

        for selected in selection.points:
            if selected.point.y is None:
                continue

            marker_x, marker_y = selected.pixel
            if not bounds.contains(marker_x, marker_y):
                continue

            self._layers.overlay.add(Color(*self.selection_color))
            self._layers.overlay.add(
                Ellipse(
                    pos=(marker_x - 4, marker_y - 4),
                    size=(8, 8),
                )
            )

        if self.tooltip_enabled:
            self._tooltip.show(
                self._selection_text(selection),
                anchor=(x, y),
                bounds=bounds,
            )

    def _selection_text(self, selection: ChartSelection) -> str:
        axis = self._primary_x_axis()
        lines = [axis.format(selection.x)]

        for selected in selection.points:
            series = self.get_series(selected.series_id)
            if selected.point.y is None:
                value = "—"
            elif series.value_formatter is None:
                axis = self.get_axis(series.y_axis)
                value = axis.format(selected.point.y)
            else:
                value = series.format_value(selected.point.y)

            lines.append(
                f"{series.label}: {value}"
            )

        return "\n".join(lines)

    def _axis_line(self, axis: ChartAxis) -> tuple[float, ...]:
        bounds = self.plot_bounds

        if axis.side == "bottom":
            return bounds.left, bounds.bottom, bounds.right, bounds.bottom
        if axis.side == "top":
            return bounds.left, bounds.top, bounds.right, bounds.top
        if axis.side == "left":
            return bounds.left, bounds.bottom, bounds.left, bounds.top

        return bounds.right, bounds.bottom, bounds.right, bounds.top

    def _text_texture(
        self,
        text: str,
        *,
        font_size: float = 11,
    ) -> Any:
        label = CoreLabel(
            text=text,
            font_size=font_size,
            color=self.text_color,
        )
        label.refresh()
        return label.texture

    @staticmethod
    def _add_texture(
        group: InstructionGroup,
        texture: Any,
        x: float,
        y: float,
    ) -> None:
        group.add(Color(1, 1, 1, 1))
        group.add(
            Rectangle(
                texture=texture,
                pos=(x, y),
                size=texture.size,
            )
        )

    def _horizontal_axes(self) -> tuple[ChartAxis, ...]:
        return tuple(
            axis
            for axis in self._axes.values()
            if axis.side in {"bottom", "top"}
        )

    def _vertical_axes(self) -> tuple[ChartAxis, ...]:
        return tuple(
            axis
            for axis in self._axes.values()
            if axis.side in {"left", "right"}
        )

    def _primary_x_axis(self) -> ChartAxis:
        axes = self._horizontal_axes()
        if not axes:
            raise ChartAxisError("Chart requires a horizontal axis")

        return axes[0]

    def _has_visible_points(self) -> bool:
        return any(
            series.visible
            and any(
                point.y is not None
                for point in self._normalized[series.id].points
            )
            for series in self._series
        )


def _zoom_domain(
    lower: float,
    upper: float,
    ratio: float,
    factor: float,
) -> tuple[float, float]:
    ratio = max(0.0, min(ratio, 1.0))
    span = upper - lower
    anchor = lower + span * ratio
    new_span = max(span * factor, 1e-12)
    return (
        anchor - new_span * ratio,
        anchor + new_span * (1 - ratio),
    )
