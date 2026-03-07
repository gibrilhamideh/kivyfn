from .datafield import DataField
from ....errors import FieldError

from enum import Enum


class EnumField(DataField):
    def __init__(self, *, enum: type[Enum] | None = None, values=None, **kwargs):
        super().__init__(**kwargs)

        if enum is not None:
            self.values = tuple(enum)
        elif values is not None:
            self.values = tuple(values)
        else:
            raise ValueError("EnumField requires enum or values")

    @property
    def metadata(self) -> dict:
        data = dict(super().metadata)
        data.update({"values": self.values})
        return data

    def parse(self, value):
        value = super().parse(value)

        if value not in self.values:
            raise FieldError(
                field=self.name,
                message="Invalid enum value",
                value=value,
                metadata=self.metadata,
            )

        return value
