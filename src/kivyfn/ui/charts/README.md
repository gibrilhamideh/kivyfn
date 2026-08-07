# KivyFN Charts

`FnLineChart` is an interactive, theme-aware Cartesian line chart for KivyFN.
Its public API separates source data, series, axes, and interaction state so
applications can start with a tuple list and grow into independently timed
multi-axis datasets without replacing the widget.

## Quick start

```python
from kivyfn.ui.charts import FnLineChart


chart = FnLineChart(
    data=[
        (0, 12),
        (1, 18),
        (2, None),
        (3, 24),
    ],
)
```

`None`, `NaN`, and infinite Y values become visible gaps by default. Invalid X
values are omitted because they have no position on the chart.

## Datetime and multiple series

```python
from kivyfn.ui.charts import (
    DateTimeAxis,
    FnLineChart,
    LinearAxis,
    LineSeries,
)


chart = FnLineChart(
    axes=[
        DateTimeAxis(id="time", side="bottom"),
        LinearAxis(id="temperature", side="left"),
    ],
    series=[
        LineSeries(
            id="inside",
            label="Inside",
            data=inside_readings,
            x="timestamp",
            y="temperature",
            x_axis="time",
            y_axis="temperature",
        ),
        LineSeries(
            id="outside",
            label="Outside",
            data=outside_readings,
            x="timestamp",
            y="temperature",
            x_axis="time",
            y_axis="temperature",
        ),
    ],
)
```

Rows may be tuples, mappings, ordinary objects, dataclasses, or values handled
by callable selectors.

## Updating data

```python
series = chart.get_series("inside")
series.data.append(reading)

with series.data.update():
    series.data.extend(first_batch)
    series.data.extend(second_batch)
```

Tuple-configured series also provide `append(x, y)` and `extend(points)`.

## Error and recovery policies

Each series accepts explicit policies:

```python
LineSeries(
    data=readings,
    invalid="gap",
    duplicates="last",
    ordering="sort",
)
```

Configuration failures always raise a `ChartConfigurationError` subclass.
Data policies control only malformed source rows; they never hide an unknown
axis, duplicate series identifier, or unsupported renderer.

## Interaction

The default chart supports horizontal pan, mouse-wheel and pinch zoom,
double-tap reset, legend visibility toggles, and nearest-X selection.

```python
from kivyfn.ui.charts import ChartInteraction


chart.interaction = ChartInteraction(
    pan="both",
    zoom="both",
    selection="nearest_point",
)
```

Bind `on_selection`, `on_viewport`, `on_chart_error`, or `on_render` to observe
the chart without accessing canvas internals.

## Public API

- `FnChart` owns axes, mixed series, interaction state, and canvas layers.
- `FnLineChart` is the convenient line-only specialization.
- `LineSeries` owns one dataset and its selectors, policies, and line style.
- `ChartDataset` provides observable append, extend, replace, and batching.
- `LinearAxis` and `DateTimeAxis` own domains, ticks, and formatting.
- `ChartViewport` stores explicit pan and zoom ranges.
- `ChartInteraction` configures pan, zoom, pinch, and selection modes.

The chart accepts a second `LinearAxis` on the right for independently scaled
series. Version one intentionally allows a single horizontal axis so panning,
selection, and shared tooltips always have an unambiguous X coordinate.

## Styling

`LineSeries` supports RGBA colors, width, linear or step interpolation,
markers, and dashed lines. A stable built-in palette is used when no color is
provided. `FnChart` colors are Kivy properties and default to the active
KivyFN theme through `chart.kv`.

Use chart methods when changing visibility:

```python
chart.hide_series("outside")
chart.show_series("outside")
chart.toggle_series("outside")
```

After directly changing a series style field, call `series.notify_changed()`
to request a redraw. Axis fields are ordinary configuration values; call
`chart.request_render()` after changing one.

## Rendering and large data

Canvas groups are persistent and separated into background, grid, series, and
overlay layers. Rendering is staged before live instructions are replaced.
Dense line data is reduced with min/max buckets so endpoints and local spikes
survive. `max_render_points` is an upper bound, and the current plot width may
select a smaller bound automatically.

## Constraints

- X values must be finite numbers or datetimes appropriate for their axis.
- Y values are finite numbers; invalid Y values follow the series policy.
- Datetime axes are horizontal and cannot mix naive and timezone-aware data.
- Actual Kivy canvas work stays on the UI thread. Batch dataset changes with
  `dataset.update()` when receiving many samples.
