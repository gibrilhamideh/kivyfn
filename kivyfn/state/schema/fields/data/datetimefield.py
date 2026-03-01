from datetime import datetime
from .datafield import DataField
from ....errors import FieldError


class DatetimeField(DataField):
    """
    Strict datetime field.
    Accepts datetime objects only.
    Performs no normalization or coercion.
    """

    def __init__(
        self,
        *,
        ge: datetime | None = None,
        le: datetime | None = None,
        **kwargs,
    ):
        super().__init__(**kwargs)
        self.ge = ge
        self.le = le

        if ge is not None and not isinstance(ge, datetime):
            raise TypeError("ge must be datetime or None")
        if le is not None and not isinstance(le, datetime):
            raise TypeError("le must be datetime or None")

    @property
    def metadata(self) -> dict:
        data = dict(super().metadata)
        data.update({"ge": self.ge, "le": self.le})
        return data

    def parse(self, value):
        value = super().parse(value)

        if not isinstance(value, datetime):
            raise FieldError(
                field=self.name,
                message="Expected datetime",
                value=value,
                metadata=self.metadata,
            )

        if self.ge is not None and value < self.ge:
            raise FieldError(
                field=self.name,
                message=f"Must be >= {self.ge}",
                value=value,
                metadata=self.metadata,
            )

        if self.le is not None and value > self.le:
            raise FieldError(
                field=self.name,
                message=f"Must be <= {self.le}",
                value=value,
                metadata=self.metadata,
            )

        return value
