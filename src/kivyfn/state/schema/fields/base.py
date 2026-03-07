from typing import Any


class BaseField:
    def __init__(self) -> None:
        self.name: str
        self.defualt: Any = None
        self.unique: bool = False
        self.index: bool = False

    def __set_name__(self, owner, name):
        self.name = name

    @property
    def metadata(self) -> dict:
        return {}

    def parse(self, value: Any) -> Any:
        return value
