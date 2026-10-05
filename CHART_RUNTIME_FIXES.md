# Chart runtime fixes, inspection, fill and glow

This small overlay applies to the supplied kivyfn archive. Extract it into
the **kivyfn repository root**, separately from the playground overlay.

Actual rendering and interaction tests with Kivy 2.3.1 exposed four defects:

1. `FnChart.on_selection` and `on_viewport` also receive Kivy property
   notifications. These include the widget instance as well as the value;
   the previous single-value handlers crashed during chart construction or
   selection. The no-op handlers now accept both callback forms. Public
   event names and explicitly dispatched event payloads are unchanged.
2. `ChartLayers` removed graphics instructions individually from a snapshot.
   Kivy also removes implicit texture instructions when removing a vertex
   instruction, causing a second removal to fail. Clearing now uses Kivy's
   native `InstructionGroup.clear()`. Replacement attaches the complete staged
   group, preserving internal relationships and keeping one current frame.
3. `ChartTooltip` unpacked label padding as two values although Kivy 2.3
   provides four. Tooltip size now uses the label texture size, which already
   includes padding.
4. Legend hit testing used parent coordinates as offsets inside the legend.
   `to_local(..., relative=True)` now maps clicks to the correct series.

The updated overlay also adds immediate press selection, configurable
snapping and drag inspection, shared value tooltips, and selection retention
across live updates. See `src/kivyfn/ui/charts/README.md` for the public API
and the exact matching/retention behavior. `ChartInteraction` adds `snap`
(default True) and `drag` (default "pan"); existing positional fields keep
their order. `ChartSelection` adds an optional `anchor_series_id` field.

The overlay also adds independent `LineSeries` fill and glow settings.
Fill modes are `none`, `solid` and `gradient`; opacity, numeric/plot-bottom
baseline, glow radius and glow opacity are configurable per series.
Existing series default to no effects. Numeric fill baselines participate
in automatic Y ranges; fixed axis/viewport ranges still win. All fills draw
behind all lines. Complete strokes, halos and areas stay inside the plot.
See the charts README for defaults, mutation and rendering semantics.

The clipping update prevents wide translucent glow strokes from leaking
onto axis labels when overlapping joins cross the plot boundary. Kivy's
nested line stencil alone can admit those pixels. The series layer now
discards fragments outside the local plot bounds before stencil or color
writes, preserving parent transforms and cumulative opacity. The fix adds
no public options or dependencies.

Normalization, data policies and sample-based inspection are preserved.
Pending viewport changes accumulate when several pan/zoom events arrive
before the next rendered frame.

The companion playground includes `tests/charts/smoke_ui.py`, which exercises
construction, repeated frame replacement, selection/clearing/tooltips and
correct legend toggling using these library classes directly, alongside
scenario, streaming and resize tests.
`tests/charts/inspection_ui.py` additionally dispatches real Kivy touch
events to cover the new inspection, snapping and persistence behavior.
`tests/charts/effects_ui.py` checks actual rendered pixels for effects,
clipping, gaps, baseline crossings, layer ordering and live updates.
It also compares every axis-margin pixel before/after wide glow, including
dense zigzags and panned lines crossing the plot edges.
