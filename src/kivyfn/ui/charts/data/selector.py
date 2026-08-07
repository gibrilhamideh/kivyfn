from __future__ import annotations

from collections.abc import Mapping, Sequence
from typing import Any

from ..errors import ChartDataError
from ..types import ValueSelector


def select_value(
    row: Any,
    selector: ValueSelector,
) -> Any:
    """Resolve a field, index, or callable selector against one row."""
    if callable(selector):
        return selector(row)

    if isinstance(selector, int):
        if isinstance(row, (str, bytes, bytearray)):
            raise ChartDataError(
                "Integer chart selectors cannot index text values"
            )

        if not isinstance(row, Sequence):
            raise ChartDataError(
                f"Selector {selector} requires a sequence row, got "
                f"{type(row).__name__}"
            )

        try:
            return row[selector]
        except IndexError as error:
            raise ChartDataError(
                f"Selector index {selector} is outside the row"
            ) from error

    if isinstance(row, Mapping):
        try:
            return row[selector]
        except KeyError as error:
            raise ChartDataError(
                f"Chart field {selector!r} is missing from the row"
            ) from error

    try:
        return getattr(row, selector)
    except AttributeError as error:
        raise ChartDataError(
            f"Chart field {selector!r} is missing from "
            f"{type(row).__name__}"
        ) from error
