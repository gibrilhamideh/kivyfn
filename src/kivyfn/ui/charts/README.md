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

Pressing the plot immediately selects a real reading, snaps the guide to
it and shows its value. The default chart retains horizontal drag-to-pan,
mouse-wheel/pinch zoom, double-tap reset and legend visibility toggles.

```python
from kivyfn.ui.charts import ChartInteraction


chart.interaction = ChartInteraction(
    selection="nearest_x", snap=True, drag="inspect", pan="x", zoom="x",
)
```

`drag="inspect"` moves between readings with one finger. Two fingers pan
and pinch according to the existing `pan`, `zoom` and `pinch_zoom` settings.
`drag="pan"` preserves the original one-finger pan behavior. Selection is
still available on press in either mode. `selection="none"` disables
inspection and leaves configured panning available. Changing interaction
settings cancels active gestures and clears the selection.

`selection="nearest_x"` shares a tooltip across visible series. With
`snap=True`, the anchor is the nearest visible valid reading by X; a Y
distance tie-break selects among samples at the same X. Other series show
their nearest reading at the anchor X. Each differing sample time/X is
printed explicitly. A gap is labeled `no data`; outside a series' source X
range the tooltip says `no sample`. No values are interpolated.

`selection="nearest_point"` picks the closest visible valid sample by
screen distance in both X and Y, using each series' axis scale. Selection
uses normalized source samples, independently of rendering decimation.
`snap=False` keeps the guide at the pointer X and labels it `Cursor`; the
tooltip still identifies the real readings and their actual X values.

`chart.selection` includes `anchor_series_id`, the guide X/pixel and selected
points. Sample identity is `(series_id, X)` after normalization/duplicate
resolution. Appending data keeps that anchor. Updating its Y value updates
the displayed value. Rolling it out, removing/hiding its series, or making
its Y invalid clears the selection. Pan, zoom and resize reproject markers;
panning the selected X out of view hides its tooltip until it returns.
`chart.clear_selection()` dismisses it explicitly. Pressing a chart margin
also dismisses it.

Bind `on_selection`, `on_viewport`, `on_chart_error`, or `on_render` to observe
the chart without accessing canvas internals. `on_selection` fires on user
selection, selected-value changes and clearing; a redraw alone does not
emit a new selection event. Datetime inspection includes the full date/time
and any UTC offset. Series `value_formatter` and axis `unit` remain usable.

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

Fill and glow are independent, optional series settings. Existing series
remain plain lines unless an effect is enabled:

```python
series = LineSeries(
    label="Temperature",
    data=readings,
    color=(0.25, 0.70, 1.0, 1.0),
    width=2.0,
    fill="gradient",
    fill_opacity=0.18,
    fill_baseline=0.0,
    glow=True,
    glow_radius=8.0,
    glow_opacity=0.25,
)
```

| Setting | Default | Meaning |
| --- | --- | --- |
| `fill` | `"none"` | `"none"`, `"solid"`, or `"gradient"` |
| `fill_opacity` | `0.18` | Independent area opacity, from 0 to 1 |
| `fill_baseline` | `0.0` | Finite Y value, or `"bottom"` for the plot edge |
| `glow` | `False` | Enable a halo around the crisp line |
| `glow_radius` | `8.0` | Extra halo extent in canvas units; 0 hides it |
| `glow_opacity` | `0.25` | Independent halo strength, from 0 to 1 |

Both effects inherit the series RGB color. The color's alpha controls the
line and markers; fill and glow have their own opacity. `solid` is uniform
shading at the chosen opacity. `gradient` fades from that opacity at the
line to transparent at the baseline, including below a numeric baseline.
The gradient follows the local line height, including step interpolation.

A numeric baseline joins the automatic range of that series' assigned Y
axis when fill is enabled and at least one adjacent valid pair can form an
area. Hidden series, empty data, and isolated single samples do not add a
baseline. Explicit axis limits and viewport ranges take precedence. The
`"bottom"` baseline follows the visible plot edge without expanding the
automatic range. Fill remains visible when the line is above the viewport
and the area between it and the baseline intersects the plot.

Gaps split both line and area. Crossing a numeric baseline splits the area
at the crossing. Every fill renders below every line, and complete strokes,
markers and halos are clipped to the plot. Selection still uses original
normalized samples; effects do not modify data or tooltip values.

Use chart methods when changing visibility:

```python
chart.hide_series("outside")
chart.show_series("outside")
chart.toggle_series("outside")
```

After directly changing a series style field, call `series.notify_changed()`
to validate effect settings and request a redraw. For example:

```python
series.fill = "solid"
series.glow = True
series.notify_changed()
```

Axis fields are ordinary configuration values; call
`chart.request_render()` after changing one.

## Rendering and large data

Canvas groups are persistent and separated into background, grid, series, and
overlay layers. Rendering is staged before live instructions are replaced.
Dense line data is reduced with min/max buckets so endpoints and local spikes
survive. `max_render_points` is an upper bound, and the current plot width may
select a smaller bound automatically.

Fill uses clipped, batched triangle meshes. Glow uses eight translucent
strokes with decreasing opacity toward the outside; it is a bounded halo
approximation rather than a post-processing blur. No new dependency is
required. Effects add rendering work, so profile dense live charts on the
intended device before choosing a large glow radius or many visible series.

Series fragments are clipped in local plot coordinates before stencil or
color writes. This keeps wide, overlapping glow strokes away from axis
labels even when Kivy's nested translucent-line stencil would admit them.
The series context inherits parent projection/modelview matrices and the
active canvas's cumulative opacity, including animated opacity changes.

Kivy's existing `Line` dash controls apply only to its native thin-line
path. Wider strokes, including the halo, use continuous lines. This update
preserves that existing dash behavior.

## Constraints

- X values must be finite numbers or datetimes appropriate for their axis.
- Y values are finite numbers; invalid Y values follow the series policy.
- Datetime axes are horizontal and cannot mix naive and timezone-aware data.
- Actual Kivy canvas work stays on the UI thread. Batch dataset changes with
  `dataset.update()` when receiving many samples.
