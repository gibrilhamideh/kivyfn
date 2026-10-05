from __future__ import annotations

from collections.abc import Callable
from datetime import datetime
from typing import Any, Literal, TypeAlias

ChartValue: TypeAlias = int | float | datetime
ValueSelector: TypeAlias = str | int | Callable[[Any], Any]
ValueFormatter: TypeAlias = Callable[[Any], str]

AxisSide = Literal["bottom", "left", "right", "top"]

InvalidDataPolicy = Literal["raise", "drop", "gap"]

DuplicatePolicy = Literal["raise", "first", "last", "average"]

OrderingPolicy = Literal["require", "sort"]

SelectionMode = Literal["none", "nearest_x", "nearest_point"]

PanMode = Literal["none", "x", "y", "both"]

ZoomMode = PanMode

DragMode = Literal["pan", "inspect"]

LineInterpolation = Literal["linear", "step"]

LineFill = Literal["none", "solid", "gradient"]
FillBaseline: TypeAlias = float | Literal["bottom"]

RenderQuality = Literal["interactive", "final"]
