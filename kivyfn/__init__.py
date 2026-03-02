from .ui import factory

factory.register()
del factory

from .app import FnApp

__all__ = ["FnApp"]
