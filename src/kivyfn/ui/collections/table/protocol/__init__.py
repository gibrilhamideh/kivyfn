from typing import Protocol, Any


class TableContentProtocol(Protocol):
    def set_table_content(
        self,
        value: Any,
        *,
        row_id: str | None = None,
        row_data: dict | None = None,
    ) -> None: ...
