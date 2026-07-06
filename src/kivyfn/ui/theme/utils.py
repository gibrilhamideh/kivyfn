from __future__ import annotations

from typing import Sequence, TypeAlias
from coloraide import Color

ColorType: TypeAlias = list[float]


def clamp(value: float, minimum: float = 0.0, maximum: float = 1.0) -> float:
    return max(minimum, min(maximum, value))


def normalize_color(color: Sequence[float]) -> ColorType:
    if len(color) == 3:
        return [
            clamp(float(color[0])),
            clamp(float(color[1])),
            clamp(float(color[2])),
            1.0,
        ]

    if len(color) == 4:
        return [
            clamp(float(color[0])),
            clamp(float(color[1])),
            clamp(float(color[2])),
            clamp(float(color[3])),
        ]

    raise ValueError("Color must be RGB or RGBA")


def to_coloraide(color: Sequence[float]) -> Color:
    color = normalize_color(color)
    return Color("srgb", color[:3]).set("alpha", color[3])


def from_coloraide(color: Color) -> ColorType:
    color = color.convert("srgb").fit("srgb")
    r, g, b = color.coords()
    return [
        clamp(float(r)),
        clamp(float(g)),
        clamp(float(b)),
        clamp(float(color.alpha())),
    ]


def alpha(color: Sequence[float], alpha: float) -> ColorType:
    color = normalize_color(color)
    color[3] = clamp(alpha)
    return color


def blend(
    color_a: Sequence[float],
    color_b: Sequence[float],
    amount: float,
    *,
    space: str = "oklch",
) -> ColorType:
    amount = clamp(amount)

    a = to_coloraide(color_a)
    b = to_coloraide(color_b)

    mixed = a.mix(b, amount, space=space)
    return from_coloraide(mixed)


def tone(color: Sequence[float], value: int) -> ColorType:
    """
    Generate a tone using OKLCH lightness.

    value:
        0   = black
        100 = white
    """

    value = max(0, min(100, int(value)))

    original = normalize_color(color)
    c = to_coloraide(original).convert("oklch")

    c["l"] = value / 100

    return alpha(from_coloraide(c), original[3])


def lighten(color: Sequence[float], amount: float) -> ColorType:
    current = to_coloraide(color).convert("oklch")["l"]
    target = clamp(current + clamp(amount))
    return tone(color, round(target * 100))


def darken(color: Sequence[float], amount: float) -> ColorType:
    current = to_coloraide(color).convert("oklch")["l"]
    target = clamp(current - clamp(amount))
    return tone(color, round(target * 100))


def overlay(
    base: Sequence[float],
    overlay_color: Sequence[float],
    *,
    space: str = "srgb",
) -> ColorType:
    """
    Composite overlay_color over base using overlay alpha.
    Useful for hover/focus/pressed state layers.
    """

    base = normalize_color(base)
    overlay_color = normalize_color(overlay_color)

    alpha = overlay_color[3]

    return [
        clamp(base[0] * (1 - alpha) + overlay_color[0] * alpha),
        clamp(base[1] * (1 - alpha) + overlay_color[1] * alpha),
        clamp(base[2] * (1 - alpha) + overlay_color[2] * alpha),
        base[3],
    ]


def palette(
    color: Sequence[float], tones: Sequence[int] | None = None
) -> dict[int, ColorType]:
    if tones is None:
        tones = (0, 5, 10, 20, 30, 40, 50, 60, 70, 80, 90, 95, 100)

    return {value: tone(color, value) for value in tones}
