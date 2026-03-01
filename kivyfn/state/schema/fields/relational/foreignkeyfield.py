from __future__ import annotations

from ..base import BaseField
from ....constants import Policy


class ForeignKeyField(BaseField):
    def __init__(
        self,
        schema: str,
        *,
        on_delete: Policy = Policy.RESTRICT,
    ):
        super().__init__()
        self.schema = schema
        self.on_delete = on_delete
