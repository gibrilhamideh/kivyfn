from __future__ import annotations

from datetime import datetime
from math import fabs
from typing import Any


def format_number(value: Any) -> str:
    """Format numeric ticks without unnecessary trailing zeroes."""
    number = float(value)
    magnitude = fabs(number)

    if magnitude and (magnitude >= 1_000_000 or magnitude < 0.001):
        return f"{number:.2e}"

    if number.is_integer():
        return str(int(number))

    return f"{number:.6f}".rstrip("0").rstrip(".")


def format_datetime(value: Any) -> str:
    """Provide a compact default label for a datetime tick."""
    if not isinstance(value, datetime):
        return str(value)

    if value.second or value.microsecond:
        return value.strftime("%H:%M:%S")

    if value.hour or value.minute:
        return value.strftime("%H:%M")

    return value.strftime("%Y-%m-%d")
