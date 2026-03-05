from .ui import factory

factory.register()
del factory

from .app import FnApp
from .config import AppConfig

__all__ = ["FnApp", "AppConfig"]
