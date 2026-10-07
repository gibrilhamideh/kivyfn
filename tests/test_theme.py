"""Verify palette switching, notifications, and interaction state layers."""

import unittest

from kivy.utils import get_hex_from_color

from kivyfn.ui.theme import Theme
from kivyfn.ui.theme.color import ThemeColor
from kivyfn.ui.theme.state import ThemeState


def hex_color(value):
    return get_hex_from_color(value)[:7]


class ThemeTests(unittest.TestCase):
    def test_mode_palettes_preserve_independent_overrides(self):
        colors = ThemeColor(
            dark={"primary": "#112233"}, light={"primary": "#abcdef"}
        )
        self.assertEqual(hex_color(colors.primary), "#112233")
        colors.primary = "#334455"
        colors.mode = "light"
        self.assertEqual(hex_color(colors.primary), "#abcdef")
        colors.mode = "dark"
        self.assertEqual(hex_color(colors.primary), "#334455")
        self.assertEqual(hex_color(ThemeColor().primary), "#d0bcff")

    def test_palette_update_is_atomic_for_role_validation(self):
        colors = ThemeColor()
        before = list(colors.primary)
        with self.assertRaises(ValueError):
            colors.set_palette(
                "dark", {"primary": "#123456", "background": "#000000"}
            )
        self.assertEqual(colors.primary, before)

    def test_palette_application_notifies_once(self):
        colors = ThemeColor()
        changes = []
        colors.bind(on_changed=lambda *_: changes.append(True))
        colors.set_palette(
            "dark", {"primary": "#123456", "onPrimary": "#ffffff"}
        )
        self.assertEqual(len(changes), 1)
        changes.clear()
        colors.mode = "light"
        self.assertEqual(len(changes), 1)
        changes.clear()
        colors.set_palette("dark", {"primary": "#abcdef"})
        self.assertEqual(changes, [])

    def test_theme_rebinds_color_and_detaches_previous_palette(self):
        theme = Theme()
        changes = []
        theme.bind(color=lambda *_: changes.append(True))
        previous = theme.color
        previous.primary = "#123456"
        self.assertEqual(len(changes), 1)
        theme.color = ThemeColor(mode="light")
        changes.clear()
        previous.primary = "#654321"
        self.assertEqual(changes, [])
        theme.color.primary = "#abcdef"
        self.assertEqual(len(changes), 1)

    def test_fill_content_pairs_and_no_legacy_aliases(self):
        colors = ThemeColor()
        self.assertEqual(
            colors.get_derived_role("tertiaryContainer"),
            colors.onTertiaryContainer,
        )
        self.assertEqual(
            colors.get_derived_role("surfaceContainerHigh"), colors.onSurface
        )
        self.assertEqual(
            colors.get_derived_role("inverseSurface"), colors.onInverseSurface
        )
        for role in (
            "background",
            "onBackground",
            "surfaceRaised",
            "surfaceHover",
            "surfaceActive",
            "textSecondary",
            "textMuted",
            "textDisabled",
            "outlineStrong",
            "divider",
            "disabled",
            "focus",
            "selection",
        ):
            self.assertFalse(hasattr(colors, role), role)
            with self.assertRaises(ValueError):
                colors.get_role(role)
        self.assertFalse(hasattr(Theme(), "highlight"))

    def test_selected_and_hovered_coexist_disabled_suppresses_layer(self):
        state = ThemeState()
        color = [0.2, 0.4, 0.6, 1.0]
        layer = state.layer(color, {"selected", "hovered"})
        self.assertEqual(layer[:3], color[:3])
        self.assertEqual(layer[3], state.hoveredOpacity)
        self.assertEqual(
            state.layer(color, {"pressed", "hovered"})[3],
            state.pressedOpacity,
        )
        self.assertEqual(state.layer(color, {"selected"})[3], 0)
        self.assertEqual(
            state.layer(color, {"disabled", "pressed", "hovered"})[3], 0
        )
        self.assertEqual(color, [0.2, 0.4, 0.6, 1.0])


if __name__ == "__main__":
    unittest.main()
