from .datafield import DataField
from ....errors import FieldError


class BooleanField(DataField):
    """
    Strict boolean field.
    Accepts bool only.
    Performs no coercion or normalization.
    """

    def parse(self, value):
        value = super().parse(value)

        if not isinstance(value, bool):
            raise FieldError(
                field=self.name,
                message="Expected boolean",
                value=value,
                metadata=self.metadata,
            )

        return value
