from __future__ import annotations
from typing import Any, Callable
from ..base import BaseField
from ....errors import FieldError


class DataField(BaseField):
    """
    Base class for all schema fields.

    Fields are DESCRIPTORS on Schema classes.
    They define structure and validation rules only.
    """

    def __init__(
        self,
        *,
        default=None,
        allow_none=False,
        unique=False,
        index=False,
        normalize_func=None,
    ):
        super().__init__()
        self.default: Any = default
        self.allow_none: bool = allow_none
        self.unique: bool = unique
        self.index: bool = index
        self.normalize_func: Callable | None = normalize_func

    @property
    def metadata(self):
        return {
            "default": self.default,
            "allow_none": self.allow_none,
            "normalize_func": self.normalize_func,
        }

    # -------------------------------------------------
    # Validation pipeline
    # -------------------------------------------------
    def parse(self, value) -> Any:
        """
        Validate and normalize a value.
        Assumes type-level coercion is handled by subclasses.
        """
        if value is None and not self.allow_none:
            raise FieldError(self.name, "value not allowed to be None")

        if callable(self.normalize_func):
            try:
                return self.normalize_func(value)
            except Exception as e:
                raise FieldError(self.name, "normalization failed") from e

        return value
