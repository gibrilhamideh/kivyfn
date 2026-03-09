"""
Register FnKivy widgets to use without import.
"""

from kivy.factory import Factory
from kivy.base import Builder


from ..resources import framework_resource


def register():
    register = Factory.register

    # ---) Context
    register("FnBinder", module="kivyfn.uibase.binder")

    # ---) Primitives
    register("FnWidget", module="kivyfn.uibase.primitives.widget.base")
    register("FnRoot", module="kivyfn.uibase.root")
    register("FnLabel", module="kivyfn.uibase.primitives.label")

    # ---) Navigation
    register("FnScreenManager", module="kivyfn.uibase.navigation")
    register("FnScreen", module="kivyfn.uibase.navigation")
    register("FnSplashScreen", module="kivyfn.uibase.navigation")

    path = framework_resource("kivyfn", "uibase", "behaviors")

    # ---) trssform behaviors
    Builder.load_file(str(path / "transform" / "scale" / "scale.kv"))
    Builder.load_file(str(path / "transform" / "rotate" / "rotate.kv"))
    Builder.load_file(str(path / "transform" / "translate" / "translate.kv"))

    # ---) style behaviors
    Builder.load_file(str(path / "style" / "elevation" / "elevation.kv"))
    Builder.load_file(str(path / "style" / "background" / "background.kv"))
    Builder.load_file(str(path / "style" / "border" / "border.kv"))
