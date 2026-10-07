# Material theme migration

This update gives KivyFN a reusable Material 3 color-role API. Gabtech's
palette and workspace marker meanings belong in Gabtech Pro. Install both
updates before restarting the application.

## Install

From the KivyFN project root:

```bash
unzip -o ~/Downloads/kivyfn-material-theme.zip -d .
rm -f src/kivyfn/ui/theme/highlight.py
```

The ZIP contains complete changed files, with paths relative to this root.
It is cumulative from the original supplied project and supersedes the
earlier theme and marker ZIPs. The removal command deletes the retired
application-specific highlight module, which ZIP extraction cannot remove.
If KivyFN is installed as a non-editable package, reinstall it from this
updated project using your existing installation workflow.

## Color roles

`ThemeColor` exposes 46 Material color roles plus eight extension roles:

- Primary, secondary, tertiary, and error base/container and content pairs.
- Primary, secondary, and tertiary fixed, fixed-dim, and content roles.
- Surface, dim/bright surfaces, and the five surface container levels.
- Surface content, outlines, inverse colors, shadow, scrim, and surface tint.
- `success`, `onSuccess`, `successContainer`, and `onSuccessContainer`.
- `warning`, `onWarning`, `warningContainer`, and `onWarningContainer`.

Success and warning are KivyFN extensions, not standard Material roles.
The exact role names are in `src/kivyfn/ui/theme/types.py`.

There are no compatibility aliases. Old names such as `background`,
`surfaceRaised`, `textSecondary`, `textMuted`, `divider`, and `disabled`
must be replaced at their call sites. Gabtech Pro's companion update
migrates those call sites.

The framework defaults are independent of Gabtech. Light and dark palettes
are stored independently, and changing `mode` applies the corresponding
palette. Each `ThemeColor` instance owns its palette values.

```python
from kivyfn.ui.theme.color import ThemeColor
from kivyfn.ui.theme.theme import Theme

colors = ThemeColor(
    mode="dark",
    dark={"primary": "#2cd4cc", "onPrimary": "#071113"},
    light={"primary": "#006a65", "onPrimary": "#ffffff"},
)
theme = Theme(color=colors)
colors.set_palette("dark", {"outline": "#596472"})
colors.mode = "light"
```

Palette updates validate role names before applying changes. Direct role
edits persist within the current mode. `on_changed` fires once per batch
or individual edit. `Theme` forwards changes so KV expressions using
`get_role()` and `alpha()` also refresh.

## Interaction states

`theme.state` holds configurable state-layer and disabled opacities:

| Property | Default |
| --- | ---: |
| `hoveredOpacity` | 0.08 |
| `focusedOpacity` | 0.10 |
| `pressedOpacity` | 0.10 |
| `draggedOpacity` | 0.16 |
| `disabledContentOpacity` | 0.38 |
| `disabledContainerOpacity` | 0.12 |

Selection controls a component's base colors. Hover, focus, press, and drag
can layer over those colors. Disabled suppresses interaction layers.
`theme.state.layer(color, states)` returns the chosen layer color without
mutating its input. `theme.highlight` has been removed.

## Verification

The six focused theme tests passed with Python 3.12 and Kivy 2.3.1:

```bash
PYTHONPATH=src python -m unittest discover -s tests -p test_theme.py -v
```

Validation also checked role references, palette changes in rendered KV
controls, and color/content pairs in both schemes. The accompanying Gabtech
Pro migration preserves the existing layout and approved marker appearance.

Role references:

- https://api.flutter.dev/flutter/material/ColorScheme-class.html
- https://github.com/material-components/material-web/blob/main/docs/theming/color.md
