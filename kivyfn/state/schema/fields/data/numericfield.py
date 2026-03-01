from .datafield import DataField
from ....errors import FieldError


class NumericField(DataField):
    """
    Numeric field supporting int/float values.
    """

    def __init__(
        self, *, ge: int | float | None = None, le: int | float | None = None, **kwargs
    ):
        super().__init__(**kwargs)
        self.ge = ge
        self.le = le

    @property
    def metadata(self) -> dict:
        data: dict = super().metadata
        data.update({"ge": self.ge, "le": self.le})
        return data

    # -------------------------------------------------
    # Validation pipeline
    # -------------------------------------------------
    def parse(self, value):
        value = super().parse(value)

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
